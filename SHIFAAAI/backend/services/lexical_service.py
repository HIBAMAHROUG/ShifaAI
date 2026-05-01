# lexical_service.py - Service d'analyse lexicale pour SHIFAAAI

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
from datetime import datetime
import unicodedata

# =========================================================
# CLASSES DE DONNÉES
# =========================================================

@dataclass
class Token:
    """Structure d'un token lexical"""
    text: str
    original_text: str
    type: str  # SYMPTOME, TERME_MEDICAL, MOT, NOMBRE, TEMPS, NEGATION, INTENSIFICATEUR, PONCTUATION
    category: Optional[str] = None
    weight: float = 1.0
    position: int = 0
    start_char: int = 0
    end_char: int = 0
    is_medical: bool = False
    confidence: float = 1.0

@dataclass
class LexicalAnalysis:
    """Résultat complet de l'analyse lexicale"""
    original_text: str
    tokens: List[Token]
    medical_terms: List[str]
    symptoms: List[str]
    negations: List[str]
    intensifiers: List[str]
    numbers: List[str]
    time_expressions: List[str]
    word_frequency: Dict[str, int]
    statistics: Dict[str, Any]
    processing_time_ms: float

# =========================================================
# SERVICE D'ANALYSE LEXICALE
# =========================================================

