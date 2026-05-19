# nlp_service.py - Service NLP complet pour SHIFAAAI

import re
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter
from datetime import datetime
import unicodedata
import math

# =========================================================
# CLASSES DE DONNÉES
# =========================================================

@dataclass
class Token:
    """Token linguistique"""
    text: str
    lemma: str
    pos_tag: str  # POS tag (NOUN, VERB, ADJ, etc.)
    entity_type: str  # SYMPTOM, DISEASE, MEDICATION, etc.
    start_char: int
    end_char: int
    is_stopword: bool = False
    is_medical: bool = False

@dataclass
class SyntacticParse:
    """Structure syntaxique"""
    sentence: str
    dependencies: List[Tuple[str, str, str]]  # (head, dependent, relation)
    phrases: Dict[str, List[str]]  # NP, VP, PP
    clause_type: str  # declarative, interrogative, negative

@dataclass
class SemanticAnalysis:
    """Analyse sémantique"""
    symptoms: List[Dict[str, Any]]
    negated_symptoms: List[Dict[str, Any]]
    temporal_info: Dict[str, Any]
    intensity_info: Dict[str, Any]
    location_info: List[str]
    confidence: float

@dataclass
class NLPResult:
    """Résultat complet du traitement NLP"""
    original_text: str
    tokens: List[Token]
    entities: List[Dict[str, Any]]
    syntax: SyntacticParse
    semantics: SemanticAnalysis
    predicted_disease: Optional[Dict[str, Any]]
    processing_time_ms: float
    confidence_score: float

# =========================================================
# SERVICE NLP PRINCIPAL
# =========================================================

