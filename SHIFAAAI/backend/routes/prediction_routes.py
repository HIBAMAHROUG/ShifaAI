# prediction_routes.py - Routes de prédiction pour SHIFAAAI

from flask import request, jsonify, Blueprint
import json
import time
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
import re

# =========================================================
# IMPORTS DES MODULES
# =========================================================

try:
    from classifier_model import ShifaaClassifier
    from tokenizer_model import MedicalTokenizer
    from parser_model import MedicalTextParser
except ImportError as e:
    print(f"⚠️ Erreur d'importation: {e}")
    print("💡 Utilisation des versions simplifiées")
    
    class SimpleClassifier:
        def __init__(self):
            self.trained = True
        def load(self):
            return True
        def predict(self, text):
            words = text.lower().split()
            if 'fièvre' in words and 'toux' in words:
                return {'disease': 'Grippe', 'confidence': 85.0, 'probability': '85%'}
            elif 'gorge' in words:
                return {'disease': 'Angine', 'confidence': 70.0, 'probability': '70%'}
            elif 'nausée' in words or 'vomissement' in words:
                return {'disease': 'Gastro-entérite', 'confidence': 75.0, 'probability': '75%'}
            else:
                return {'disease': 'Non spécifié', 'confidence': 40.0, 'probability': '40%'}
        def predict_proba_multiple(self, text, top_n=3):
            main = self.predict(text)
            alternatives = []
            if main['disease'] == 'Grippe':
                alternatives = [{'disease': 'COVID-19', 'confidence': 45.0}, {'disease': 'Rhume', 'confidence': 30.0}]
            elif main['disease'] == 'Angine':
                alternatives = [{'disease': 'Pharyngite', 'confidence': 40.0}, {'disease': 'Laryngite', 'confidence': 25.0}]
            return [main] + alternatives[:top_n-1]
    
    ShifaaClassifier = SimpleClassifier
    MedicalTokenizer = None
    MedicalTextParser = None

# =========================================================
# CONFIGURATION
# =========================================================

prediction_bp = Blueprint('prediction', __name__, url_prefix='/api/predict')

DB_PATH = "shifaa.db"

# Initialiser les modèles
classifier = ShifaaClassifier()
classifier.load()  # Charger le modèle s'il existe

tokenizer = MedicalTokenizer() if MedicalTokenizer else None
parser = MedicalTextParser() if MedicalTextParser else None

# =========================================================
# BASE DE DONNÉES
# =========================================================

def get_db():
    """Établir une connexion à la base de données"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"❌ Erreur connexion DB: {e}")
        return None

def save_prediction(text: str, result: Dict[str, Any]) -> int:
    """Sauvegarder une prédiction dans la base de données"""
    conn = get_db()
    if not conn:
        return -1
    
    try:
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT,
                predicted_disease TEXT,
                confidence_score REAL,
                all_predictions TEXT,
                processing_time_ms INTEGER,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO predictions (input_text, predicted_disease, confidence_score, all_predictions, processing_time_ms)
            VALUES (?, ?, ?, ?, ?)
        """, (
            text[:500],
            result.get('disease', 'Unknown'),
            result.get('confidence', 0),
            json.dumps(result.get('all_predictions', [])),
            result.get('processing_time_ms', 0)
        ))
        
        conn.commit()
        return cursor.lastrowid
        
    except sqlite3.Error as e:
        print(f"❌ Erreur sauvegarde: {e}")
        return -1
    finally:
        conn.close()

def get_prediction_history(limit: int = 50) -> List[Dict]:
    """Récupérer l'historique des prédictions"""
    conn = get_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, input_text, predicted_disease, confidence_score, created_at
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    except sqlite3.Error as e:
        print(f"❌ Erreur historique: {e}")
        return []
    finally:
        conn.close()

# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================

def preprocess_input(text: str) -> str:
    """Prétraiter le texte d'entrée"""
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    # Supprimer la ponctuation excessive
    text = re.sub(r'[^\w\s]', ' ', text)
    return text.strip()

