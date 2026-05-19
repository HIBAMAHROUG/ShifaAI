"""Trains and evaluates lightweight text classifiers for medical symptoms."""

import pandas as pd
import numpy as np
import pickle
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

DATASET_PATH = "data/dataset.csv"
MODEL_DIR = "ai-model"
MODEL_PATH = os.path.join(MODEL_DIR, "shifaa_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

def preprocess_text(text):
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    stopwords = ['le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 
                 'donc', 'car', 'mais', 'est', 'sont', 'a', 'au', 'aux', 'avec', 
                 'sans', 'pour', 'par', 'dans', 'sur', 'chez', 'entre', 'je', 
                 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'ce', 'cette',
                 'ces', 'mon', 'ton', 'son', 'ma', 'ta', 'sa', 'mes', 'tes', 'ses']
    
    words = text.split()
    words = [w for w in words if w not in stopwords]
    
    return ' '.join(words)

def load_dataset():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found. Creating a default dataset...")
        create_default_dataset()
    
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset loaded: {len(df)} samples")
    print(f"Unique diseases: {df['disease'].nunique()}")
    print(f"Preview:\n{df.head()}")
    
    return df

def create_default_dataset():
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
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    print(f"Default dataset created: {DATASET_PATH}")

class ShifaaClassifier:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.vectorizer = None
        self.label_encoder = None
        self.trained = False
        
    def get_classifiers(self):
        return {
            'Naive Bayes': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                ('clf', MultinomialNB(alpha=0.5))
            ]),
            'Logistic Regression': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                ('clf', LogisticRegression(max_iter=1000, C=1.0))
            ]),
            'Random Forest': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
            ]),
            'SVM': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                ('clf', LinearSVC(max_iter=1000, C=1.0))
            ]),
            'Neural Network': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                ('clf', MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42))
            ]),
            'Gradient Boosting': Pipeline([
                ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000)),
                ('clf', GradientBoostingClassifier(n_estimators=100, random_state=42))
            ])
        }
    
    def train_all(self, X, y, test_size=0.2):
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )
        print("\n" + "="*60)
        print("MODEL TRAINING")
        print("="*60)
        
        results = []
        classifiers = self.get_classifiers()
        
        for name, model in classifiers.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                self.models[name] = model
                results.append({
                    'model': name,
                    'accuracy': accuracy,
                    'f1_score': f1
                })
                
                print(f"✅ {name:20} | Accuracy: {accuracy:.2%} | F1: {f1:.2%}")
                
            except Exception as e:
                print(f"❌ {name:20} | Erreur: {str(e)[:50]}")
        
        best = max(results, key=lambda x: x['accuracy'])
        self.best_model = self.models[best['model']]
        self.trained = True
        print("\n" + "="*60)
        print(f"Best model: {best['model']} (Accuracy: {best['accuracy']:.2%})")
        print("="*60)
        cv_scores = cross_val_score(self.best_model, X, y_encoded, cv=5)
        print(f"Cross-validation (5-fold): {cv_scores.mean():.2%} ± {cv_scores.std():.2%}")
        
        return best
    
    def train_single(self, X, y, model_name='Logistic Regression', test_size=0.2):
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )
        
        classifiers = self.get_classifiers()
        
        if model_name not in classifiers:
            raise ValueError(f"Modèle {model_name} non trouvé. Choisir parmi: {list(classifiers.keys())}")
        
        self.best_model = classifiers[model_name]
        self.best_model.fit(X_train, y_train)
        
        y_pred = self.best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Modèle {model_name} entraîné - Accuracy: {accuracy:.2%}")
        
        self.trained = True
        return accuracy
    
    def predict(self, symptoms_text, return_proba=False):
        """Prédire la maladie à partir des symptômes"""
        
        if not self.trained:
            raise ValueError("Le modèle n'est pas encore entraîné. Appelez train_all() d'abord.")
        
        # Prétraiter
        processed = preprocess_text(symptoms_text)
        
        # Prédiction
        prediction_encoded = self.best_model.predict([processed])[0]
        disease = self.label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Probabilités
        probabilities = None
        confidence = 0
        
        if hasattr(self.best_model.named_steps['clf'], 'predict_proba'):
            proba = self.best_model.predict_proba([processed])[0]
            confidence = max(proba) * 100
            probabilities = {
                self.label_encoder.inverse_transform([i])[0]: proba[i] * 100
                for i in range(len(proba))
                if proba[i] > 0.05
            }
        
        result = {
            "disease": disease,
            "confidence": round(confidence, 2) if confidence else 80.0,
            "probability": f"{confidence:.1f}%" if confidence else "N/A"
        }
        
        if return_proba and probabilities:
            # Trier par probabilité décroissante
            sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
            result["all_probabilities"] = sorted_probs[:5]
        
        return result
    
    def predict_proba_multiple(self, symptoms_text, top_n=3):
        """Retourner les top N prédictions avec probabilités"""
        
        if not self.trained:
            raise ValueError("Le modèle n'est pas encore entraîné.")
        
        processed = preprocess_text(symptoms_text)
        
        if hasattr(self.best_model.named_steps['clf'], 'predict_proba'):
            proba = self.best_model.predict_proba([processed])[0]
            
            # Obtenir les indices des top N probabilités
            top_indices = np.argsort(proba)[::-1][:top_n]
            
            predictions = []
            for idx in top_indices:
                disease = self.label_encoder.inverse_transform([idx])[0]
                predictions.append({
                    "disease": disease,
                    "confidence": round(proba[idx] * 100, 2),
                    "probability": f"{proba[idx] * 100:.1f}%"
                })
            
            return predictions
        
        # Fallback si predict_proba non disponible
        return [self.predict(symptoms_text)]
    
    def save(self, path=MODEL_PATH):
        """Sauvegarder le modèle"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.best_model,
                'label_encoder': self.label_encoder,
                'trained': self.trained
            }, f)
        
        print(f"✅ Modèle sauvegardé: {path}")
    
    def load(self, path=MODEL_PATH):
        """Charger un modèle sauvegardé"""
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.best_model = data['model']
            self.label_encoder = data['label_encoder']
            self.trained = data['trained']
            
            print(f"✅ Modèle chargé: {path}")
            return True
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
            return False

# =========================================================
# OPTIMISATION DES HYPERPARAMÈTRES
# =========================================================

def optimize_model(X_train, y_train):
    """Optimisation des hyperparamètres avec GridSearchCV"""
    
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', MultinomialNB())
    ])
    
    param_grid = {
        'tfidf__max_features': [1000, 3000, 5000, 10000],
        'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
        'tfidf__min_df': [1, 2],
        'clf__alpha': [0.1, 0.5, 1.0, 2.0]
    }
    
    grid_search = GridSearchCV(
        pipeline, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
    )
    
    grid_search.fit(X_train, y_train)
    
    print(f"🏆 Meilleurs paramètres: {grid_search.best_params_}")
    print(f"📊 Meilleur score: {grid_search.best_score_:.2%}")
    
    return grid_search.best_estimator_

# =========================================================
# MAIN
# =========================================================

def main():
    """Fonction principale"""
    
    print("\n" + "="*60)
    print("🏥 SHIFAAAI - MODÈLE DE CLASSIFICATION")
    print("="*60 + "\n")
    
    # Charger le dataset
    df = load_dataset()
    
    # Prétraiter les symptômes
    print("\n🔄 Prétraitement des données...")
    df['symptoms_clean'] = df['symptoms'].apply(preprocess_text)
    X = df['symptoms_clean']
    y = df['disease']
    
    print(f"✅ {len(X)} échantillons prétraités")
    
    # Créer et entraîner le classifieur
    classifier = ShifaaClassifier()
    
    # Essayer de charger un modèle existant
    if not classifier.load():
        # Entraîner tous les modèles
        best = classifier.train_all(X, y)
        
        # Sauvegarder le meilleur modèle
        classifier.save()
    
    # Tester avec des exemples
    print("\n" + "="*60)
    print("🧪 TESTS DE PRÉDICTION")
    print("="*60)
    
    test_examples = [
        "fièvre toux fatigue courbatures",
        "mal de gorge douleur gorge fièvre",
        "nausée vomissement diarrhée",
        "maux de tête intense sensibilité lumière",
        "toux sèche essoufflement respiration difficile"
    ]
    
    for symptoms in test_examples:
        result = classifier.predict(symptoms)
        print(f"\n🔍 '{symptoms}'")
        print(f"   → {result['disease']} (confiance: {result['confidence']:.1f}%)")
    
    # Exemple avec top 3 prédictions
    print("\n" + "="*60)
    print("📊 TOP 3 PRÉDICTIONS")
    print("="*60)
    
    symptoms = "fièvre toux fatigue perte goût"
    predictions = classifier.predict_proba_multiple(symptoms, top_n=3)
    
    print(f"\n🔍 '{symptoms}'")
    for i, pred in enumerate(predictions, 1):
        print(f"   {i}. {pred['disease']} ({pred['confidence']:.1f}%)")
    
    return classifier

# =========================================================
# API DE PRÉDICTION (INTÉGRATION AVEC FLASK)
# =========================================================

def create_prediction_api(classifier):
    """Créer une fonction de prédiction pour l'API Flask"""
    
    def predict_endpoint(symptoms_text, top_n=1):
        """
        Point d'entrée pour l'API
        Args:
            symptoms_text: Texte des symptômes
            top_n: Nombre de prédictions à retourner
        Returns:
            Dictionnaire avec les prédictions
        """
        if top_n > 1:
            predictions = classifier.predict_proba_multiple(symptoms_text, top_n=top_n)
            return {
                "success": True,
                "input_symptoms": symptoms_text,
                "predictions": predictions,
                "model": "shifaa-v2"
            }
        else:
            result = classifier.predict(symptoms_text)
            return {
                "success": True,
                "input_symptoms": symptoms_text,
                "prediction": result["disease"],
                "confidence": result["confidence"],
                "model": "shifaa-v2"
            }
    
    return predict_endpoint

# =========================================================
# EXÉCUTION
# =========================================================

if __name__ == "__main__":
    classifier = main()
    
    print("\n" + "="*60)
    print("✨ Modèle prêt à l'emploi!")
    print(f"📁 Modèle sauvegardé: {MODEL_PATH}")
    print("💡 Utilisez classifier.predict('vos symptômes')")
    print("="*60)
