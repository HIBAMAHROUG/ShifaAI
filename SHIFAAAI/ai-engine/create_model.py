# create_model.py - Script pour créer et sauvegarder le modèle

import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
import os

# =========================================================
# CRÉATION DU MODÈLE
# =========================================================

def create_model():
    """Créer et sauvegarder le modèle SHIFAAAI"""
    
    print("\n" + "="*60)
    print("🔧 CRÉATION DU MODÈLE SHIFAAAI")
    print("="*60)
    
    # Données d'entraînement
    data = {
        "symptoms": [
            "fièvre toux fatigue", "fièvre toux perte goût", "mal gorge douleur gorge",
            "fatigue maux tête", "toux sèche respiration difficile", "fièvre frissons sueurs",
            "douleur poitrine essoufflement", "nausée vomissement diarrhée", "fatigue vertige",
            "maux tête vision floue", "toux fièvre douleur poitrine", "fièvre douleur articulaire",
            "fatigue perte poids", "toux chronique", "fièvre éruption cutanée",
            "douleur abdomen nausée", "insomnie stress fatigue", "fièvre douleur oreille",
            "vertige nausée perte équilibre", "fièvre toux maux gorge fatigue"
        ],
        "disease": [
            "Grippe", "COVID-19", "Angine", "Migraine", "Asthme", "Infection virale",
            "Problème cardiaque", "Gastro-entérite", "Anémie", "Hypertension", "Pneumonie",
            "Dengue", "Diabète", "Bronchite", "Allergie", "Appendicite", "Anxiété", "Otite",
            "Vertige positionnel", "Grippe sévère"
        ]
    }
    
    df = pd.DataFrame(data)
    
    print(f"📊 Données: {len(df)} échantillons, {df['disease'].nunique()} maladies")
    
    # Vectorizer TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=1
    )
    
    # Encoder les labels
    label_encoder = LabelEncoder()
    
    # Préparer les données
    X = vectorizer.fit_transform(df['symptoms'])
    y = label_encoder.fit_transform(df['disease'])
    
    # Modèle (Random Forest)
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        random_state=42
    )
    
    print("\n🚀 Entraînement du modèle...")
    model.fit(X, y)
    
    print(f"✅ Modèle entraîné avec succès")
    print(f"   Accuracy entraînement: {model.score(X, y):.2%}")
    
    # Créer le pipeline complet
    pipeline = {
        'vectorizer': vectorizer,
        'model': model,
        'label_encoder': label_encoder,
        'classes': label_encoder.classes_.tolist(),
        'metadata': {
            'version': '2.0.0',
            'training_date': '2024-01-15',
            'model_type': 'RandomForestClassifier',
            'num_classes': len(label_encoder.classes_),
            'num_features': X.shape[1]
        }
    }
    
    # Sauvegarder
    os.makedirs('models', exist_ok=True)
    with open('models/model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    print("\n💾 Modèle sauvegardé: models/model.pkl")
    
    return pipeline

# =========================================================
# TEST DU MODÈLE
# =========================================================

def test_model():
    """Tester le modèle sauvegardé"""
    
    print("\n" + "="*60)
    print("🧪 TEST DU MODÈLE")
    print("="*60)
    
    # Charger le modèle
    with open('models/model.pkl', 'rb') as f:
        pipeline = pickle.load(f)
    
    vectorizer = pipeline['vectorizer']
    model = pipeline['model']
    label_encoder = pipeline['label_encoder']
    
    # Tester avec différents symptômes
    test_cases = [
        ("fièvre toux fatigue", "Grippe"),
        ("mal de gorge", "Angine"),
        ("nausée vomissement", "Gastro-entérite"),
        ("maux de tête intense", "Migraine"),
        ("toux sèche essoufflement", "Asthme")
    ]
    
    print("\n📋 Tests de prédiction:")
    print("-" * 50)
    
    for symptoms, expected in test_cases:
        X_test = vectorizer.transform([symptoms])
        pred_encoded = model.predict(X_test)[0]
        pred = label_encoder.inverse_transform([pred_encoded])[0]
        
        # Probabilités
        proba = model.predict_proba(X_test)[0]
        confidence = max(proba) * 100
        
        status = "✅" if pred == expected else "⚠️"
        print(f"{status} Symptômes: '{symptoms}'")
        print(f"   Prédiction: {pred} (confiance: {confidence:.1f}%)")
        print(f"   Attendu: {expected}")
        print()

if __name__ == "__main__":
    create_model()
    test_model()