def validate_symptoms(text: str) -> Dict[str, Any]:
    """Valider et analyser les symptômes d'entrée"""
    if not text or len(text) < 3:
        return {"valid": False, "error": "Texte trop court (minimum 3 caractères)"}
    
    if len(text) > 1000:
        return {"valid": False, "error": "Texte trop long (maximum 1000 caractères)"}
    
    # Vérifier les mots-clés minimum
    medical_keywords = ['fièvre', 'toux', 'douleur', 'fatigue', 'gorge', 'nausée', 
                        'vomissement', 'diarrhée', 'mal', 'maux']
    
    text_lower = text.lower()
    found_keywords = [kw for kw in medical_keywords if kw in text_lower]
    
    if not found_keywords:
        return {"valid": False, "error": "Aucun symptôme médical détecté", "warning": True}
    
    return {"valid": True, "detected_keywords": found_keywords}

# =========================================================
# ROUTES DE PRÉDICTION
# =========================================================

@prediction_bp.route('/', methods=['POST'])
def predict():
    """
    Prédiction principale
    POST /api/predict/
    Body: {"text": "symptômes", "top_n": 3, "save": true}
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Récupérer le texte
        text = data.get('text', '') or data.get('symptoms', '')
        if not text:
            return jsonify({"error": "No symptoms provided"}), 400
        
        # Prétraiter
        text = preprocess_input(text)
        
        # Valider
        validation = validate_symptoms(text)
        if not validation["valid"]:
            return jsonify({
                "success": False,
                "error": validation.get("error", "Invalid input"),
                "warning": validation.get("warning", False)
            }), 400
        
        # Paramètres
        top_n = data.get('top_n', 3)
        top_n = min(max(top_n, 1), 5)
        save_result = data.get('save', True)
        
        # Prédiction
        predictions = classifier.predict_proba_multiple(text, top_n=top_n)
        main_prediction = predictions[0] if predictions else {"disease": "Non déterminé", "confidence": 0}
        
        # Calculer le score de confiance global
        confidence_score = main_prediction.get('confidence', 0)
        confidence_level = "élevé" if confidence_score >= 70 else "moyen" if confidence_score >= 40 else "faible"
        
        # Déterminer si consultation nécessaire
        urgent_diseases = ['COVID-19', 'Pneumonie', 'Appendicite', 'Méningite', 'Problème cardiaque']
        requires_consultation = main_prediction.get('disease') in urgent_diseases or confidence_score > 80
        
        # Générer des recommandations
        recommendations = generate_recommendations(main_prediction, validation.get('detected_keywords', []))
        
        processing_time = (time.time() - start_time) * 1000
        
        # Préparer la réponse
        response = {
            "success": True,
            "input_text": text,
            "detected_keywords": validation.get('detected_keywords', []),
            "predictions": predictions,
            "top_prediction": {
                "disease": main_prediction.get('disease'),
                "confidence": main_prediction.get('confidence'),
                "probability": main_prediction.get('probability', f"{main_prediction.get('confidence', 0)}%"),
                "risk_level": get_risk_level(main_prediction.get('disease')),
                "requires_consultation": requires_consultation
            },
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "recommendations": recommendations,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "model_version": "shifaa-v2.0",
            "disclaimer": "⚠️ Ceci est une analyse assistée par IA. Ne remplace pas un avis médical professionnel."
        }
        
        # Sauvegarder en base
        analysis_id = None
        if save_result:
            response['processing_time_ms'] = round(processing_time, 2)
            analysis_id = save_prediction(text, {
                "disease": main_prediction.get('disease'),
                "confidence": confidence_score,
                "all_predictions": predictions,
                "processing_time_ms": round(processing_time, 2)
            })
        
        if analysis_id and analysis_id > 0:
            response["analysis_id"] = analysis_id
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": "prediction_error"
        }), 500


@prediction_bp.route('/batch', methods=['POST'])
def predict_batch():
    """
    Prédiction par lots
    POST /api/predict/batch
    Body: {"texts": ["symptômes1", "symptômes2", ...], "top_n": 1}
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        texts = data.get('texts', [])
        if not texts or not isinstance(texts, list):
            return jsonify({"error": "Invalid texts array"}), 400
        
        top_n = data.get('top_n', 1)
        top_n = min(max(top_n, 1), 3)
        
        results = []
        for i, text in enumerate(texts):
            try:
                text = preprocess_input(text)
                predictions = classifier.predict_proba_multiple(text, top_n=top_n)
                
                results.append({
                    "index": i,
                    "text": text[:200],
                    "success": True,
                    "top_prediction": predictions[0] if predictions else None,
                    "all_predictions": predictions
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "text": text[:100],
                    "success": False,
                    "error": str(e)
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            "success": True,
            "total": len(texts),
            "successful": sum(1 for r in results if r['success']),
            "results": results,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": "batch_prediction_error"
        }), 500


