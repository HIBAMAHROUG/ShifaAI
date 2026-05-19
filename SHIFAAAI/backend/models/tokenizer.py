"""Tokenizes medical text into normalized symbols and metadata."""

import re
import json
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import Counter
import unicodedata

@dataclass
class Token:
    text: str
    original_text: str
    type: str
    position: int
    start_char: int
    end_char: int
    lemma: Optional[str] = None
    is_stopword: bool = False
    is_medical: bool = False
    confidence: float = 1.0

@dataclass
class TokenizationResult:
    original_text: str
    tokens: List[Token]
    num_tokens: int
    num_medical_terms: int
    num_symptoms: int
    medical_terms: List[str]
    symptoms_list: List[str]
    word_frequency: Dict[str, int]
    processing_time_ms: float

class MedicalTokenizer:
    def __init__(self):
        self.medical_terms = self._init_medical_terms()
        self.symptoms = self._init_symptoms()
        self.medical_stopwords = self._init_stopwords()
        self.token_types = {
            'SYMPTOM': 'symptom',
            'MEDICAL_TERM': 'medical_term',
            'NEGATION': 'negation',
            'INTENSIFIER': 'intensifier',
            'NUMBER': 'number',
            'TIME': 'time',
            'PUNCTUATION': 'punctuation',
            'WORD': 'word'
        }
        
        self.patterns = self._init_patterns()
        self.negations = {'pas', 'ne', 'non', 'jamais', 'plus', 'aucun', 'sans', 'ni', 'aucune'}
        self.intensifiers = {'très', 'beaucoup', 'extrêmement', 'trop', 'fort', 'intense', 
                            'léger', 'légèrement', 'assez', 'peu', 'vraiment', 'absolument'}
        self.time_words = {'depuis', 'pendant', 'il y a', 'hier', 'aujourd\'hui', 'demain',
                          'matin', 'soir', 'nuit', 'jour', 'semaine', 'mois', 'année'}
    
    def _init_medical_terms(self) -> Dict[str, str]:
        return {
            'fièvre': 'symptom', 'fievre': 'symptom', 'toux': 'symptom', 'fatigue': 'symptom',
            'douleur': 'symptom', 'courbature': 'symptom', 'nausée': 'symptom', 'vomissement': 'symptom',
            'diarrhée': 'symptom', 'migraine': 'symptom', 'vertige': 'symptom', 'essoufflement': 'symptom',
            'tachycardie': 'sign', 'bradycardie': 'sign', 'hypertension': 'sign', 'hypotension': 'sign',
            'cyanose': 'sign', 'pâleur': 'sign', 'rougeur': 'sign', 'œdème': 'sign',
            'radiographie': 'exam', 'scanner': 'exam', 'irm': 'exam', 'prise de sang': 'exam',
            'test': 'exam', 'analyse': 'exam', 'bilan': 'exam',
            'antibiotique': 'treatment', 'antidouleur': 'treatment', 'repos': 'treatment',
            'hydratation': 'treatment', 'consultation': 'treatment', 'hospitalisation': 'treatment'
        }
    
    def _init_symptoms(self) -> set:
        return {
            'fièvre', 'fievre', 'toux', 'fatigue', 'douleur', 'courbature', 'courbatures',
            'frisson', 'frissons', 'gorge', 'nez', 'éternuement', 'maux de tête', 'mal de tête',
            'nausée', 'nausées', 'vomissement', 'vomissements', 'diarrhée', 'constipation',
            'essoufflement', 'respiration difficile', 'oppression', 'palpitation', 'vertige',
            'étourdissement', 'perte connaissance', 'confusion', 'tremblement', 'insomnie',
            'anxiété', 'dépression', 'perte poids', 'perte appétit', 'démangeaison', 'éruption'
        }
    
    def _init_stopwords(self) -> set:
        return {
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'donc', 'car',
            'mais', 'est', 'sont', 'a', 'au', 'aux', 'avec', 'sans', 'pour', 'par', 'dans',
            'sur', 'chez', 'entre', 'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'ce', 'cette', 'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
            'qui', 'que', 'quoi', 'dont', 'où', 'lui', 'leur', 'eux', 'cela', 'ça'
        }
    
    def _init_patterns(self) -> List[Tuple[str, str]]:
        return [
            (r'\b\d+(?:\.\d+)?\b', 'NUMBER'),
            (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', 'DATE'),
            (r'\b\d{1,2}:\d{2}\b', 'TIME'),
            (r'[.!?;,:()\[\]{}\'\"„”«»]', 'PUNCTUATION'),
            (r'\b(?:d[ea]|du|des?|le|la|les?)\s+(?:courbatures?|douleurs?)\b', 'MEDICAL_PHRASE'),
            (r'\b(?:très|beaucoup|extrêmement)\s+(?:fort|intense)\s+(?:douleur|fièvre)\b', 'INTENSITY_PHRASE'),
        ]
    
    def tokenize(self, text: str) -> TokenizationResult:
        import time
        start_time = time.time()
        
        original_text = text
        text_lower = text.lower()
        
        text_clean = self._preprocess(text)
        raw_tokens = self._basic_tokenize(text_clean)
        tokens = []
        medical_terms = []
        symptoms_list = []
        
        for i, (token_text, start_char, end_char) in enumerate(raw_tokens):
            token_type = self._classify_token(token_text, text_lower, i)
            is_medical = token_type in ['symptom', 'medical_term']
            is_stopword = token_text in self.medical_stopwords
            
            if is_medical:
                medical_terms.append(token_text)
                if token_type == 'symptom':
                    symptoms_list.append(token_text)
            
            lemma = self._get_lemma(token_text)
            
            tokens.append(Token(
                text=token_text,
                original_text=token_text,
                type=token_type,
                position=i,
                start_char=start_char,
                end_char=end_char,
                lemma=lemma,
                is_stopword=is_stopword,
                is_medical=is_medical,
                confidence=0.95 if is_medical else 0.85
            ))
        
        word_frequency = Counter([t.text for t in tokens if t.type == 'word' or t.is_medical])
        
        processing_time = (time.time() - start_time) * 1000
        
        return TokenizationResult(
            original_text=original_text,
            tokens=tokens,
            num_tokens=len(tokens),
            num_medical_terms=len(medical_terms),
            num_symptoms=len(symptoms_list),
            medical_terms=list(set(medical_terms)),
            symptoms_list=list(set(symptoms_list)),
            word_frequency=dict(word_frequency.most_common(10)),
            processing_time_ms=round(processing_time, 2)
        )
    
    def _preprocess(self, text: str) -> str:
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        text = text.replace("'", "'")
        text = re.sub(r'([.!?;,:()\[\]{}\'\"„”«»])', r' \1 ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _basic_tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        tokens = []
        current_pos = 0
        text_remaining = text
        
        while text_remaining:
            matched = False
            for pattern, token_type in self.patterns:
                match = re.match(pattern, text_remaining, re.IGNORECASE)
                if match:
                    token_text = match.group(0)
                    start = current_pos
                    end = start + len(token_text)
                    tokens.append((token_text, start, end))
                    text_remaining = text_remaining[len(token_text):]
                    current_pos = end
                    matched = True
                    break
            if not matched:
                match = re.match(r'\S+', text_remaining)
                if match:
                    token_text = match.group(0)
                    start = current_pos
                    end = start + len(token_text)
                    tokens.append((token_text, start, end))
                    text_remaining = text_remaining[len(token_text):]
                    current_pos = end
                else:
                    break
            
            # Ignorer les espaces
            if text_remaining and text_remaining[0].isspace():
                text_remaining = text_remaining[1:]
                current_pos += 1
        
        return tokens
    
    def _classify_token(self, token: str, full_text: str, position: int) -> str:
        """Classifier un token selon son type"""
        token_lower = token.lower()
        
        # Vérifier si c'est un symptôme
        if token_lower in self.symptoms:
            return 'symptom'
        
        # Vérifier si c'est un terme médical
        if token_lower in self.medical_terms:
            return 'medical_term'
        
        # Vérifier si c'est une négation
        if token_lower in self.negations:
            return 'negation'
        
        # Vérifier si c'est un intensificateur
        if token_lower in self.intensifiers:
            return 'intensifier'
        
        # Vérifier si c'est un nombre
        if re.match(r'^\d+$', token):
            return 'number'
        
        # Vérifier si c'est une ponctuation
        if re.match(r'^[.!?;,:()\[\]{}\'\"„”«»]$', token):
            return 'punctuation'
        
        # Vérifier si c'est un mot temporel
        if token_lower in self.time_words:
            return 'time'
        
        return 'word'
    
    def _get_lemma(self, word: str) -> str:
        """Obtenir le lemme d'un mot (version simplifiée)"""
        # Règles de lemmatisation simples pour le français
        if word.endswith('euse'):
            return word[:-4] + 'eur'
        if word.endswith('te'):
            return word[:-2] + 't'
        if word.endswith('s') and not word.endswith('ss'):
            return word[:-1]
        if word.endswith('ent') and len(word) > 5:
            return word[:-3]
        if word.endswith('ant'):
            return word[:-3] + 'er'
        
        return word

# =========================================================
# TOKENIZER AVANCÉ AVEC ANALYSE CONTEXTUELLE
# =========================================================

class AdvancedMedicalTokenizer(MedicalTokenizer):
    """Tokeniseur avancé avec analyse contextuelle"""
    
    def __init__(self):
        super().__init__()
        self.context_window = 3
        self.ngram_min = 1
        self.ngram_max = 3
    
    def tokenize_advanced(self, text: str) -> Dict[str, Any]:
        """
        Tokenisation avancée avec n-grams et analyse contextuelle
        """
        basic_result = super().tokenize(text)
        
        # Extraire les n-grams médicaux
        tokens_text = [t.text for t in basic_result.tokens if not t.is_stopword]
        
        ngrams = self._extract_ngrams(tokens_text)
        
        # Analyser le contexte
        context_analysis = self._analyze_context(basic_result.tokens)
        
        # Détecter les phrases médicales
        medical_phrases = self._detect_medical_phrases(text)
        
        return {
            "basic": asdict(basic_result),
            "advanced": {
                "ngrams": ngrams,
                "context_analysis": context_analysis,
                "medical_phrases": medical_phrases,
                "token_sequence": " → ".join([f"{t.text}({t.type})" for t in basic_result.tokens[:20]])
            }
        }
    
    def _extract_ngrams(self, tokens: List[str]) -> Dict[str, List[Tuple[str, int]]]:
        """Extraire les n-grams des tokens"""
        ngrams = {}
        
        for n in range(self.ngram_min, self.ngram_max + 1):
            ngram_list = []
            for i in range(len(tokens) - n + 1):
                ngram = ' '.join(tokens[i:i+n])
                ngram_list.append(ngram)
            
            # Compter les fréquences
            ngram_counts = Counter(ngram_list)
            ngrams[f"{n}_gram"] = ngram_counts.most_common(10)
        
        return ngrams
    
    def _analyze_context(self, tokens: List[Token]) -> Dict[str, Any]:
        """Analyser le contexte des tokens"""
        context_analysis = {
            "negation_contexts": [],
            "intensity_contexts": [],
            "symptom_relations": []
        }
        
        for i, token in enumerate(tokens):
            if token.type == 'negation':
                # Chercher les symptômes dans la fenêtre contextuelle
                start = max(0, i - self.context_window)
                end = min(len(tokens), i + self.context_window)
                context_tokens = tokens[start:end]
                affected_symptoms = [t.text for t in context_tokens if t.type == 'symptom']
                
                if affected_symptoms:
                    context_analysis["negation_contexts"].append({
                        "negation": token.text,
                        "affected_symptoms": affected_symptoms,
                        "position": i
                    })
            
            elif token.type == 'intensifier' and i < len(tokens) - 1:
                # Vérifier le token suivant
                if tokens[i+1].type in ['symptom', 'medical_term']:
                    context_analysis["intensity_contexts"].append({
                        "intensifier": token.text,
                        "affected_term": tokens[i+1].text,
                        "position": i
                    })
            
            elif token.type == 'symptom':
                # Chercher les relations avec d'autres symptômes
                relations = []
                for j in range(max(0, i-5), min(len(tokens), i+5)):
                    if j != i and tokens[j].type in ['symptom', 'medical_term']:
                        relations.append({
                            "related_token": tokens[j].text,
                            "distance": abs(j - i),
                            "type": tokens[j].type
                        })
                
                if relations:
                    context_analysis["symptom_relations"].append({
                        "symptom": token.text,
                        "relations": relations[:3]
                    })
        
        return context_analysis
    
    def _detect_medical_phrases(self, text: str) -> List[Dict[str, Any]]:
        """Détecter les phrases médicales complexes"""
        medical_phrases = []
        
        # Patterns pour reconnaître les phrases médicales
        phrase_patterns = [
            (r'(?:je\s+)?(?:ressens?|ai|suis|a(?:i|vais|i)?|éprouve?)\s+(?:une\s+)?(douleur|fièvre|fatigue|nausée)\s+(?:\w+\s+)*?(?:depuis|pendant)\s+(\d+\s*(?:jours?|heures?))', 4),
            (r'(?:je\s+)?(?:n\'?(?:ai|éprouve|ressens)?\s+pas\s+de)\s+(fièvre|douleur|toux)', 3),
            (r'(?:c\'est\s+)?(?:très|trop|extrêmement)\s+(?:fort|intense|douloureux)', 2),
        ]
        
        for pattern, confidence in phrase_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                medical_phrases.append({
                    "phrase": match.group(0),
                    "confidence": confidence,
                    "position": match.start()
                })
        
        return medical_phrases

# =========================================================
# VISUALISATION DES TOKENS
# =========================================================

def visualize_tokens(result: TokenizationResult) -> str:
    """Visualiser les tokens avec leurs types"""
    
    # Couleurs pour les différents types (ANSI)
    colors = {
        'symptom': '\033[95m',      # Magenta
        'medical_term': '\033[94m',  # Bleu
        'negation': '\033[91m',      # Rouge
        'intensifier': '\033[93m',   # Jaune
        'number': '\033[96m',        # Cyan
        'time': '\033[92m',          # Vert
        'default': '\033[0m'         # Reset
    }
    
    output = []
    output.append("\n" + "="*80)
    output.append("📊 TOKENISATION MÉDICALE - VISUALISATION")
    output.append("="*80)
    
    output.append(f"\n📝 Texte original: {result.original_text[:100]}...")
    output.append(f"🔢 Nombre de tokens: {result.num_tokens}")
    output.append(f"🏥 Termes médicaux: {result.num_medical_terms}")
    output.append(f"🩺 Symptômes: {result.num_symptoms}")
    output.append(f"⏱️ Temps de traitement: {result.processing_time_ms}ms")
    
    output.append("\n" + "-"*80)
    output.append("🎨 Légende:")
    output.append(f"{colors['symptom']}🟣 Symptôme{colors['default']} | {colors['medical_term']}🔵 Terme médical{colors['default']} | {colors['negation']}🔴 Négation{colors['default']}")
    output.append(f"{colors['intensifier']}🟡 Intensificateur{colors['default']} | {colors['number']}🟢 Nombre{colors['default']} | {colors['time']}🟢 Temps{colors['default']}")
    output.append("-"*80)
    
    output.append("\n🔍 Séquence des tokens:")
    
    line = []
    for token in result.tokens:
        color = colors.get(token.type, colors['default'])
        line.append(f"{color}{token.text}({token.type[0]}){colors['default']}")
    
    output.append(" ".join(line))
    
    if result.medical_terms:
        output.append(f"\n🏥 Termes médicaux détectés: {', '.join(result.medical_terms[:10])}")
    
    if result.symptoms_list:
        output.append(f"🩺 Symptômes: {', '.join(result.symptoms_list)}")
    
    return '\n'.join(output)

# =========================================================
# TESTS
# =========================================================

def test_tokenizer():
    """Tester le tokenizer médical"""
    
    test_texts = [
        "J'ai une forte fièvre et une toux sèche depuis 3 jours",
        "Je n'ai pas de fièvre mais j'ai des nausées",
        "Douleur thoracique intense avec essoufflement",
        "Les courbatures sont très intenses dans tout le corps",
        "Fièvre à 39.5°C, fatigue extrême et perte d'appétit"
    ]
    
    tokenizer = MedicalTokenizer()
    advanced_tokenizer = AdvancedMedicalTokenizer()
    
    print("\n" + "="*80)
    print("🧪 TESTS DU TOKENIZER MÉDICAL")
    print("="*80)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 Test {i}: {text}")
        print("-"*40)
        
        # Tokenisation basique
        result = tokenizer.tokenize(text)
        print(f"✅ {result.num_tokens} tokens, {result.num_medical_terms} termes médicaux")
        print(f"🩺 Symptômes: {', '.join(result.symptoms_list)}")
        
        # Tokenisation avancée
        advanced_result = advanced_tokenizer.tokenize_advanced(text)
        print(f"🔬 N-grams détectés: {len(advanced_result['advanced']['ngrams'].get('2_gram', []))}")
    
    # Visualisation du premier exemple
    print("\n" + visualize_tokens(tokenizer.tokenize(test_texts[0])))

def test_edge_cases():
    """Tester les cas limites"""
    
    edge_cases = [
        "",  # Texte vide
        "fièvre",  # Un seul mot
        "J'ai une fièvre de 39.5°C depuis mercredi dernier, et une toux qui dure",  # Texte long
        "Pas de fièvre, pas de toux, rien du tout",  # Négations
    ]
    
    tokenizer = MedicalTokenizer()
    
    print("\n" + "="*80)
    print("🧪 TESTS DES CAS LIMITES")
    print("="*80)
    
    for text in edge_cases:
        print(f"\n📝 Texte: '{text[:50]}'")
        result = tokenizer.tokenize(text)
        
        if result.num_tokens == 0:
            print("⚠️ Aucun token généré")
        else:
            print(f"✅ Tokens: {[t.text for t in result.tokens[:10]]}")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    test_tokenizer()
    test_edge_cases()
    
    print("\n" + "="*80)
    print("💡 UTILISATION AVEC L'API")
    print("="*80)
    print("""
    from tokenizer_model import MedicalTokenizer
    
    tokenizer = MedicalTokenizer()
    result = tokenizer.tokenize("fièvre et toux depuis 3 jours")
    
    # Accéder aux tokens
    for token in result.tokens:
        print(f"{token.text} [{token.type}]")
    
    # Accéder aux statistiques
    print(f"Symptômes: {result.symptoms_list}")
    """)