class LexicalService:
    """Service d'analyse lexicale pour texte médical"""
    
    def __init__(self):
        self._init_dictionaries()
        self._init_patterns()
    
    def _init_dictionaries(self):
        """Initialiser les dictionnaires médicaux"""
        
        # Symptômes par catégorie
        self.symptoms_dict = {
            # Température
            "fièvre": {"category": "température", "weight": 3},
            "fievre": {"category": "température", "weight": 3},
            "frissons": {"category": "température", "weight": 2},
            "sueurs": {"category": "température", "weight": 2},
            
            # Respiratoire
            "toux": {"category": "respiratoire", "weight": 3},
            "tousser": {"category": "respiratoire", "weight": 3},
            "essoufflement": {"category": "respiratoire", "weight": 4},
            "respiration difficile": {"category": "respiratoire", "weight": 4},
            "expectoration": {"category": "respiratoire", "weight": 2},
            
            # ORL
            "gorge": {"category": "orl", "weight": 2},
            "mal de gorge": {"category": "orl", "weight": 2},
            "nez": {"category": "orl", "weight": 2},
            "nez congestionné": {"category": "orl", "weight": 2},
            "éternuement": {"category": "orl", "weight": 2},
            "oreille": {"category": "orl", "weight": 2},
            "douleur oreille": {"category": "orl", "weight": 2},
            
            # Neurologique
            "maux de tête": {"category": "neurologique", "weight": 2},
            "migraine": {"category": "neurologique", "weight": 3},
            "vertige": {"category": "neurologique", "weight": 2},
            "étourdissement": {"category": "neurologique", "weight": 2},
            "confusion": {"category": "neurologique", "weight": 4},
            
            # Digestif
            "nausée": {"category": "digestif", "weight": 2},
            "nausées": {"category": "digestif", "weight": 2},
            "vomissement": {"category": "digestif", "weight": 3},
            "diarrhée": {"category": "digestif", "weight": 3},
            "douleur ventre": {"category": "digestif", "weight": 2},
            
            # Musculo-squelettique
            "douleur": {"category": "douleur", "weight": 2},
            "courbatures": {"category": "musculaire", "weight": 2},
            "douleur articulaire": {"category": "articulaire", "weight": 2},
            "raideur": {"category": "musculaire", "weight": 2},
            
            # Général
            "fatigue": {"category": "général", "weight": 2},
            "épuisement": {"category": "général", "weight": 3},
            "perte poids": {"category": "général", "weight": 2},
            "anorexie": {"category": "général", "weight": 2}
        }
        
        # Termes médicaux généraux
        self.medical_terms = {
            "examen": "medical_term",
            "analyse": "medical_term",
            "traitement": "medical_term",
            "médicament": "medical_term",
            "vaccination": "medical_term",
            "hospitalisation": "medical_term",
            "consultation": "medical_term",
            "diagnostic": "medical_term",
            "prescription": "medical_term",
            "ordonnance": "medical_term"
        }
        
        # Négations
        self.negations = {
            "pas", "ne", "non", "jamais", "plus", "aucun", "aucune", 
            "sans", "ni", "personne", "rien", "aucunement"
        }
        
        # Intensificateurs
        self.intensifiers = {
            "très": 1.5, "beaucoup": 1.3, "extrêmement": 2.0, "trop": 1.5,
            "fort": 1.4, "intense": 1.4, "léger": 0.7, "légèrement": 0.7,
            "assez": 1.2, "peu": 0.6, "vraiment": 1.3, "absolument": 1.5,
            "modérément": 1.0, "faiblement": 0.5, "très peu": 0.4
        }
        
        # Expressions temporelles
        self.time_expressions = {
            "aujourd'hui", "hier", "avant-hier", "cette semaine", "ce mois",
            "depuis", "pendant", "il y a", "voici", "voilà"
        }
        
        # Unités de temps
        self.time_units = {
            "jour": "jours", "jours": "jours", "semaine": "semaines", 
            "semaines": "semaines", "mois": "mois", "année": "années",
            "heure": "heures", "heures": "heures", "minute": "minutes"
        }
    
    def _init_patterns(self):
        """Initialiser les patterns regex"""
        self.patterns = {
            'number': re.compile(r'\b\d+(?:[.,]\d+)?\b'),
            'date': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            'time': re.compile(r'\b\d{1,2}:\d{2}\b'),
            'duration': re.compile(r'(\d+)\s*(?:jours?|heures?|semaines?|mois|années?)'),
            'email': re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b'),
            'url': re.compile(r'https?://[^\s]+')
        }
    
    def analyze(self, text: str) -> LexicalAnalysis:
        """
        Effectuer une analyse lexicale complète du texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            LexicalAnalysis contenant tous les résultats
        """
        import time
        start_time = time.time()
        
        original_text = text
        
        # Prétraitement
        text_cleaned = self._preprocess(text)
        text_lower = text_cleaned.lower()
        
        # Tokenisation
        tokens = self._tokenize(text_cleaned, text_lower)
        
        # Extraction des éléments
        medical_terms = []
        symptoms = []
        negations = []
        intensifiers = []
        numbers = []
        time_expressions = []
        
        for token in tokens:
            if token.type == 'SYMPTOME':
                symptoms.append(token.text)
                medical_terms.append(token.text)
            elif token.type == 'TERME_MEDICAL':
                medical_terms.append(token.text)
            elif token.type == 'NEGATION':
                negations.append(token.text)
            elif token.type == 'INTENSIFICATEUR':
                intensifiers.append(token.text)
            elif token.type == 'NOMBRE':
                numbers.append(token.text)
            elif token.type == 'TEMPS':
                time_expressions.append(token.text)
        
        # Fréquence des mots
        all_words = [t.text for t in tokens if t.type not in ['PONCTUATION']]
        word_frequency = dict(Counter(all_words).most_common(15))
        
        # Statistiques
        statistics = self._calculate_statistics(tokens, symptoms, medical_terms)
        
        processing_time = (time.time() - start_time) * 1000
        
        return LexicalAnalysis(
            original_text=original_text,
            tokens=tokens,
            medical_terms=list(set(medical_terms)),
            symptoms=list(set(symptoms)),
            negations=list(set(negations)),
            intensifiers=list(set(intensifiers)),
            numbers=list(set(numbers)),
            time_expressions=list(set(time_expressions)),
            word_frequency=word_frequency,
            statistics=statistics,
            processing_time_ms=round(processing_time, 2)
        )
    
    def _preprocess(self, text: str) -> str:
        """Prétraiter le texte"""
        # Normaliser Unicode
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ASCII', 'ignore').decode('utf-8')
        
        # Remplacer les apostrophes
        text = text.replace("'", "'")
        
        # Supprimer les caractères spéciaux (garder lettres, chiffres, espaces, ponctuation basique)
        text = re.sub(r'[^\w\s\'-]', ' ', text)
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize(self, text: str, text_lower: str) -> List[Token]:
        """Tokeniser le texte"""
        tokens = []
        words = text.split()
        current_pos = 0
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            start_char = text.find(word, current_pos)
            end_char = start_char + len(word)
            current_pos = end_char
            
            # Déterminer le type du token
            token_type = 'MOT'
            category = None
            weight = 1.0
            is_medical = False
            
            # Vérifier les patterns spéciaux d'abord
            if self.patterns['number'].match(word):
                token_type = 'NOMBRE'
                category = 'numérique'
            
            # Vérifier les symptômes
            elif word_lower in self.symptoms_dict:
                token_type = 'SYMPTOME'
                category = self.symptoms_dict[word_lower]['category']
                weight = self.symptoms_dict[word_lower]['weight']
                is_medical = True
            
            # Vérifier les termes médicaux
            elif word_lower in self.medical_terms:
                token_type = 'TERME_MEDICAL'
                category = 'medical'
                is_medical = True
            
            # Vérifier les négations
            elif word_lower in self.negations:
                token_type = 'NEGATION'
                category = 'logique'
                weight = -1.0
            
            # Vérifier les intensificateurs
            elif word_lower in self.intensifiers:
                token_type = 'INTENSIFICATEUR'
                category = 'intensité'
                weight = self.intensifiers[word_lower]
            
            # Vérifier les expressions temporelles
            elif word_lower in self.time_expressions:
                token_type = 'TEMPS'
                category = 'temporel'
            
            # Vérifier les unités de temps
            elif word_lower in self.time_units:
                token_type = 'TEMPS'
                category = 'temporel'
            
            # Ponctuation (si nécessaire)
            elif len(word) == 1 and word in '.,;:!?()[]{}':
                token_type = 'PONCTUATION'
            
            # Créer le token
            token = Token(
                text=word,
                original_text=word,
                type=token_type,
                category=category,
                weight=weight,
                position=i,
                start_char=start_char,
                end_char=end_char,
                is_medical=is_medical,
                confidence=0.95 if is_medical else 0.85
            )
            tokens.append(token)
        
        # Post-traitement: détection des bigrammes médicaux
        tokens = self._detect_medical_bigrams(tokens)
        
        return tokens
    
    def _detect_medical_bigrams(self, tokens: List[Token]) -> List[Token]:
        """Détecter les bigrammes médicaux (ex: 'mal de gorge')"""
        i = 0
        while i < len(tokens) - 1:
            # Vérifier les bigrammes courants
            bigram = f"{tokens[i].text} {tokens[i+1].text}".lower()
            
            if bigram in self.symptoms_dict:
                # Fusionner les deux tokens
                merged_token = Token(
                    text=bigram,
                    original_text=bigram,
                    type='SYMPTOME',
                    category=self.symptoms_dict[bigram]['category'],
                    weight=self.symptoms_dict[bigram]['weight'],
                    position=tokens[i].position,
                    start_char=tokens[i].start_char,
                    end_char=tokens[i+1].end_char,
                    is_medical=True,
                    confidence=0.95
                )
                tokens[i] = merged_token
                del tokens[i+1]
            i += 1
        
        return tokens
    
    def _calculate_statistics(self, tokens: List[Token], symptoms: List[str], 
                             medical_terms: List[str]) -> Dict[str, Any]:
        """Calculer les statistiques de l'analyse"""
        
        # Compter par type
        type_counts = Counter([t.type for t in tokens])
        
        # Compter par catégorie de symptômes
        symptom_categories = Counter()
        for token in tokens:
            if token.type == 'SYMPTOME' and token.category:
                symptom_categories[token.category] += 1
        
        # Score de confiance lexicale
        confidence_score = min(0.5 + (len(symptoms) * 0.1) + (len(medical_terms) * 0.05), 1.0)
        
        return {
            "total_tokens": len(tokens),
            "unique_tokens": len(set([t.text for t in tokens])),
            "type_distribution": dict(type_counts),
            "symptom_categories": dict(symptom_categories),
            "num_symptoms": len(symptoms),
            "num_medical_terms": len(medical_terms),
            "num_negations": sum(1 for t in tokens if t.type == 'NEGATION'),
            "num_intensifiers": sum(1 for t in tokens if t.type == 'INTENSIFICATEUR'),
            "confidence_score": round(confidence_score, 2),
            "text_complexity": self._calculate_complexity(tokens)
        }
    
    def _calculate_complexity(self, tokens: List[Token]) -> str:
        """Calculer la complexité du texte"""
        medical_ratio = sum(1 for t in tokens if t.is_medical) / max(len(tokens), 1)
        
        if medical_ratio > 0.3:
            return "élevée"
        elif medical_ratio > 0.1:
            return "moyenne"
        else:
            return "faible"
    
    def extract_key_phrases(self, analysis: LexicalAnalysis, top_n: int = 5) -> List[str]:
        """Extraire les phrases clés de l'analyse"""
        # Combiner les symptômes et termes médicaux
        key_terms = analysis.symptoms + analysis.medical_terms
        
        # Ajouter les intensificateurs avec leurs symptômes associés
        enhanced_terms = []
        for term in key_terms:
            # Chercher des intensificateurs à proximité
            for token in analysis.tokens:
                if token.text == term and token.position > 0:
                    prev_token = analysis.tokens[token.position - 1]
                    if prev_token.type == 'INTENSIFICATEUR':
                        enhanced_terms.append(f"{prev_token.text} {term}")
                        break
            
            if term not in [t.split()[-1] for t in enhanced_terms]:
                enhanced_terms.append(term)
        
        # Retourner les termes uniques les plus importants
        unique_terms = []
        for term in enhanced_terms:
            if term not in unique_terms:
                unique_terms.append(term)
        
        return unique_terms[:top_n]
    
    def format_output(self, analysis: LexicalAnalysis, format_type: str = 'json') -> str:
        """
        Formater la sortie de l'analyse
        
        Args:
            analysis: Résultat de l'analyse
            format_type: 'json', 'text', ou 'table'
        """
        if format_type == 'json':
            return json.dumps(asdict(analysis), ensure_ascii=False, indent=2)
        
        elif format_type == 'text':
            output = []
            output.append("="*60)
            output.append("📊 ANALYSE LEXICALE SHIFAAAI")
            output.append("="*60)
            output.append(f"\n📝 Texte original: {analysis.original_text[:200]}")
            output.append(f"\n🏥 Statistiques:")
            output.append(f"   - Tokens: {analysis.statistics['total_tokens']}")
            output.append(f"   - Symptômes: {len(analysis.symptoms)}")
            output.append(f"   - Termes médicaux: {len(analysis.medical_terms)}")
            output.append(f"   - Négations: {len(analysis.negations)}")
            output.append(f"   - Intensificateurs: {len(analysis.intensifiers)}")
            
            if analysis.symptoms:
                output.append(f"\n🩺 Symptômes détectés:")
                for s in analysis.symptoms[:10]:
                    output.append(f"   - {s}")
            
            if analysis.negations:
                output.append(f"\n🚫 Négations: {', '.join(analysis.negations)}")
            
            output.append(f"\n⏱️ Temps: {analysis.processing_time_ms}ms")
            output.append("="*60)
            
            return '\n'.join(output)
        
        elif format_type == 'table':
            from tabulate import tabulate
            table_data = []
            for token in analysis.tokens[:30]:
                table_data.append([
                    token.position,
                    token.text,
                    token.type,
                    token.category or '-',
                    token.weight
                ])
            return tabulate(table_data, headers=['#', 'Token', 'Type', 'Catégorie', 'Poids'])
        
        return str(asdict(analysis))

