# preprocessing.py - Utilitaires de prétraitement pour SHIFAAAI

import re
import hashlib
import unicodedata
import string
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import Counter
from datetime import datetime
import json

# =========================================================
# CONFIGURATION
# =========================================================

class PreprocessingConfig:
    """Configuration du prétraitement"""
    
    # Stopwords français (mots vides)
    FRENCH_STOPWORDS = {
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de',
        'et', 'ou', 'donc', 'car', 'mais', 'alors', 'donc',
        'est', 'sont', 'a', 'au', 'aux', 'avec', 'sans',
        'pour', 'par', 'dans', 'sur', 'chez', 'entre',
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
        'me', 'te', 'se', 'lui', 'leur', 'ce', 'cette', 'ces',
        'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses',
        'qui', 'que', 'quoi', 'dont', 'où',
        'ceci', 'cela', 'ça', 'cet', 'cette'
    }
    
    # Stopwords médicaux (mots à ignorer spécifiquement)
    MEDICAL_STOPWORDS = {
        'patient', 'docteur', 'médecin', 'consultation', 'rendez-vous',
        'prescription', 'ordonnance', 'traitement', 'médicament'
    }
    
    # Caractères à conserver
    KEEP_CHARS = set('abcdefghijklmnopqrstuvwxyzàâäéèêëîïôöùûüç-')
    
    # Ponctuation à supprimer
    PUNCTUATION = string.punctuation + '«»""''…—–'
    
    # Symboles à remplacer par des espaces
    REPLACE_SYMBOLS = {
        '/': ' ', '\\': ' ', '|': ' ', '-': ' ', '_': ' ',
        '*': ' ', '+': ' ', '=': ' ', '<': ' ', '>': ' '
    }

# =========================================================
# PRÉTRAITEMENT DE BASE
# =========================================================

class TextPreprocessor:
    """Classe pour le prétraitement de texte médical"""
    
    def __init__(self):
        self.config = PreprocessingConfig()
    
    def normalize_unicode(self, text: str) -> str:
        """
        Normaliser les caractères Unicode (accents, etc.)
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte normalisé en NFC
        """
        if not text:
            return ""
        return unicodedata.normalize('NFKC', text)
    
    def remove_accents(self, text: str) -> str:
        """
        Supprimer les accents du texte
        
        Args:
            text: Texte avec accents
            
        Returns:
            Texte sans accents
        """
        if not text:
            return ""
        
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        return text
    
    def to_lowercase(self, text: str) -> str:
        """Convertir en minuscules"""
        if not text:
            return ""
        return text.lower()
    
    def remove_punctuation(self, text: str) -> str:
        """
        Supprimer la ponctuation
        
        Args:
            text: Texte avec ponctuation
            
        Returns:
            Texte sans ponctuation
        """
        if not text:
            return ""
        
        translator = str.maketrans('', '', PreprocessingConfig.PUNCTUATION)
        return text.translate(translator)
    
    def remove_digits(self, text: str, keep_as_placeholder: bool = False) -> str:
        """
        Supprimer ou remplacer les chiffres
        
        Args:
            text: Texte avec chiffres
            keep_as_placeholder: Remplacer par '[NUM]' au lieu de supprimer
            
        Returns:
            Texte sans chiffres
        """
        if not text:
            return ""
        
        if keep_as_placeholder:
            return re.sub(r'\d+', '[NUM]', text)
        else:
            return re.sub(r'\d+', '', text)
    
    def replace_symbols(self, text: str) -> str:
        """
        Remplacer les symboles par des espaces
        
        Args:
            text: Texte avec symboles
            
        Returns:
            Texte avec symboles remplacés
        """
        if not text:
            return ""
        
        for symbol, replacement in PreprocessingConfig.REPLACE_SYMBOLS.items():
            text = text.replace(symbol, replacement)
        
        return text
    
    def remove_extra_spaces(self, text: str) -> str:
        """
        Supprimer les espaces en trop
        
        Args:
            text: Texte avec espaces multiples
            
        Returns:
            Texte normalisé
        """
        if not text:
            return ""
        
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def remove_stopwords(self, text: str, include_medical: bool = False) -> List[str]:
        """
        Supprimer les stopwords
        
        Args:
            text: Texte à traiter
            include_medical: Inclure les stopwords médicaux
            
        Returns:
            Liste des mots sans stopwords
        """
        if not text:
            return []
        
        words = text.split()
        stopwords = PreprocessingConfig.FRENCH_STOPWORDS.copy()
        
        if include_medical:
            stopwords.update(PreprocessingConfig.MEDICAL_STOPWORDS)
        
        return [w for w in words if w not in stopwords]
    
    def clean_html(self, text: str) -> str:
        """
        Supprimer les balises HTML
        
        Args:
            text: Texte avec HTML
            
        Returns:
            Texte sans HTML
        """
        if not text:
            return ""
        
        # Supprimer les balises
        text = re.sub(r'<[^>]+>', ' ', text)
        # Supprimer les entités HTML
        text = re.sub(r'&[a-z]+;', ' ', text)
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
        
        return text
    
    def basic_preprocess(self, text: str) -> str:
        """
        Prétraitement de base en une étape
        
        Args:
            text: Texte à prétraiter
            
        Returns:
            Texte prétraité
        """
        if not text:
            return ""
        
        text = self.normalize_unicode(text)
        text = self.clean_html(text)
        text = self.replace_symbols(text)
        text = self.remove_punctuation(text)
        text = self.to_lowercase(text)
        text = self.remove_extra_spaces(text)
        
        return text