@prediction_bp.route('/history', methods=['GET'])
def prediction_history():
    """
    Récupérer l'historique des prédictions
    GET /api/predict/history?limit=50
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Max 100
        
        history = get_prediction_history(limit)
        
        return jsonify({
            "success": True,
            "total": len(history),
            "history": history,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@prediction_bp.route('/history/<int:analysis_id>', methods=['GET'])
def get_prediction_by_id(analysis_id: int):
    """
    Récupérer une prédiction spécifique
    GET /api/predict/history/123
    """
    conn = get_db()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, input_text, predicted_disease, confidence_score, all_predictions, created_at
            FROM predictions
            WHERE id = ?
        """, (analysis_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"error": "Prediction not found"}), 404
        
        return jsonify({
            "success": True,
            "id": row[0],
            "input_text": row[1],
            "predicted_disease": row[2],
            "confidence_score": row[3],
            "all_predictions": json.loads(row[4]) if row[4] else [],
            "created_at": row[5]
        }), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@prediction_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Soumettre un feedback sur une prédiction
    POST /api/predict/feedback
    Body: {"prediction_id": 123, "helpful": true, "correct_disease": "Grippe", "comment": "..."}
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        prediction_id = data.get('prediction_id')
        helpful = data.get('helpful', False)
        correct_disease = data.get('correct_disease')
        comment = data.get('comment', '')
        
        if not prediction_id:
            return jsonify({"error": "prediction_id required"}), 400
        
        conn = get_db()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()
        
        # Créer la table de feedback si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                helpful BOOLEAN,
                correct_disease TEXT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        """)
        
        cursor.execute("""
            INSERT INTO feedback (prediction_id, helpful, correct_disease, comment)
            VALUES (?, ?, ?, ?)
        """, (prediction_id, helpful, correct_disease, comment))
        
        conn.commit()
        
        return jsonify({
            "success": True,
            "message": "Feedback enregistré avec succès",
            "feedback_id": cursor.lastrowid
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@prediction_bp.route('/diseases', methods=['GET'])
def list_diseases():
    """
    Lister toutes les maladies que le modèle peut prédire
    GET /api/predict/diseases
    """
    diseases = [
        {"id": 1, "name": "Grippe", "risk_level": "modéré", "common_symptoms": ["fièvre", "toux", "fatigue"]},
        {"id": 2, "name": "COVID-19", "risk_level": "élevé", "common_symptoms": ["fièvre", "toux", "perte goût", "perte odorat"]},
        {"id": 3, "name": "Angine", "risk_level": "faible", "common_symptoms": ["mal de gorge", "douleur gorge", "fièvre"]},
        {"id": 4, "name": "Gastro-entérite", "risk_level": "modéré", "common_symptoms": ["nausée", "vomissement", "diarrhée"]},
        {"id": 5, "name": "Bronchite", "risk_level": "modéré", "common_symptoms": ["toux", "expectoration", "fatigue"]},
        {"id": 6, "name": "Migraine", "risk_level": "modéré", "common_symptoms": ["maux de tête", "nausée", "sensibilité lumière"]},
        {"id": 7, "name": "Rhume", "risk_level": "faible", "common_symptoms": ["nez congestionné", "éternuement", "gorge irritée"]},
        {"id": 8, "name": "Pneumonie", "risk_level": "critique", "common_symptoms": ["fièvre élevée", "toux", "douleur poitrine"]},
        {"id": 9, "name": "Infection urinaire", "risk_level": "faible", "common_symptoms": ["brulure en urinant", "urination fréquente"]},
        {"id": 10, "name": "Allergie", "risk_level": "faible", "common_symptoms": ["nez congestionné", "éternuement", "démangeaison"]}
    ]
    
    return jsonify({
        "success": True,
        "total": len(diseases),
        "diseases": diseases
    }), 200


@prediction_bp.route('/stats', methods=['GET'])
def prediction_stats():
    """
    Statistiques des prédictions
    GET /api/predict/stats
    """
    conn = get_db()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Total des prédictions
        cursor.execute("SELECT COUNT(*) FROM predictions")
        total = cursor.fetchone()[0]
        
        # Prédictions par maladie
        cursor.execute("""
            SELECT predicted_disease, COUNT(*) as count
            FROM predictions
            GROUP BY predicted_disease
            ORDER BY count DESC
            LIMIT 10
        """)
        by_disease = [{"disease": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Confidence moyenne
        cursor.execute("SELECT AVG(confidence_score) FROM predictions")
        avg_confidence = cursor.fetchone()[0] or 0
        
        # Prédictions aujourd'hui
        cursor.execute("""
            SELECT COUNT(*) FROM predictions
            WHERE DATE(created_at) = DATE('now')
        """)
        today = cursor.fetchone()[0]
        
        return jsonify({
            "success": True,
            "stats": {
                "total_predictions": total,
                "today_predictions": today,
                "average_confidence": round(avg_confidence, 2),
                "most_common_diseases": by_disease[:5]
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================

def get_risk_level(disease: str) -> str:
    """Déterminer le niveau de risque d'une maladie"""
    risk_levels = {
        "Grippe": "modéré",
        "COVID-19": "élevé",
        "Angine": "faible",
        "Gastro-entérite": "modéré",
        "Bronchite": "modéré",
        "Migraine": "modéré",
        "Rhume": "faible",
        "Pneumonie": "critique",
        "Infection urinaire": "faible",
        "Allergie": "faible"
    }
    return risk_levels.get(disease, "indéterminé")