class NLPService:
    """Service NLP complet pour l'analyse médicale"""
    
    def __init__(self):
        self._init_dictionaries()
        self._init_patterns()
        self._init_pos_tags()
    
    def _init_dictionaries(self):
        """Initialiser les dictionnaires médicaux"""
        
        # Symptômes médicaux
        self.symptom_dict = {
            # Fièvre et température
            "fièvre": {"type": "SYMPTOM", "category": "temperature", "icd10": "R50"},
            "fievre": {"type": "SYMPTOM", "category": "temperature", "icd10": "R50"},
            "frissons": {"type": "SYMPTOM", "category": "temperature"},
            "hyperthermie": {"type": "SYMPTOM", "category": "temperature"},
            
            # Respiratoire
            "toux": {"type": "SYMPTOM", "category": "respiratory", "icd10": "R05"},
            "tousser": {"type": "SYMPTOM", "category": "respiratory", "icd10": "R05"},
            "essoufflement": {"type": "SYMPTOM", "category": "respiratory", "icd10": "R06"},
            "dyspnée": {"type": "SYMPTOM", "category": "respiratory", "icd10": "R06"},
            "expectoration": {"type": "SYMPTOM", "category": "respiratory"},
            "respiration sifflante": {"type": "SYMPTOM", "category": "respiratory"},
            
            # ORL
            "gorge": {"type": "SYMPTOM", "category": "ent"},
            "mal de gorge": {"type": "SYMPTOM", "category": "ent"},
            "nez bouché": {"type": "SYMPTOM", "category": "ent"},
            "éternuement": {"type": "SYMPTOM", "category": "ent"},
            "oreille qui gratte": {"type": "SYMPTOM", "category": "ent"},
            
            # Digestif
            "nausée": {"type": "SYMPTOM", "category": "digestive"},
            "vomissement": {"type": "SYMPTOM", "category": "digestive"},
            "diarrhée": {"type": "SYMPTOM", "category": "digestive", "icd10": "R19"},
            "constipation": {"type": "SYMPTOM", "category": "digestive"},
            "douleur abdominale": {"type": "SYMPTOM", "category": "digestive"},
            
            # Neurologique
            "maux de tête": {"type": "SYMPTOM", "category": "neurological"},
            "migraine": {"type": "SYMPTOM", "category": "neurological", "icd10": "G43"},
            "vertige": {"type": "SYMPTOM", "category": "neurological"},
            "étourdissement": {"type": "SYMPTOM", "category": "neurological"},
            "confusion": {"type": "SYMPTOM", "category": "neurological"},
            
            # Musculo-squelettique
            "douleur": {"type": "SYMPTOM", "category": "pain"},
            "courbature": {"type": "SYMPTOM", "category": "muscular"},
            "douleur articulaire": {"type": "SYMPTOM", "category": "articular"},
            "raideur": {"type": "SYMPTOM", "category": "muscular"},
            "lombalgie": {"type": "SYMPTOM", "category": "back"},
            
            # Général
            "fatigue": {"type": "SYMPTOM", "category": "general", "icd10": "R53"},
            "asthénie": {"type": "SYMPTOM", "category": "general"},
            "perte de poids": {"type": "SYMPTOM", "category": "general"},
            "anorexie": {"type": "SYMPTOM", "category": "general"}
        }
        
        # Maladies
        self.disease_dict = {
            "grippe": {"type": "DISEASE", "category": "infectious", "icd10": "J10"},
            "influenza": {"type": "DISEASE", "category": "infectious", "icd10": "J10"},
            "covid": {"type": "DISEASE", "category": "infectious", "icd10": "U07"},
            "covid-19": {"type": "DISEASE", "category": "infectious", "icd10": "U07"},
            "angine": {"type": "DISEASE", "category": "ent", "icd10": "J02"},
            "pharyngite": {"type": "DISEASE", "category": "ent", "icd10": "J02"},
            "bronchite": {"type": "DISEASE", "category": "respiratory", "icd10": "J20"},
            "pneumonie": {"type": "DISEASE", "category": "respiratory", "icd10": "J18"},
            "gastro": {"type": "DISEASE", "category": "digestive", "icd10": "A09"},
            "migraine": {"type": "DISEASE", "category": "neurological", "icd10": "G43"}
        }
        
        # Médicaments
        self.medication_dict = {
            "paracétamol": {"type": "MEDICATION", "category": "analgesic"},
            "ibuprofène": {"type": "MEDICATION", "category": "nsaid"},
            "aspirine": {"type": "MEDICATION", "category": "analgesic"},
            "amoxicilline": {"type": "MEDICATION", "category": "antibiotic"},
            "ventoline": {"type": "MEDICATION", "category": "bronchodilator"}
        }
        
        # Stopwords français
        self.stopwords = {
            "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "donc", "car",
            "mais", "est", "sont", "a", "au", "aux", "avec", "sans", "pour", "par", "dans",
            "sur", "chez", "entre", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
            "ce", "cette", "ces", "mon", "ton", "son", "ma", "ta", "sa", "mes", "tes", "ses",
            "qui", "que", "quoi", "dont", "où", "lui", "leur", "eux", "cela", "ça"
        }
        
        # Négations
        self.negations = {"pas", "ne", "non", "jamais", "plus", "aucun", "aucune", "sans", "ni"}
        
        # Intensificateurs
        self.intensifiers = {
            "très": 1.5, "beaucoup": 1.3, "extrêmement": 2.0, "trop": 1.5,
            "fort": 1.4, "intense": 1.4, "léger": 0.7, "légèrement": 0.7,
            "assez": 1.2, "peu": 0.6, "vraiment": 1.3
        }
        
        # Modificateurs temporels
        self.time_modifiers = {
            "depuis": "start", "pendant": "duration", "il y a": "ago",
            "aujourd'hui": "today", "hier": "yesterday", "maintenant": "now"
        }
    
    def _init_patterns(self):
        """Initialiser les patterns regex"""
        self.patterns = {
            'number': re.compile(r'\b\d+(?:[.,]\d+)?\b'),
            'date': re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),
            'duration': re.compile(r'(\d+)\s*(?:jours?|heures?|semaines?|mois|années?)'),
            'email': re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b'),
            'sentence_split': re.compile(r'[.!?]+')
        }
    
    def _init_pos_tags(self):
        """Initialiser les tags POS simplifiés"""
        self.pos_keywords = {
            'NOUN': ['fièvre', 'toux', 'douleur', 'fatigue', 'gorge', 'nausée'],
            'VERB': ['avoir', 'ressentir', 'souffrir', 'présenter', 'constater'],
            'ADJ': ['fort', 'intense', 'léger', 'modéré', 'sévère', 'aigu'],
            'ADV': ['très', 'beaucoup', 'peu', 'assez', 'extrêmement']
        }
    
    # =========================================================
    # MÉTHODES PRINCIPALES
    # =========================================================
    
    def process(self, text: str) -> NLPResult:
        """
        Traitement NLP complet du texte
        
        Args:
            text: Texte médical à analyser
            
        Returns:
            NLPResult contenant toutes les analyses
        """
        import time
        start_time = time.time()
        
        original_text = text
        
        # 1. Prétraitement
        text_clean = self._preprocess(text)
        
        # 2. Tokenisation
        tokens = self._tokenize(text_clean)
        
        # 3. Reconnaissance d'entités
        entities = self._extract_entities(tokens, text_clean)
        
        # 4. Analyse syntaxique
        syntax = self._parse_syntax(text_clean, tokens)
        
        # 5. Analyse sémantique
        semantics = self._analyze_semantics(tokens, entities, text_clean)
        
        # 6. Prédiction maladie
        predicted_disease = self._predict_disease(semantics, text_clean)
        
        # 7. Score de confiance
        confidence = self._calculate_confidence(semantics, predicted_disease)
        
        processing_time = (time.time() - start_time) * 1000
        
        return NLPResult(
            original_text=original_text,
            tokens=tokens,
            entities=entities,
            syntax=syntax,
            semantics=semantics,
            predicted_disease=predicted_disease,
            processing_time_ms=round(processing_time, 2),
            confidence_score=confidence
        )
    
    def _preprocess(self, text: str) -> str:
        """Prétraitement du texte"""
        # Normalisation
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ASCII', 'ignore').decode('utf-8')
        text = text.lower()
        
        # Suppression des caractères spéciaux
        text = re.sub(r'[^\w\s\'-]', ' ', text)
        
        # Nettoyage des espaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize(self, text: str) -> List[Token]:
        """Tokenisation avec POS tags basiques"""
        tokens = []
        words = text.split()
        current_pos = 0
        
        for word in words:
            start = text.find(word, current_pos)
            end = start + len(word)
            current_pos = end
            
            # Déterminer le POS tag approximatif
            pos_tag = self._guess_pos_tag(word)
            
            # Vérifier si c'est un stopword
            is_stopword = word in self.stopwords
            
            # Vérifier si c'est un terme médical
            is_medical = word in self.symptom_dict or word in self.disease_dict or word in self.medication_dict
            
            # Déterminer le type d'entité
            entity_type = 'O'
            if word in self.symptom_dict:
                entity_type = 'SYMPTOM'
            elif word in self.disease_dict:
                entity_type = 'DISEASE'
            elif word in self.medication_dict:
                entity_type = 'MEDICATION'
            
            # Lemmatisation simple
            lemma = self._lemmatize(word)
            
            token = Token(
                text=word,
                lemma=lemma,
                pos_tag=pos_tag,
                entity_type=entity_type,
                start_char=start,
                end_char=end,
                is_stopword=is_stopword,
                is_medical=is_medical
            )
            tokens.append(token)
        
        return tokens
    
    def _guess_pos_tag(self, word: str) -> str:
        """Deviner le POS tag d'un mot"""
        if word in self.pos_keywords['NOUN']:
            return 'NOUN'
        if word in self.pos_keywords['VERB']:
            return 'VERB'
        if word in self.pos_keywords['ADJ']:
            return 'ADJ'
        if word in self.pos_keywords['ADV']:
            return 'ADV'
        if re.match(r'\d+', word):
            return 'NUM'
        return 'NOUN'  # Default
    
    def _lemmatize(self, word: str) -> str:
        """Lemmatisation simple"""
        # Règles de base pour le français
        if word.endswith('ent'):
            return word[:-3] + 'er'
        if word.endswith('ant'):
            return word[:-3] + 'er'
        if word.endswith('euse'):
            return word[:-4] + 'eur'
        if word.endswith('te'):
            return word[:-2] + 't'
        if word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        return word
    
    def _extract_entities(self, tokens: List[Token], text: str) -> List[Dict[str, Any]]:
        """Extraire les entités nommées"""
        entities = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token.entity_type != 'O':
                # Détection des entités multi-mots
                entity_text = token.text
                entity_start = token.start_char
                entity_end = token.end_char
                j = i + 1
                
                while j < len(tokens) and tokens[j].entity_type != 'O':
                    entity_text += ' ' + tokens[j].text
                    entity_end = tokens[j].end_char
                    j += 1
                
                entities.append({
                    "text": entity_text,
                    "type": token.entity_type,
                    "start": entity_start,
                    "end": entity_end,
                    "confidence": 0.9
                })
                
                i = j
            else:
                i += 1
        
        return entities
    
    def _parse_syntax(self, text: str, tokens: List[Token]) -> SyntacticParse:
        """Analyse syntaxique simplifiée"""
        # Division en phrases
        sentences = self.patterns['sentence_split'].split(text)
        
        # Détection des dépendances simples
        dependencies = []
        for sent in sentences:
            words = sent.strip().split()
            for i, word in enumerate(words):
                if word in ['et', 'avec', 'mais'] and i > 0:
                    dependencies.append((words[i-1], word, 'conjunction'))
        
        # Extraction des phrases nominales
        phrases = {
            'NP': [],  # Noun phrases
            'VP': [],  # Verb phrases
            'PP': []   # Prepositional phrases
        }
        
        for sent in sentences:
            # Détection simple des phrases nominales
            np_match = re.findall(r'\b(?:une?|la|le|les)\s+(\w+(?:\s+\w+)?)', sent)
            if np_match:
                phrases['NP'].extend(np_match)
        
        # Type de clause
        clause_type = 'declarative'
        if any(neg in text for neg in self.negations):
            clause_type = 'negative'
        if '?' in text:
            clause_type = 'interrogative'
        
        return SyntacticParse(
            sentence=sentences[0] if sentences else text,
            dependencies=dependencies,
            phrases=phrases,
            clause_type=clause_type
        )
    
    def _analyze_semantics(self, tokens: List[Token], entities: List[Dict], text: str) -> SemanticAnalysis:
        """Analyse sémantique complète"""
        symptoms = []
        negated_symptoms = []
        temporal_info = {}
        intensity_info = {}
        locations = []
        
        # Parcourir le texte
        words = text.split()
        
        for i, token in enumerate(tokens):
            # Détection des symptômes
            if token.entity_type == 'SYMPTOM' or token.text in self.symptom_dict:
                symptom_data = {
                    "text": token.text,
                    "start": token.start_char,
                    "end": token.end_char,
                    "category": self.symptom_dict.get(token.text, {}).get('category', 'unknown')
                }
                
                # Vérifier la négation
                is_negated = False
                for j in range(max(0, i-3), i):
                    if tokens[j].text in self.negations:
                        is_negated = True
                        break
                
                # Vérifier l'intensité
                intensity = 1.0
                for j in range(max(0, i-2), i):
                    if tokens[j].text in self.intensifiers:
                        intensity = self.intensifiers[tokens[j].text]
                        symptom_data["intensity"] = intensity
                        intensity_info[token.text] = intensity
                        break
                
                if is_negated:
                    negated_symptoms.append(symptom_data)
                else:
                    symptoms.append(symptom_data)
            
            # Extraction temporelle
            if token.text in self.time_modifiers:
                if i + 1 < len(tokens) and tokens[i+1].text.isdigit():
                    temporal_info[self.time_modifiers[token.text]] = tokens[i+1].text
                elif i + 2 < len(tokens) and tokens[i+1].text.isdigit():
                    temporal_info[self.time_modifiers[token.text]] = f"{tokens[i+1].text} {tokens[i+2].text}"
            
            # Extraction des localisations
            if token.text in ['dans', 'au', 'à', 'sur'] and i + 1 < len(tokens):
                locations.append(tokens[i+1].text)
        
        # Extraction des durées
        duration_match = self.patterns['duration'].search(text)
        if duration_match:
            temporal_info["duration"] = duration_match.group(0)
        
        # Calcul de la confiance sémantique
        confidence = min(0.5 + (len(symptoms) * 0.1), 1.0) if symptoms else 0.3
        
        return SemanticAnalysis(
            symptoms=symptoms,
            negated_symptoms=negated_symptoms,
            temporal_info=temporal_info,
            intensity_info=intensity_info,
            location_info=locations,
            confidence=confidence
        )
    
    def _predict_disease(self, semantics: SemanticAnalysis, text: str) -> Optional[Dict[str, Any]]:
        """Prédire la maladie basée sur les symptômes"""
        symptoms = [s["text"] for s in semantics.symptoms]
        
        if not symptoms:
            return None
        
        # Règles simples de prédiction
        symptoms_set = set(symptoms)
        
        # Grippe
        if 'fièvre' in symptoms_set and 'toux' in symptoms_set:
            return {
                "disease": "Grippe",
                "confidence": 85,
                "icd10": "J10",
                "recommendation": "Repos, hydratation, consultation si aggravation"
            }
        
        # COVID-19
        if 'fièvre' in symptoms_set and ('toux' in symptoms_set or 'fatigue' in symptoms_set):
            return {
                "disease": "COVID-19 (possible)",
                "confidence": 75,
                "icd10": "U07",
                "recommendation": "Test PCR recommandé, isolement"
            }
        
        # Angine
        if 'gorge' in symptoms_set or 'mal de gorge' in symptoms_set:
            return {
                "disease": "Angine / Pharyngite",
                "confidence": 70,
                "icd10": "J02",
                "recommendation": "Gargarismes, consultation si persistance"
            }
        
        # Gastro-entérite
        if ('nausée' in symptoms_set or 'vomissement' in symptoms_set) and 'diarrhée' in symptoms_set:
            return {
                "disease": "Gastro-entérite",
                "confidence": 80,
                "icd10": "A09",
                "recommendation": "Hydratation essentielle, régime sans lactose"
            }
        
        # Migraine
        if 'maux de tête' in symptoms_set or 'migraine' in symptoms_set:
            return {
                "disease": "Migraine",
                "confidence": 65,
                "icd10": "G43",
                "recommendation": "Repos dans l'obscurité, antimigraineux"
            }
        
        return {
            "disease": "Non déterminé",
            "confidence": 40,
            "recommendation": "Consultez un médecin pour un diagnostic précis"
        }
    
    def _calculate_confidence(self, semantics: SemanticAnalysis, prediction: Optional[Dict]) -> float:
        """Calculer le score de confiance global"""
        confidence = 0.0
        
        # Facteur symptômes
        if semantics.symptoms:
            confidence += min(len(semantics.symptoms) * 0.15, 0.5)
        
        # Facteur intensité
        if semantics.intensity_info:
            confidence += 0.1
        
        # Facteur temporel
        if semantics.temporal_info:
            confidence += 0.1
        
        # Facteur prédiction
        if prediction and prediction.get('confidence', 0) > 50:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    # =========================================================
    # MÉTHODES SPÉCIALISÉES
    # =========================================================
    
    def extract_symptoms(self, text: str) -> List[str]:
        """Extraire uniquement les symptômes"""
        result = self.process(text)
        return [s["text"] for s in result.semantics.symptoms]
    
    def extract_diseases(self, text: str) -> List[str]:
        """Extraire les maladies mentionnées"""
        result = self.process(text)
        diseases = [e["text"] for e in result.entities if e["type"] == "DISEASE"]
        return diseases
    
    def get_medical_terms(self, text: str) -> List[str]:
        """Extraire tous les termes médicaux"""
        result = self.process(text)
        medical_terms = [t.text for t in result.tokens if t.is_medical]
        return list(set(medical_terms))
    
    def get_sentence_embedding(self, text: str) -> List[float]:
        """Générer un embedding simple du texte"""
        result = self.process(text)
        # Embedding basé sur les symptômes détectés
        embedding = np.zeros(50)
        for i, symptom in enumerate(result.semantics.symptoms[:10]):
            if i < 50:
                embedding[i] = 1.0
        return embedding.tolist()

