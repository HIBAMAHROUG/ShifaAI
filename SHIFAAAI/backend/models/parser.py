"""Parses medical text into symptoms, timing, and context signals."""

import re
import json
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import spacy
from collections import Counter

@dataclass
class Symptom:
    text: str
    original_text: str
    type: str
    severity: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[str] = None
    intensity: Optional[float] = None
    confidence: float = 1.0

@dataclass
class TemporalInfo:
    duration_value: Optional[int] = None
    duration_unit: Optional[str] = None
    onset: Optional[str] = None
    frequency: Optional[str] = None

@dataclass
class ParseResult:
    original_text: str
    symptoms: List[Symptom]
    temporal_info: TemporalInfo
    negations: List[str]
    intensifiers: List[str]
    locations: List[str]
    confidence: float

class MedicalTextParser:
    def __init__(self):
        self.symptom_keywords = self._init_symptom_keywords()
        self.location_keywords = self._init_location_keywords()
        self.negation_words = {"pas", "ne", "non", "jamais", "plus", "aucun", "sans", "ni"}
        self.intensifiers = {
            "très": 1.5, "beaucoup": 1.3, "extrêmement": 2.0, "trop": 1.5,
            "fortement": 1.4, "légèrement": 0.7, "un peu": 0.5, "peu": 0.6,
            "assez": 1.2, "plutôt": 1.1, "vraiment": 1.3, "absolument": 1.5
        }
        self.duration_patterns = [
            (r'(\d+)\s*(?:jours?|journées?)', 'jours', 1),
            (r'(\d+)\s*(?:heures?|h)', 'heures', 1),
            (r'(\d+)\s*(?:semaines?)', 'semaines', 1),
            (r'(\d+)\s*(?:mois)', 'mois', 1),
            (r'(\d+)\s*(?:ans?)', 'ans', 1),
            (r'(depuis|il y a)\s*(\d+)\s*(?:jours?|heures?)', 'duration', 2),
            (r'(\d+)\s*(?:à|a)\s*(\d+)', 'range', None)
        ]
        
        self.severity_patterns = {
            'critique': ['sévère', 'très fort', 'extrême', 'insupportable', 'intolérable'],
            'élevé': ['fort', 'intense', 'important', 'aigu', 'violent'],
            'modéré': ['moyen', 'modéré', 'supportable', 'gérable'],
            'faible': ['léger', 'faible', 'mineur', 'petit']
        }
        
        self.location_patterns = [
            (r'(?:(?:au|x|à|dans le|dans la)\s+)?(?:niveau\s+de\s+la\s+)?(?\w+(?:\s+\w+)?)', 'location')
        ]
        self.nlp = None
        try:
            self.nlp = spacy.load("fr_core_news_sm")
        except OSError:
            pass
    
    def _init_symptom_keywords(self) -> Dict[str, str]:
        return {
            "fièvre": "temperature", "fievre": "temperature", "frissons": "temperature",
            "sueurs": "temperature", "hyperthermie": "temperature",
            "toux": "respiratory", "tousser": "respiratory", "expectoration": "respiratory",
            "essoufflement": "respiratory", "difficulté respirer": "respiratory",
            "respiration sifflante": "respiratory", "dyspnée": "respiratory",
            "respiration difficile": "respiratory", "oppression thoracique": "respiratory",
            "gorge": "ent", "mal gorge": "ent", "douleur gorge": "ent", "angine": "ent",
            "nez": "ent", "nez bouché": "ent", "écoulement nasal": "ent", 
            "éternuement": "ent", "éternuer": "ent", "oreille": "ent", "douleur oreille": "ent",
            "otalgie": "ent", "acouphènes": "ent", "bourdonnement": "ent",
            "maux de tête": "neuro", "céphalée": "neuro", "migraine": "neuro",
            "vertige": "neuro", "étourdissement": "neuro", "tête qui tourne": "neuro",
            "perte connaissance": "neuro", "confusion": "neuro", "tremblement": "neuro",
            "nausée": "digest", "nausées": "digest", "vomissement": "digest", "vomir": "digest",
            "diarrhée": "digest", "diarrhées": "digest", "constipation": "digest",
            "douleur ventre": "digest", "douleur abdominale": "digest", "ballonnement": "digest",
            "douleur": "musculo", "courbatures": "musculo", "douleur musculaire": "musculo",
            "arthralgie": "musculo", "douleur articulaire": "musculo", "raideur": "musculo",
            "fatigue": "general", "épuisement": "general", "asthénie": "general",
            "perte poids": "general", "anorexie": "general", "fièvre": "general",
            "éruption": "derma", "éruption cutanée": "derma", "rougeur": "derma",
            "démangeaison": "derma", "prurit": "derma", "bouton": "derma", "urticaire": "derma"
        }
    
    def _init_location_keywords(self) -> Dict[str, List[str]]:
        return {
            "tête": ["tête", "crâne", "front", "nuque", "occiput"],
            "thorax": ["poitrine", "thorax", "cage thoracique", "sternum"],
            "abdomen": ["ventre", "abdomen", "estomac", "bas ventre", "flanc"],
            "membres": ["bras", "jambe", "main", "pied", "épaule", "genou", "coude", "poignet", "cheville"],
            "dos": ["dos", "lombaires", "colonne", "rachis"]
        }
    
    def parse(self, text: str) -> ParseResult:
        original_text = text
        text_lower = text.lower()
        symptoms = self._extract_symptoms(text_lower)
        temporal_info = self._extract_temporal_info(text_lower)
        negations = self._extract_negations(text_lower)
        intensifiers = self._extract_intensifiers(text_lower)
        locations = self._extract_locations(text_lower)
        confidence = self._calculate_confidence(symptoms, len(original_text.split()))
        
        return ParseResult(
            original_text=original_text,
            symptoms=symptoms,
            temporal_info=temporal_info,
            negations=negations,
            intensifiers=intensifiers,
            locations=locations,
            confidence=confidence
        )
    
    def _extract_symptoms(self, text: str) -> List[Symptom]:
        symptoms = []
        text_tokens = text.split()
        
        for i, token in enumerate(text_tokens):
            if token in self.symptom_keywords:
                symptom_type = self.symptom_keywords[token]
                severity = self._detect_severity(text, token)
                location = self._detect_location(text, i)
                intensity = self._get_intensity(text, i)
                is_negated = any(neg in text[max(0, i-3):i] for neg in self.negation_words)
                if not is_negated:
                    symptoms.append(Symptom(
                        text=token,
                        original_text=token,
                        type=symptom_type,
                        severity=severity,
                        location=location,
                        duration=None,
                        intensity=intensity,
                        confidence=0.9 if intensity else 0.8
                    ))
        
        # Utiliser spaCy si disponible pour une meilleure extraction
        if self.nlp:
            symptoms.extend(self._extract_symptoms_spacy(text, symptoms))
        
        # Éliminer les doublons (garder le plus précis)
        unique_symptoms = {}
        for s in symptoms:
            key = s.text
            if key not in unique_symptoms or s.intensity > unique_symptoms[key].intensity:
                unique_symptoms[key] = s
        
        return list(unique_symptoms.values())
    
    def _extract_symptoms_spacy(self, text: str, existing_symptoms: List[Symptom]) -> List[Symptom]:
        symptoms = []
        doc = self.nlp(text)
        
        existing_texts = [s.text for s in existing_symptoms]
        
        for ent in doc.ents:
            if ent.label_ in ["SYMPTOM", "DISEASE"]:
                if ent.text.lower() not in existing_texts:
                    is_negated = any(neg in doc.text[max(0, ent.start-5):ent.end].lower() 
                                    for neg in self.negation_words)
                    
                    if not is_negated:
                        symptoms.append(Symptom(
                            text=ent.text,
                            original_text=ent.text,
                            type="symptom",
                            confidence=0.85
                        ))
        
        return symptoms
    
    def _extract_temporal_info(self, text: str) -> TemporalInfo:
        temporal = TemporalInfo()
        
        for pattern, unit, group in self.duration_patterns:
            match = re.search(pattern, text)
            if match:
                if unit == 'duration':
                    value = int(match.group(2))
                    temporal.duration_value = value
                    temporal.duration_unit = match.group(1)
                elif unit != 'range':
                    value = int(match.group(1))
                    temporal.duration_value = value
                    temporal.duration_unit = unit
                
                # Détecter le début
                if any(word in text for word in ['depuis', 'il y a', 'pendant']):
                    if 'depuis' in text:
                        temporal.onset = 'depuis'
                    elif 'il y a' in text:
                        temporal.onset = 'il y a'
                
                break
        
        # Détecter la fréquence
        frequency_patterns = {
            'quotidien': ['chaque jour', 'tous les jours', 'quotidiennement'],
            'hebdomadaire': ['chaque semaine', 'toutes les semaines'],
            'mensuel': ['chaque mois', 'tous les mois'],
            'occasionnel': ['parfois', 'occasionnellement', 'de temps en temps']
        }
        
        for freq, patterns in frequency_patterns.items():
            if any(p in text for p in patterns):
                temporal.frequency = freq
                break
        
        return temporal
    
    def _extract_negations(self, text: str) -> List[str]:
        """Extraire les mots de négation"""
        negations = []
        words = text.split()
        
        for i, word in enumerate(words):
            if word in self.negation_words:
                # Capturer le contexte (jusqu'à 3 mots après)
                context = words[i+1:i+4]
                negations.append(f"{word} {' '.join(context)}" if context else word)
        
        return negations
    
    def _extract_intensifiers(self, text: str) -> List[str]:
        """Extraire les intensificateurs"""
        return [word for word in text.split() if word in self.intensifiers]
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extraire les localisations"""
        locations = []
        
        for region, keywords in self.location_keywords.items():
            for kw in keywords:
                if kw in text:
                    locations.append(f"{region} ({kw})")
        
        # Patterns de localisation plus complexes
        location_patterns = [
            r'(?:dans le|dans la|au|x|à)\s+(\w+)',
            r'localis[ée]?\s+(?:au|x|à)\s+(\w+)',
            r'niveau\s+(\w+)'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in locations:
                    locations.append(match)
        
        return list(set(locations))
    
    def _detect_severity(self, text: str, symptom: str) -> Optional[str]:
        """Détecter la sévérité d'un symptôme"""
        # Chercher autour du symptôme
        symptom_pos = text.find(symptom)
        context_start = max(0, symptom_pos - 30)
        context_end = min(len(text), symptom_pos + 30)
        context = text[context_start:context_end]
        
        for level, keywords in self.severity_patterns.items():
            for kw in keywords:
                if kw in context:
                    return level
        
        return None
    
    def _detect_location(self, text: str, token_idx: int) -> Optional[str]:
        """Détecter la localisation autour d'un token"""
        tokens = text.split()
        start = max(0, token_idx - 5)
        end = min(len(tokens), token_idx + 5)
        context = ' '.join(tokens[start:end])
        
        for region, keywords in self.location_keywords.items():
            for kw in keywords:
                if kw in context:
                    return region
        
        return None
    
    def _get_intensity(self, text: str, token_idx: int) -> Optional[float]:
        """Obtenir le facteur d'intensité"""
        tokens = text.split()
        start = max(0, token_idx - 3)
        context = ' '.join(tokens[start:token_idx])
        
        for intensifier, factor in self.intensifiers.items():
            if intensifier in context:
                return factor
        
        return 1.0
    
    def _calculate_confidence(self, symptoms: List[Symptom], total_words: int) -> float:
        """Calculer le score de confiance du parsing"""
        if not symptoms:
            return 0.3
        
        # Facteurs de confiance
        num_symptoms = len(symptoms)
        has_intensities = any(s.intensity for s in symptoms)
        has_locations = any(s.location for s in symptoms)
        
        score = min(0.5 + (num_symptoms * 0.05), 1.0)
        
        if has_intensities:
            score = min(score + 0.1, 1.0)
        if has_locations:
            score = min(score + 0.1, 1.0)
        
        return round(score, 2)