# =========================================================
# PRÉTRAITEMENT SPÉCIFIQUE MÉDICAL
# =========================================================

class MedicalTextPreprocessor(TextPreprocessor):
    """Prétraitement spécialisé pour texte médical"""
    
    def __init__(self):
        super().__init__()
        self._init_medical_patterns()
    
    def _init_medical_patterns(self):
        """Initialiser les patterns pour texte médical"""
        
        # Patterns pour normaliser les termes médicaux
        self.medical_patterns = {
            # Unités de mesure
            'temperature': re.compile(r'(\d{2,3})\s*°?\s*[cC](?:elsius)?'),
            'weight': re.compile(r'(\d+(?:[.,]\d+)?)\s*(?:kg|kilo|kilogramme)'),
            'height': re.compile(r'(\d+(?:[.,]\d+)?)\s*(?:cm|centimètre)'),
            
            # Fréquences
            'frequency': re.compile(r'(\d+)\s*(?:fois|fois par jour|×)'),
            
            # Durées
            'duration': re.compile(r'(\d+)\s*(?:jours?|heures?|semaines?|mois|années?)'),
            
            # Dosages
            'dosage': re.compile(r'(\d+(?:[.,]\d+)?)\s*(?:mg|g|ml|µg)'),
            
            # Temps
            'time': re.compile(r'(\d{1,2})[h:]\s*(\d{2})?')
        }
    
    def normalize_medical_terms(self, text: str) -> str:
        """
        Normaliser les termes médicaux courants
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte avec termes normalisés
        """
        if not text:
            return ""
        
        substitutions = {
            r'\bfi[ée]vre\b': 'fievre',
            r'\btoux\s+s[èe]che\b': 'toux_seche',
            r'\bmaux?\s+de\s+t[êe]te\b': 'maux_tete',
            r'\bcourbatures?\b': 'courbatures',
            r'\bessoufflement\b': 'essoufflement',
            r'\bdiarrh[ée]e\b': 'diarrhee',
            r'\bnaus[ée]e\b': 'nausea',
            r'\bvomissements?\b': 'vomissement',
            r'\bvertiges?\b': 'vertige',
            r'\b[ée]ternuements?\b': 'eternuement',
            r'\b[ée]coulement\s+nasal\b': 'ecoulement_nasal',
            r'\bnez\s+bouch[ée]\b': 'nez_bouche',
            r'\bmalaise\b': 'malaise',
            r'\bfrissons?\b': 'frissons',
            r'\bsueurs?\b': 'sueurs',
            r'\bdouleurs?\s+dans\s+la\s+poitrine\b': 'douleur_poitrine',
            r'\bperte\s+d\'?app[ée]tit\b': 'perte_appetit',
            r'\binsomnie\b': 'insomnie'
        }
        
        text = text.lower()
        for pattern, replacement in substitutions.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extraire les entités médicales du texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire des entités extraites
        """
        entities = {
            'symptoms': [],
            'medications': [],
            'medical_terms': [],
            'numbers': [],
            'units': []
        }
        
        # Symptômes courants
        symptoms = [
            'fièvre', 'toux', 'fatigue', 'douleur', 'nausée', 'vomissement',
            'diarrhée', 'essoufflement', 'vertige', 'courbature', 'frisson'
        ]
        
        text_lower = text.lower()
        for symptom in symptoms:
            if symptom in text_lower:
                entities['symptoms'].append(symptom)
        
        # Nombres
        numbers = re.findall(r'\b\d+(?:[.,]\d+)?\b', text)
        entities['numbers'] = numbers
        
        # Unités médicales
        units = re.findall(r'\b(?:mg|g|ml|µg|kg|cm|°C)\b', text)
        entities['units'] = units
        
        return entities
    
    def anonymize_text(self, text: str) -> str:
        """
        Anonymiser le texte (noms, emails, téléphones)
        
        Args:
            text: Texte à anonymiser
            
        Returns:
            Texte anonymisé
        """
        if not text:
            return ""
        
        # Noms propres (capitalisés suivis de lettres)
        text = re.sub(r'\b[A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*\b', '[NOM]', text)
        
        # Emails
        text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', text)
        
        # Téléphones
        text = re.sub(r'\b(0|\+33)[\s.-]?\d[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b', '[TEL]', text)
        
        # Dates
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '[DATE]', text)
        
        return text
    
    def normalize_date_expressions(self, text: str) -> str:
        """
        Normaliser les expressions de dates
        
        Args:
            text: Texte avec dates
            
        Returns:
            Texte avec dates normalisées
        """
        if not text:
            return ""
        
        # Remplacer les dates relatives par des marqueurs
        date_patterns = [
            (r'aujourd\'hui', '[AUJOURDHUI]'),
            (r'hier', '[HIER]'),
            (r'avant-hier', '[AVANT_HIER]'),
            (r'la semaine dernière', '[SEMAINE_DERNIERE]'),
            (r'la semaine prochaine', '[SEMAINE_PROCHAINE]'),
            (r'le mois dernier', '[MOIS_DERNIER]'),
            (r'le mois prochain', '[MOIS_PROCHAIN]'),
            (r'l\'année dernière', '[ANNEE_DERNIERE]'),
            (r'l\'année prochaine', '[ANNEE_PROCHAINE]')
        ]
        
        text = text.lower()
        for pattern, replacement in date_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def medical_preprocess(self, text: str, 
                          normalize_terms: bool = True,
                          extract_entities: bool = False,
                          anonymize: bool = False) -> Dict[str, Any]:
        """
        Prétraitement médical complet
        
        Args:
            text: Texte à prétraiter
            normalize_terms: Normaliser les termes médicaux
            extract_entities: Extraire les entités
            anonymize: Anonymiser le texte
            
        Returns:
            Dictionnaire avec texte traité et entités
        """
        result = {'original': text}
        
        if not text:
            result['processed'] = ""
            return result
        
        # Prétraitement de base
        processed = self.basic_preprocess(text)
        
        # Normalisation médicale
        if normalize_terms:
            processed = self.normalize_medical_terms(processed)
        
        # Anonymisation
        if anonymize:
            processed = self.anonymize_text(processed)
        
        # Normalisation des dates
        processed = self.normalize_date_expressions(processed)
        
        # Suppression des stopwords
        words = self.remove_stopwords(processed, include_medical=True)
        processed_without_stopwords = ' '.join(words)
        
        result['processed'] = processed
        result['processed_without_stopwords'] = processed_without_stopwords
        result['tokens'] = words
        
        # Extraction d'entités
        if extract_entities:
            result['entities'] = self.extract_medical_entities(processed)
        
        return result

# =========================================================
# PRÉTRAITEMENT DE DATASET
# =========================================================

class DatasetPreprocessor:
    """Prétraitement pour datasets médicaux"""
    
    def __init__(self):
        self.text_preprocessor = MedicalTextPreprocessor()
    
    def clean_dataset(self, data: List[Dict[str, Any]], 
                      text_fields: List[str],
                      drop_duplicates: bool = True,
                      drop_nulls: bool = True) -> List[Dict[str, Any]]:
        """
        Nettoyer un dataset médical
        
        Args:
            data: Liste des échantillons
            text_fields: Champs texte à nettoyer
            drop_duplicates: Supprimer les doublons
            drop_nulls: Supprimer les valeurs nulles
            
        Returns:
            Dataset nettoyé
        """
        if not data:
            return []
        
        cleaned = []
        seen = set()
        
        for item in data:
            # Supprimer les valeurs nulles
            if drop_nulls:
                if not all(item.get(field) for field in text_fields):
                    continue
            
            # Créer une copie
            cleaned_item = item.copy()
            
            # Nettoyer les champs texte
            for field in text_fields:
                if field in cleaned_item and cleaned_item[field]:
                    cleaned_item[field] = self.text_preprocessor.basic_preprocess(
                        str(cleaned_item[field])
                    )
            
            # Supprimer les doublons
            if drop_duplicates:
                item_hash = self._hash_item(cleaned_item, text_fields)
                if item_hash in seen:
                    continue
                seen.add(item_hash)
            
            cleaned.append(cleaned_item)
        
        return cleaned
    
    def _hash_item(self, item: Dict[str, Any], fields: List[str]) -> str:
        """Générer un hash pour un item"""
        hash_str = '|'.join(str(item.get(f, '')) for f in fields)
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def augment_dataset(self, data: List[Dict[str, Any]], 
                        text_field: str,
                        augmentation_factor: int = 2) -> List[Dict[str, Any]]:
        """
        Augmenter le dataset par synonymes et variations
        
        Args:
            data: Dataset original
            text_field: Champ texte à augmenter
            augmentation_factor: Facteur d'augmentation
            
        Returns:
            Dataset augmenté
        """
        if not data:
            return []
        
        augmented = data.copy()
        
        # Synonymes médicaux
        synonyms = {
            'fièvre': ['fievre', 'température élevée', 'hyperthermie'],
            'toux': ['tousser', 'quinte de toux', 'toux sèche'],
            'fatigue': ['asthénie', 'épuisement', 'lassitude'],
            'douleur': ['mal', 'douleurs', 'algie']
        }
        
        for item in data:
            for _ in range(augmentation_factor - 1):
                new_item = item.copy()
                text = str(item.get(text_field, ''))
                
                # Remplacer par des synonymes
                for original, syn_list in synonyms.items():
                    if original in text:
                        new_text = text.replace(original, syn_list[0])
                        new_item[text_field] = new_text
                        break
                
                augmented.append(new_item)
        
        return augmented

# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================

def tokenize_text(text: str, min_token_length: int = 2) -> List[str]:
    """
    Tokenizer simple pour texte prétraité
    
    Args:
        text: Texte à tokenizer
        min_token_length: Longueur minimale des tokens
        
    Returns:
        Liste des tokens
    """
    if not text:
        return []
    
    # Nettoyage
    text = re.sub(r'[^\w\s-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    tokens = text.lower().split()
    return [t for t in tokens if len(t) >= min_token_length]

def build_vocabulary(tokens_list: List[List[str]], 
                     min_frequency: int = 2,
                     max_vocab_size: int = 10000) -> Dict[str, int]:
    """
    Construire un vocabulaire à partir des tokens
    
    Args:
        tokens_list: Liste des listes de tokens
        min_frequency: Fréquence minimale
        max_vocab_size: Taille maximale du vocabulaire
        
    Returns:
        Dictionnaire token -> index
    """
    # Compter les fréquences
    counter = Counter()
    for tokens in tokens_list:
        counter.update(set(tokens))  # Compter chaque document une fois
    
    # Filtrer et trier
    vocab = {word: idx for idx, (word, count) in enumerate(
        counter.most_common(max_vocab_size)
    ) if count >= min_frequency}
    
    # Ajouter des tokens spéciaux
    special_tokens = ['[PAD]', '[UNK]', '[CLS]', '[SEP]']
    for token in reversed(special_tokens):
        if token not in vocab:
            vocab = {token: len(vocab), **vocab}
    
    return vocab

def process_batch(texts: List[str], preprocessor: MedicalTextPreprocessor) -> List[Dict]:
    """
    Traiter un lot de textes
    
    Args:
        texts: Liste des textes
        preprocessor: Instance de MedicalTextPreprocessor
        
    Returns:
        Liste des résultats de prétraitement
    """
    results = []
    for text in texts:
        results.append(preprocessor.medical_preprocess(text, extract_entities=True))
    return results

# =========================================================
# INTÉGRATION AVEC DATAFRAME
# =========================================================

def preprocess_dataframe_column(df, column_name: str, 
                                 preprocessor: MedicalTextPreprocessor = None,
                                 **kwargs) -> List[str]:
    """
    Prétraiter une colonne de DataFrame
    
    Args:
        df: DataFrame pandas
        column_name: Nom de la colonne
        preprocessor: Instance de preprocesseur
        **kwargs: Arguments pour medical_preprocess
        
    Returns:
        Liste des textes prétraités
    """
    if preprocessor is None:
        preprocessor = MedicalTextPreprocessor()
    
    results = []
    for text in df[column_name]:
        if text and isinstance(text, str):
            processed = preprocessor.medical_preprocess(text, **kwargs)
            results.append(processed.get('processed', ''))
        else:
            results.append('')
    
    return results

# =========================================================
# TESTS
# =========================================================

def test_preprocessing():
    """Tester les utilitaires de prétraitement"""
    
    print("\n" + "="*60)
    print("🔧 TEST DES UTILITAIRES DE PRÉTRAITEMENT")
    print("="*60)
    
    preprocessor = MedicalTextPreprocessor()
    
    # Test texte médical
    medical_text = """
    Patient: Jean DUPONT
    Téléphone: 06 12 34 56 78
    Email: jean.dupont@email.com
    
    Le patient présente une forte fièvre (38.5°C) associée à une toux sèche 
    persistante depuis 3 jours. Il ressent également une grande fatigue 
    et des courbatures dans tout le corps.
    
    Traitement actuel: Paracétamol 1000mg 3 fois par jour.
    """
    
    print(f"\n📝 Texte original:\n{medical_text}")
    
    # Prétraitement basique
    basic = preprocessor.basic_preprocess(medical_text)
    print(f"\n🧹 Prétraitement basique:\n{basic[:200]}...")
    
    # Prétraitement médical
    medical_result = preprocessor.medical_preprocess(
        medical_text, 
        normalize_terms=True,
        extract_entities=True,
        anonymize=True
    )
    
    print(f"\n🏥 Prétraitement médical:")
    print(f"   Texte: {medical_result['processed'][:150]}...")
    print(f"   Tokens: {len(medical_result.get('tokens', []))}")
    print(f"   Symptômes: {medical_result.get('entities', {}).get('symptoms', [])}")
    print(f"   Nombres: {medical_result.get('entities', {}).get('numbers', [])}")
    
    # Tokenisation
    tokens = tokenize_text(basic)
    print(f"\n🔤 Tokens: {tokens[:10]}...")
    
    print("\n✅ Tests terminés avec succès")

if __name__ == "__main__":
    test_preprocessing()
    print("\n" + "="*60)
    print("📚 UTILITAIRES DISPONIBLES")
    print("="*60)
    print("""
Classes:
    TextPreprocessor - Prétraitement texte de base
    MedicalTextPreprocessor - Prétraitement texte médical
    DatasetPreprocessor - Prétraitement dataset

Fonctions:
    tokenize_text() - Tokenisation simple
    build_vocabulary() - Construction vocabulaire
    process_batch() - Traitement par lots
    preprocess_dataframe_column() - Prétraitement pour DataFrame
""")