# =========================================================
# SERVICE SINGLETON
# =========================================================

_lexical_service_instance = None

def get_lexical_service() -> LexicalService:
    """Obtenir l'instance unique du service lexical"""
    global _lexical_service_instance
    if _lexical_service_instance is None:
        _lexical_service_instance = LexicalService()
    return _lexical_service_instance

# =========================================================
# ROUTES FLASK
# =========================================================

def create_lexical_routes():
    """Créer les routes Flask pour le service lexical"""
    from flask import Blueprint, request, jsonify
    
    lexical_bp = Blueprint('lexical', __name__, url_prefix='/api/lexical')
    service = get_lexical_service()
    
    @lexical_bp.route('/analyze', methods=['POST'])
    def analyze():
        """Endpoint d'analyse lexicale"""
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        format_type = data.get('format', 'json')
        
        try:
            result = service.analyze(text)
            
            if format_type == 'json':
                return jsonify({
                    "success": True,
                    "data": asdict(result)
                })
            else:
                return jsonify({
                    "success": True,
                    "data": result,
                    "formatted": service.format_output(result, format_type)
                })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @lexical_bp.route('/extract', methods=['POST'])
    def extract_keywords():
        """Extraire les mots-clés"""
        data = request.get_json()
        text = data.get('text', '')
        top_n = data.get('top_n', 5)
        
        result = service.analyze(text)
        keywords = service.extract_key_phrases(result, top_n)
        
        return jsonify({
            "success": True,
            "text": text,
            "keywords": keywords
        })
    
    @lexical_bp.route('/stats', methods=['GET'])
    def get_stats():
        """Obtenir des statistiques sur l'analyse"""
        # Pour démonstration, analyse d'un texte d'exemple
        sample_text = "fièvre intense et toux sèche depuis 3 jours"
        result = service.analyze(sample_text)
        
        return jsonify({
            "success": True,
            "capabilities": {
                "symptoms_detection": True,
                "negation_detection": True,
                "intensity_detection": True,
                "time_extraction": True,
                "medical_terms_extraction": True
            },
            "sample_stats": result.statistics
        })
    
    return lexical_bp