def generate_recommendations(prediction: Dict[str, Any], symptoms: List[str]) -> List[str]:
    """Générer des recommandations personnalisées"""
    recommendations = []
    
    disease = prediction.get('disease', '')
    confidence = prediction.get('confidence', 0)
    
    # Recommandations générales
    recommendations.append("📝 Surveillez l'évolution de vos symptômes")
    recommendations.append("💧 Restez hydraté(e) et reposez-vous")
    
    # Recommandations basées sur la maladie
    if disease == "Grippe":
        recommendations.append("🌡️ Prenez votre température régulièrement")
        recommendations.append("🍯 Le miel peut aider pour la toux")
    elif disease == "COVID-19":
        recommendations.append("🏠 Isolez-vous immédiatement")
        recommendations.append("🧪 Faites un test PCR")
        recommendations.append("👨‍⚕️ Consultez un médecin rapidement")
    elif disease == "Angine":
        recommendations.append("🥤 Buvez des boissons chaudes")
        recommendations.append("🧂 Gargarismes à l'eau salée")
    elif disease == "Gastro-entérite":
        recommendations.append("💧 Hydratation essentielle (solutions de réhydratation)")
        recommendations.append("🍚 Régime sans lactose, riz, banane")
    elif disease == "Pneumonie":
        recommendations.append("🚨 Consultation médicale URGENTE")
        recommendations.append("📞 Appelez le 15 si difficultés respiratoires")
    
    # Recommandations basées sur les symptômes
    if 'fièvre' in symptoms:
        recommendations.append("🌡️ Surveillez votre température 2 fois par jour")
    if 'toux' in symptoms:
        recommendations.append("🍯 Le miel peut apaiser la toux")
    if 'fatigue' in symptoms:
        recommendations.append("🛌 Reposez-vous et écoutez votre corps")
    
    # Recommandation de consultation
    if confidence < 50:
        recommendations.append("🔍 Contactez un médecin pour plus de précision")
    elif disease in ["COVID-19", "Pneumonie", "Appendicite"]:
        recommendations.append("🏥 Consultation médicale recommandée")
    
    return recommendations[:6]


# =========================================================
# INITIALISATION
# =========================================================

def register_prediction_routes(app):
    """Enregistrer les routes de prédiction dans l'application Flask"""
    app.register_blueprint(prediction_bp)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    register_prediction_routes(app)
    
    print("\n" + "="*60)
    print("🔮 SHIFAAAI - PREDICTION API")
    print("="*60)
    print("📋 Routes disponibles:")
    print("   POST /api/predict/              - Prédiction simple")
    print("   POST /api/predict/batch         - Prédiction par lots")
    print("   GET  /api/predict/history       - Historique")
    print("   GET  /api/predict/history/<id>  - Détail prédiction")
    print("   POST /api/predict/feedback      - Feedback utilisateur")
    print("   GET  /api/predict/diseases      - Liste des maladies")
    print("   GET  /api/predict/stats         - Statistiques")
    print("="*60 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)
