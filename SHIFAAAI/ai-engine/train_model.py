# train_simple.py - Version sans pandas

import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

def train_model():
    print("🚀 Entraînement du modèle SHIFAAI (version simple)...")
    
    # Données d'entraînement
    symptoms = [
        "fiévre toux fatigue", "fiévre toux perte goût", "mal gorge douleur gorge",
        "fatigue maux tête", "toux sèche respiration difficile", "fiévre frissons sueurs",
        "nausée vomissement diarrhée", "fatigue vertige", "maux tête vision floue"
    ]
    
    diseases = [
        "Grippe", "COVID-19", "Angine", "Migraine", "Asthme", 
        "Infection virale", "Gastro-entérite", "Anémie", "Hypertension"
    ]
    
    # Encodage
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(diseases)
    
    # Vectorisation
    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
    X_vectorized = vectorizer.fit_transform(symptoms)
    
    # Modèle
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vectorized, y_encoded)
    
    # Sauvegarde
    os.makedirs('models', exist_ok=True)
    
    model_data = {
        'model': model,
        'vectorizer': vectorizer,
        'label_encoder': label_encoder,
        'classes': label_encoder.classes_.tolist(),
        'training_date': datetime.now().isoformat()
    }
    
    with open('models/shifaa_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
    
    print("✅ Modèle sauvegardé: models/shifaa_model.pkl")

if __name__ == "__main__":
    train_model()