# =========================================================
# TESTS
# =========================================================

def test_lexical_service():
    """Tester le service lexical"""
    service = get_lexical_service()
    
    print("\n" + "="*60)
    print("🔤 TEST DU SERVICE LEXICAL")
    print("="*60)
    
    test_texts = [
        "J'ai une forte fièvre et une toux sèche depuis 3 jours",
        "Je n'ai pas de fièvre mais j'ai des nausées",
        "Douleur thoracique intense avec essoufflement",
        "Fatigue extrême et courbatures dans tout le corps",
        "Pas de symptômes particuliers"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        print("-"*40)
        
        result = service.analyze(text)
        
        print(f"   Tokens: {result.statistics['total_tokens']}")
        print(f"   Symptômes: {result.symptoms if result.symptoms else 'aucun'}")
        print(f"   Négations: {result.negations if result.negations else 'aucune'}")
        print(f"   Intensificateurs: {result.intensifiers if result.intensifiers else 'aucun'}")
        print(f"   Confiance: {result.statistics['confidence_score']}")
    
    # Formatage
    print("\n" + "="*60)
    print("📄 EXEMPLE DE FORMATAGE")
    print("="*60)
    
    result = service.analyze(test_texts[0])
    print(service.format_output(result, 'text'))
    
    return service

if __name__ == "__main__":
    test_lexical_service()
    
    # Créer l'application Flask pour tester les routes
    try:
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(create_lexical_routes())
        
        print("\n" + "="*60)
        print("🚀 SERVEUR LEXICAL DÉMARRÉ")
        print("="*60)
        print("📍 Endpoints:")
        print("   POST /api/lexical/analyze  - Analyse lexicale")
        print("   POST /api/lexical/extract  - Extraction mots-clés")
        print("   GET  /api/lexical/stats    - Statistiques")
        print("="*60)
        
        app.run(host="127.0.0.1", port=5002, debug=True)
    except ImportError:
        print("Flask non installé - impossible de démarrer le serveur")
