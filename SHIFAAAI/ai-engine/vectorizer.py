"""Builds text vectorizers for SHIFAAAI medical symptom models."""

import pickle
import numpy as np
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.decomposition import TruncatedSVD
from typing import List, Dict, Any, Optional, Union
import os
from datetime import datetime

class VectorizerConfig:
    DEFAULT_MAX_FEATURES = 10000
    DEFAULT_NGRAM_RANGE = (1, 3)
    DEFAULT_MIN_DF = 2
    DEFAULT_MAX_DF = 0.95
    VECTORIZER_TYPES = ['tfidf', 'count', 'hashing']
    MEDICAL_STOPWORDS = [
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'donc',
        'car', 'mais', 'est', 'sont', 'a', 'au', 'aux', 'avec', 'sans', 'pour',
        'par', 'dans', 'sur', 'chez', 'entre', 'je', 'tu', 'il', 'elle', 'nous',
        'vous', 'ils', 'elles', 'ce', 'cette', 'ces', 'mon', 'ton', 'son',
        'ma', 'ta', 'sa', 'mes', 'tes', 'ses', 'qui', 'que', 'quoi', 'dont'
    ]

class ShifaaVectorizer:
    def __init__(self, 
                 max_features: int = VectorizerConfig.DEFAULT_MAX_FEATURES,
                 ngram_range: tuple = VectorizerConfig.DEFAULT_NGRAM_RANGE,
                 min_df: int = VectorizerConfig.DEFAULT_MIN_DF,
                 max_df: float = VectorizerConfig.DEFAULT_MAX_DF,
                 vectorizer_type: str = 'tfidf',
                 use_svd: bool = False,
                 svd_components: int = 100):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.vectorizer_type = vectorizer_type
        self.use_svd = use_svd
        self.svd_components = svd_components
        
        self.vectorizer = None
        self.svd = None
        self.is_fitted = False
        self.feature_names = []
        
        self._create_vectorizer()
    
    def _create_vectorizer(self):
        common_params = {
            'ngram_range': self.ngram_range,
            'stop_words': VectorizerConfig.MEDICAL_STOPWORDS,
            'lowercase': True
        }
        
        if self.vectorizer_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                sublinear_tf=True,
                **common_params
            )
        elif self.vectorizer_type == 'count':
            self.vectorizer = CountVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                **common_params
            )
        elif self.vectorizer_type == 'hashing':
            self.vectorizer = HashingVectorizer(
                n_features=self.max_features,
                alternate_sign=False,
                **common_params
            )
        else:
            raise ValueError(f"Type de vectorizer inconnu: {self.vectorizer_type}")
        
        if self.use_svd:
            self.svd = TruncatedSVD(
                n_components=self.svd_components,
                random_state=42
            )
    
    def fit(self, texts: List[str]) -> 'ShifaaVectorizer':
        cleaned_texts = [self._clean_text(t) for t in texts]
        self.vectorizer.fit(cleaned_texts)
        self.is_fitted = True
        if hasattr(self.vectorizer, 'get_feature_names_out'):
            self.feature_names = self.vectorizer.get_feature_names_out()
        elif hasattr(self.vectorizer, 'get_feature_names'):
            self.feature_names = self.vectorizer.get_feature_names()
        if self.use_svd:
            X = self.vectorizer.transform(cleaned_texts)
            self.svd.fit(X)
        print(f"Vectorizer trained: {len(self.feature_names)} features")
        
        return self
    
    def transform(self, texts: Union[str, List[str]]) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Le vectorizer doit d'abord être entraîné")
        if isinstance(texts, str):
            texts = [texts]
        cleaned_texts = [self._clean_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned_texts)
        if self.use_svd:
            X = self.svd.transform(X)
        
        return X
    
    def fit_transform(self, texts: List[str]) -> np.ndarray:
        self.fit(texts)
        return self.transform(texts)
    
    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        text = text.lower()
        replacements = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'ô': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i',
            'ç': 'c'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def get_feature_importance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        if not self.is_fitted:
            return []
        
        # Pour TF-IDF, on peut obtenir les scores moyens
        if self.vectorizer_type == 'tfidf' and hasattr(self.vectorizer, 'idf_'):
            scores = self.vectorizer.idf_
            # Trier par importance (plus petit IDF = plus fréquent/important)
            indices = np.argsort(scores)[:top_n]
            
            return [
                {
                    'feature': self.feature_names[i],
                    'score': scores[i]
                }
                for i in indices
            ]
        
        return []
    
    def get_vocabulary(self) -> Dict[str, int]:
        """
        Obtenir le vocabulaire
        
        Returns:
            Dictionnaire {mot: index}
        """
        if hasattr(self.vectorizer, 'vocabulary_'):
            return self.vectorizer.vocabulary_
        return {}
    
    def save(self, path: str = 'models/vectorizer.pkl'):
        """
        Sauvegarder le vectorizer
        
        Args:
            path: Chemin de sauvegarde
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        
        print(f"💾 Vectorizer sauvegardé: {path}")
    
    @staticmethod
    def load(path: str = 'models/vectorizer.pkl') -> 'ShifaaVectorizer':
        """
        Charger un vectorizer sauvegardé
        
        Args:
            path: Chemin du fichier
            
        Returns:
            Vectorizer chargé
        """
        with open(path, 'rb') as f:
            vectorizer = pickle.load(f)
        
        print(f"✅ Vectorizer chargé: {path}")
        return vectorizer

# =========================================================
# VECTORIZER SPÉCIALISÉ POUR TEXTE MÉDICAL
# =========================================================

class MedicalVectorizer(ShifaaVectorizer):
    """
    Vectorizer spécialisé pour le texte médical
    avec vocabulaire médical prédéfini
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_medical_vocabulary()
    
    def _init_medical_vocabulary(self):
        """Initialiser le vocabulaire médical de base"""
        
        self.medical_terms = {
            # Symptômes courants
            'fievre': 1.0, 'toux': 1.0, 'fatigue': 0.8, 'douleur': 0.9,
            'gorge': 0.7, 'nausee': 0.7, 'vomissement': 0.8, 'diarrhee': 0.8,
            'essoufflement': 0.9, 'vertige': 0.7, 'maux': 0.6, 'tete': 0.6,
            
            # Intensités
            'forte': 0.5, 'intense': 0.5, 'leger': 0.3, 'modere': 0.4,
            'severe': 0.6, 'chronique': 0.5, 'aigu': 0.5,
            
            # Durées
            'depuis': 0.4, 'pendant': 0.4, 'jours': 0.3, 'semaines': 0.3,
            
            # Localisations
            'poitrine': 0.5, 'ventre': 0.5, 'dos': 0.4, 'bras': 0.4,
            'jambe': 0.4, 'epaule': 0.4, 'genou': 0.4
        }
    
    def transform_with_weights(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Transformer avec pondération des termes médicaux
        
        Args:
            texts: Texte ou liste de textes
            
        Returns:
            Matrice de features pondérée
        """
        X = self.transform(texts)
        
        # Appliquer des poids supplémentaires aux termes médicaux
        # (à implémenter selon les besoins)
        
        return X

# =========================================================
# UTILITAIRES POUR VECTORIZER
# =========================================================

def create_vectorizer_from_data(texts: List[str], 
                                vectorizer_type: str = 'tfidf',
                                max_features: int = 5000) -> ShifaaVectorizer:
    """
    Créer et entraîner un vectorizer à partir de données
    
    Args:
        texts: Liste des textes
        vectorizer_type: Type de vectorizer
        max_features: Nombre maximum de features
        
    Returns:
        Vectorizer entraîné
    """
    vectorizer = ShifaaVectorizer(
        max_features=max_features,
        vectorizer_type=vectorizer_type
    )
    
    vectorizer.fit(texts)
    return vectorizer

def vectorize_symptoms(symptoms: List[str], 
                       vectorizer: ShifaaVectorizer = None,
                       train: bool = True) -> np.ndarray:
    """
    Vectoriser une liste de symptômes
    
    Args:
        symptoms: Liste des symptômes
        vectorizer: Vectorizer existant (optionnel)
        train: Si True, entraîne un nouveau vectorizer
        
    Returns:
        Matrice vectorisée
    """
    if vectorizer is None:
        vectorizer = ShifaaVectorizer()
    
    if train:
        return vectorizer.fit_transform(symptoms)
    else:
        return vectorizer.transform(symptoms)

def get_vectorizer_info(vectorizer: ShifaaVectorizer) -> Dict[str, Any]:
    """
    Obtenir des informations sur le vectorizer
    
    Args:
        vectorizer: Vectorizer à analyser
        
    Returns:
        Dictionnaire d'informations
    """
    info = {
        'type': vectorizer.vectorizer_type,
        'is_fitted': vectorizer.is_fitted,
        'max_features': vectorizer.max_features,
        'ngram_range': vectorizer.ngram_range,
        'feature_count': len(vectorizer.feature_names) if vectorizer.is_fitted else 0,
        'use_svd': vectorizer.use_svd
    }
    
    if vectorizer.use_svd and vectorizer.svd:
        info['svd_components'] = vectorizer.svd.n_components
        info['svd_explained_variance'] = vectorizer.svd.explained_variance_ratio_.sum()
    
    return info

# =========================================================
# TESTS
# =========================================================

def test_vectorizer():
    """Tester le vectorizer"""
    
    print("\n" + "="*60)
    print("🧪 TEST DU VECTORIZER SHIFAAAI")
    print("="*60)
    
    # Données de test
    texts = [
        "fièvre toux fatigue",
        "mal de gorge douleur",
        "nausée vomissement diarrhée",
        "maux de tête intense",
        "douleur poitrine essoufflement"
    ]
    
    # Test avec TF-IDF
    print("\n📊 Test avec TF-IDF Vectorizer:")
    vectorizer_tfidf = ShifaaVectorizer(vectorizer_type='tfidf')
    X_tfidf = vectorizer_tfidf.fit_transform(texts)
    print(f"   Shape: {X_tfidf.shape}")
    print(f"   Features: {len(vectorizer_tfidf.feature_names)}")
    
    # Test avec Count Vectorizer
    print("\n📊 Test avec Count Vectorizer:")
    vectorizer_count = ShifaaVectorizer(vectorizer_type='count')
    X_count = vectorizer_count.fit_transform(texts)
    print(f"   Shape: {X_count.shape}")
    
    # Test avec SVD
    print("\n📊 Test avec TF-IDF + SVD:")
    vectorizer_svd = ShifaaVectorizer(vectorizer_type='tfidf', use_svd=True, svd_components=3)
    X_svd = vectorizer_svd.fit_transform(texts)
    print(f"   Shape: {X_svd.shape}")
    
    # Sauvegarde et chargement
    print("\n💾 Test de sauvegarde/chargement:")
    vectorizer_svd.save('models/test_vectorizer.pkl')
    loaded = ShifaaVectorizer.load('models/test_vectorizer.pkl')
    print(f"   Type chargé: {type(loaded).__name__}")
    print(f"   Features: {len(loaded.feature_names)}")
    
    # Information
    print("\n📋 Informations vectorizer:")
    info = get_vectorizer_info(vectorizer_tfidf)
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Feature importance
    print("\n⭐ Features importantes:")
    important = vectorizer_tfidf.get_feature_importance(5)
    for feat in important:
        print(f"   {feat['feature']}: {feat['score']:.3f}")

# =========================================================
# POINT D'ENTRÉE PRINCIPAL
# =========================================================

if __name__ == "__main__":
    test_vectorizer()
    
    print("\n" + "="*60)
    print("📦 UTILISATION DU VECTORIZER")
    print("="*60)
    print("""
    # Utilisation simple
    from vectorizer import ShifaaVectorizer
    
    vectorizer = ShifaaVectorizer()
    X = vectorizer.fit_transform(symptoms_list)
    
    # Sauvegarder
    vectorizer.save('models/vectorizer.pkl')
    
    # Charger
    vectorizer = ShifaaVectorizer.load('models/vectorizer.pkl')
    
    # Prédiction
    X_new = vectorizer.transform(new_symptoms)
    """)