# =========================================================
# EXTENSION AVEC REGEX AVANCÉ
# =========================================================

class AdvancedMedicalParser(MedicalTextParser):
    """Parseur médical avancé avec patterns complexes"""
    
    def __init__(self):
        super().__init__()
        self._init_advanced_patterns()
    
    def _init_advanced_patterns(self):
        """Initialiser les patterns avancés"""
        
        # Patterns pour phrases complètes
        self.patterns = {
            'symptom_with_location': re.compile(
                r'(douleur|mal|gêne)\s+(?:au|x|à|dans le|dans la)\s+(\w+(?:\s+\w+)?)',
                re.IGNORECASE
            ),
            'symptom_with_intensity': re.compile(
                r'(très|peu|assez|extrêmement)\s+(?:fort|intense)\s+(?:douleur|mal)',
                re.IGNORECASE
            ),
            'duration_period': re.compile(
                r'(depuis|pendant)\s+(\d+)\s*(?:jours?|heures?|semaines?|mois?)',
                re.IGNORECASE
            ),
            'body_part_location': re.compile(
                r'(?:au|x|à|niveau\s+du|niveau\s+de\s+la)\s+(\w+(?:\s+\w+)?)',
                re.IGNORECASE
            )
        }
    
    def parse_advanced(self, text: str) -> Dict[str, Any]:
        """Parse avancé avec extraction de structures complexes"""
        
        result = self.parse(text)
        
        # Extraire les patterns avancés
        advanced_data = {
            "symptom_location_pairs": [],
            "intensity_phrases": [],
            "duration_info": {},
            "body_parts": []
        }
        
        # Symptômes avec localisation
        for match in self.patterns['symptom_with_location'].finditer(text):
            advanced_data["symptom_location_pairs"].append({
                "symptom": match.group(1),
                "location": match.group(2)
            })
        
        # Durée
        for match in self.patterns['duration_period'].finditer(text):
            advanced_data["duration_info"] = {
                "type": match.group(1),
                "value": int(match.group(2)),
                "unit": self._extract_unit(match.group(0))
            }
        
        # Parties du corps
        for match in self.patterns['body_part_location'].finditer(text):
            advanced_data["body_parts"].append(match.group(1))
        
        return {
            "basic": asdict(result),
            "advanced": advanced_data
        }
    
    def _extract_unit(self, text: str) -> str:
        """Extraire l'unité de temps du texte"""
        if 'jour' in text: return 'jours'
        if 'heure' in text: return 'heures'
        if 'semaine' in text: return 'semaines'
        if 'mois' in text: return 'mois'
        return 'unknown'

# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================

def parse_symptoms(text: str, advanced: bool = False) -> Dict[str, Any]:
    """
    Fonction principale de parsing des symptômes
    
    Args:
        text: Texte à analyser
        advanced: Utiliser le parsing avancé
    
    Returns:
        Dictionnaire avec les résultats du parsing
    """
    if advanced:
        parser = AdvancedMedicalParser()
        result = parser.parse_advanced(text)
    else:
        parser = MedicalTextParser()
        result = asdict(parser.parse(text))
    
    return result

def format_parse_result(result: Dict[str, Any]) -> str:
    """Formater le résultat du parsing pour affichage"""
    output = []
    
    output.append("="*50)
    output.append("📊 RÉSULTAT DU PARSING MÉDICAL")
    output.append("="*50)
    
    output.append(f"\n🔍 Texte original: {result['original_text']}")
    output.append(f"📈 Confiance: {result['confidence']*100:.0f}%")
    
    if result['symptoms']:
        output.append(f"\n🏥 Symptômes détectés ({len(result['symptoms'])}):")
        for s in result['symptoms']:
            symptom_text = f"   - {s['text']}"
            if s.get('severity'):
                symptom_text += f" (sévérité: {s['severity']})"
            if s.get('location'):
                symptom_text += f" [localisation: {s['location']}]"
            if s.get('intensity'):
                symptom_text += f" intensité: {s['intensity']}x"
            output.append(symptom_text)
    
    if result['temporal_info'].get('duration_value'):
        t = result['temporal_info']
        output.append(f"\n⏱️ Information temporelle: {t['duration_value']} {t.get('duration_unit', '')}")
        if t.get('onset'):
            output.append(f"   Début: {t['onset']}")
    
    if result['negations']:
        output.append(f"\n🚫 Négations détectées: {', '.join(result['negations'])}")
    
    if result['locations']:
        output.append(f"\n📍 Localisations: {', '.join(result['locations'])}")
    
    return '\n'.join(output)