# =========================================================
# SERVICE SINGLETON
# =========================================================

_nlp_service_instance = None

def get_nlp_service() -> NLPService:
    """Obtenir l'instance unique du service NLP"""
    global _nlp_service_instance
    if _nlp_service_instance is None:
        _nlp_service_instance = NLPService()
    return _nlp_service_instance

# =========================================================
# ROUTES FLASK
# =========================================================

def create_nlp_routes():
    """Créer les routes Flask pour le service NLP"""
    from flask import Blueprint, request, jsonify
    
    nlp_bp = Blueprint('nlp', __name__, url_prefix='/api/nlp')
    service = get_nlp_service()
    
    @nlp_bp.route('/analyze', methods=['POST'])
    def analyze():
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        result = service.process(text)
        return jsonify({
            "success": True,
            "result": asdict(result)
        })
    
    @nlp_bp.route('/symptoms', methods=['POST'])
    def extract_symptoms():
        data = request.get_json()
        text = data.get('text', '')
        
        symptoms = service.extract_symptoms(text)
        return jsonify({
            "success": True,
            "symptoms": symptoms
        })
    
    return nlp_bp

# =========================================================
# TESTS
# =========================================================

def test_nlp_service():
    """Tester le service NLP"""
    service = get_nlp_service()
    
    print("\n" + "="*60)
    print("🧠 TEST DU SERVICE NLP")
    print("="*60)
    
    test_texts = [
        "J'ai une forte fièvre et une toux sèche depuis 3 jours",
        "Je n'ai pas de fièvre mais j'ai des nausées et des vomissements",
        "Douleur thoracique intense avec essoufflement",
        "Migraine avec nausée et sensibilité à la lumière"
    ]
    
    for text in test_texts:
        print(f"\n📝 Texte: {text}")
        print("-"*40)
        
        result = service.process(text)
        
        print(f"   Symptômes: {[s['text'] for s in result.semantics.symptoms]}")
        print(f"   Négations: {[s['text'] for s in result.semantics.negated_symptoms]}")
        print(f"   Intensité: {result.semantics.intensity_info}")
        print(f"   Prédiction: {result.predicted_disease['disease'] if result.predicted_disease else 'None'}")
        print(f"   Confiance: {result.confidence_score:.2%}")
        print(f"   Temps: {result.processing_time_ms}ms")

if __name__ == "__main__":
    test_nlp_service()
    
    # Démarrer le serveur Flask
    try:
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(create_nlp_routes())
        
        print("\n" + "="*60)
        print("🚀 SERVEUR NLP DÉMARRÉ")
        print("="*60)
        print("📍 Endpoints:")
        print("   POST /api/nlp/analyze   - Analyse NLP complète")
        print("   POST /api/nlp/symptoms  - Extraction symptômes")
        print("="*60)
        
        app.run(host="127.0.0.1", port=5003, debug=True)
    except ImportError:
        print("Flask non installé - impossible de démarrer le serveur")