# =========================================================
# TESTS ET EXEMPLES
# =========================================================

def test_parser():
    """Tester le parseur avec des exemples"""
    
    test_cases = [
        "J'ai une forte fièvre depuis 3 jours et une toux sèche",
        "Je ressens une douleur intense au niveau du ventre",
        "Mal de tête modéré depuis hier",
        "Je n'ai pas de fièvre mais j'ai des nausées et des vomissements",
        "Douleur thoracique avec essoufflement",
        "Vertiges et perte d'équilibre depuis ce matin",
        "Courbatures dans tout le corps et fatigue extrême"
    ]
    
    parser = MedicalTextParser()
    
    print("\n" + "="*60)
    print("🧪 TESTS DU PARSEUR MÉDICAL")
    print("="*60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {text}")
        print("-"*40)
        
        result = parser.parse(text)
        print(format_parse_result(asdict(result)))

def test_advanced_parser():
    """Tester le parseur avancé"""
    
    text = "J'ai une douleur à la poitrine depuis 3 jours, c'est assez intense"
    
    parser = AdvancedMedicalParser()
    result = parser.parse_advanced(text)
    
    print("\n" + "="*60)
    print("🔬 TEST PARSER AVANCÉ")
    print("="*60)
    print(f"\n📝 Texte: {text}")
    print(f"\n📊 Résultat avancé:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    test_parser()
    test_advanced_parser()
    
    # Exemple d'utilisation avec l'API Flask
    print("\n" + "="*60)
    print("💡 UTILISATION AVEC L'API")
    print("="*60)
    print("""
    from parser_model import parse_symptoms
    
    @app.route('/api/parse', methods=['POST'])
    def parse():
        text = request.json.get('text', '')
        result = parse_symptoms(text, advanced=True)
        return jsonify(result)
    """)
