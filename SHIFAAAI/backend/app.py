"""Handles medical analysis routes, NLP predictions, and external API enrichment."""

from flask import Flask, jsonify, request
from flask_cors import CORS
from medical_apis import MedicalAPIs
from infermedica_api import InfermedicaClient
import unicodedata
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

PORT = 5000
HOST = '127.0.0.1'

INFERMEDICA_APP_ID = os.getenv('INFERMEDICA_APP_ID', 'votre_app_id')
INFERMEDICA_APP_KEY = os.getenv('INFERMEDICA_APP_KEY', 'votre_app_key')

try:
    infermedica_client = InfermedicaClient(INFERMEDICA_APP_ID, INFERMEDICA_APP_KEY)
    print("✅ Client Infermedica initialisé")
except Exception as e:
    infermedica_client = None
    print(f"⚠️ Erreur initialisation Infermedica: {e}")

DISEASE_DATABASE = {
    "Grippe": {
        "keywords": ["fievre", "fièvre", "toux", "fatigue", "courbature", "frisson"],
        "severity": "modéré", "treatment": "Repos, hydratation, paracétamol"
    },
    "COVID-19": {
        "keywords": ["fievre", "fièvre", "toux", "fatigue", "perte gout", "perte odorat", "anosmie", "agueusie", "covid"],
        "severity": "élevé", "treatment": "Isolement, repos, consultation médicale"
    },
    "Bronchite": {
        "keywords": ["toux", "expectoration", "glaires", "poitrine", "respiration", "essoufflement", "bronchite"],
        "severity": "modéré", "treatment": "Repos, bronchodilatateurs, hydratation"
    },
    "Pneumonie": {
        "keywords": ["poumon", "infection poumon", "fievre elevee", "toux grasse", "crachat sang"],
        "severity": "critique", "treatment": "URGENCE - Consultation médicale immédiate"
    },
    "Asthme": {
        "keywords": ["respiration sifflante", "sifflement", "crise asthme", "ventoline", "oppression thoracique"],
        "severity": "modéré", "treatment": "Bronchodilatateurs, consultation pneumologue"
    },
    
    "Angine": {
        "keywords": ["gorge", "mal gorge", "douleur gorge", "avaler", "amygdale"],
        "severity": "faible", "treatment": "Gargarismes, boissons chaudes, paracétamol"
    },
    "Rhinite allergique": {
        "keywords": ["nez", "éternuement", "gratte", "pollin", "allergie"],
        "severity": "faible", "treatment": "Antihistaminiques, éviter allergènes"
    },
    "Otite": {
        "keywords": ["oreille", "douleur oreille", "infection oreille", "otite"],
        "severity": "faible", "treatment": "Consulter ORL, antalgiques"
    },
    "Sinusite": {
        "keywords": ["sinus", "nez bouché", "douleur visage", "sinusite"],
        "severity": "faible", "treatment": "Lavage nez, décongestionnants"
    },
    
    "Migraine": {
        "keywords": ["migraine", "mal tete", "cephalee", "tete", "lumiere", "bruit", "nausee", "aura"],
        "severity": "modéré", "treatment": "Repos obscurité, antimigraineux"
    },
    "Céphalée de tension": {
        "keywords": ["tension tete", "mal tete permanent", "stress tete"],
        "severity": "faible", "treatment": "Repos, relaxation, antalgiques"
    },
    "Vertige positionnel": {
        "keywords": ["vertige", "tete tourne", "etourdissement", "perte equilibre"],
        "severity": "modéré", "treatment": "Kinésithérapie vestibulaire"
    },
    
    "Gastro-entérite": {
        "keywords": ["nausee", "vomissement", "diarrhee", "ventre", "gastro"],
        "severity": "modéré", "treatment": "Hydratation, repos, régime sans lactose"
    },
    "Gastrite": {
        "keywords": ["estomac", "brulure estomac", "acidite", "gastrite"],
        "severity": "faible", "treatment": "Anti-acides, éviter aliments gras"
    },
    "Constipation": {
        "keywords": ["constipation", "selles dures", "difficulte aller selle"],
        "severity": "faible", "treatment": "Fibres, hydratation, activité physique"
    },
    
    "Problème cardiaque": {
        "keywords": ["coeur", "palpitation", "douleur poitrine", "cardiaque", "infarctus", "angine poitrine", "tachycardie"],
        "severity": "critique", "treatment": "URGENCE - Consulter immédiatement"
    },
    "Hypertension": {
        "keywords": ["tension", "pression arterielle", "hypertension", "tension elevee"],
        "severity": "modéré", "treatment": "Consultation cardiologue, régime sans sel"
    },
    
    "Arthrose": {
        "keywords": ["articulation", "genou", "hanche", "arthrose", "raideur matin"],
        "severity": "modéré", "treatment": "Physiothérapie, antalgiques"
    },
    "Lombalgie": {
        "keywords": ["lombaire", "dos", "mal dos", "lombalgie", "sciatique"],
        "severity": "modéré", "treatment": "Repos, kinésithérapie"
    },
    
    "Eczéma": {
        "keywords": ["peau", "demangeaison", "rougeur", "eczema", "plaque rouge"],
        "severity": "faible", "treatment": "Crèmes hydratantes, corticoïdes"
    },
    "Urticaire": {
        "keywords": ["bouton", "urticaire", "allergie peau", "plaque"],
        "severity": "faible", "treatment": "Antihistaminiques"
    },
    
    "Dépression": {
        "keywords": ["tristesse", "deprime", "moral bas", "perte plaisir", "fatigue morale"],
        "severity": "modéré", "treatment": "Consulter psychologue/psychiatre"
    },
    "Anxiété": {
        "keywords": ["stress", "anxiete", "angoisse", "panique", "nerveux"],
        "severity": "modéré", "treatment": "Relaxation, consultation psychologue"
    }
}

def normalize_text(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize('NFD', text).encode('ASCII', 'ignore').decode('utf-8')
    return text

def extract_symptoms(text: str) -> list:
    normalized = normalize_text(text)
    all_keywords = []
    
    for disease, info in DISEASE_DATABASE.items():
        for keyword in info['keywords']:
            if keyword in normalized:
                all_keywords.append(keyword)
    
    common_symptoms = {
        'fievre': 'fièvre', 'toux': 'toux', 'fatigue': 'fatigue',
        'courbature': 'courbatures', 'frisson': 'frissons', 'gorge': 'mal de gorge',
        'nausee': 'nausée', 'vomissement': 'vomissement', 'diarrhee': 'diarrhée',
        'essoufflement': 'essoufflement', 'poitrine': 'douleur poitrine',
        'migraine': 'migraine', 'vertige': 'vertige', 'palpitation': 'palpitations'
    }
    
    detected = []
    for key, symptom in common_symptoms.items():
        if key in normalized:
            detected.append(symptom)
    
    return list(set(detected + all_keywords))

def predict_diseases(symptoms: list) -> list:
    scores = {}
    
    for disease, info in DISEASE_DATABASE.items():
        score = 0
        max_possible = len(info['keywords'])
        
        for sym in symptoms:
            for keyword in info['keywords']:
                if sym == keyword or keyword in sym or sym in keyword:
                    score += 1
                    break
        
        if max_possible > 0:
            probability = (score / max_possible) * 100
            if probability > 15:
                scores[disease] = {
                    "probability": round(probability),
                    "severity": info['severity'],
                    "treatment": info['treatment']
                }
    
    sorted_diseases = sorted(scores.items(), key=lambda x: x[1]['probability'], reverse=True)
    
    results = []
    for disease, info in sorted_diseases[:5]:
        results.append({
            "disease": disease,
            "probability": info['probability'],
            "severity": info['severity'],
            "treatment": info['treatment']
        })
    
    return results

def tokenize_text(text: str) -> list:
    words = text.split()
    tokens = []
    
    for word in words:
        clean_word = word.lower().strip('.,;:!?')
        token_type = "WORD"
        
        for disease, info in DISEASE_DATABASE.items():
            for keyword in info['keywords']:
                if keyword in clean_word:
                    token_type = "SYMPTOM"
                    break
            if token_type == "SYMPTOM":
                break
        
        if clean_word in ['pas', 'ne', 'non', 'jamais', 'plus', 'aucun']:
            token_type = "NEGATION"
        
        if clean_word in ['très', 'beaucoup', 'extremement', 'trop', 'fort', 'intense']:
            token_type = "INTENSIFIER"
        
        tokens.append({"word": word, "type": token_type})
    
    return tokens

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "ShifaaAI Medical API",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get('text') or '').strip()
        
        if not text:
            return jsonify({"error": "Aucun symptôme fourni"}), 400
        
        symptoms = extract_symptoms(text)
        predictions = predict_diseases(symptoms)
        tokens = tokenize_text(text)
        
        external_info = {}
        if predictions:
            top_disease = predictions[0]['disease']
            mesh_result = MedicalAPIs.search_mesh_term(top_disease)
            if mesh_result.get('success'):
                external_info['mesh'] = mesh_result['data']
        
        return jsonify({
            "success": True,
            "text": text,
            "tokens": tokens,
            "symptoms_detected": symptoms,
            "predictions": predictions,
            "top_prediction": predictions[0] if predictions else {"disease": "Non déterminé", "probability": 20},
            "external_info": external_info,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/external/disease-info', methods=['POST'])
def external_disease_info():
    data = request.get_json(silent=True) or {}
    disease_name = (data.get('disease') or '').strip()

    if not disease_name:
        return jsonify({"success": False, "error": "Le nom de la maladie est requis"}), 400
    
    result = MedicalAPIs.search_disease(disease_name)
    return jsonify(result)

@app.route('/api/infermedica/parse', methods=['POST'])
def infermedica_parse():
    if not infermedica_client:
        return jsonify({"error": "Client Infermedica non configuré"}), 500
    
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get('text') or '').strip()
        if not text:
            return jsonify({"error": "Le texte à analyser est requis"}), 400

        try:
            age = int(data.get('age', 30))
        except (TypeError, ValueError):
            age = 30

        sex = str(data.get('sex', 'male')).strip().lower()
        if sex not in {'male', 'female'}:
            sex = 'male'

        parsed = infermedica_client.parse_symptoms(text)
        
        diagnosis = None
        if parsed.get('mentions'):
            symptoms = parsed['mentions']
            diagnosis = infermedica_client.get_diagnosis(symptoms, age, sex)
        
        return jsonify({
            "success": True,
            "parsed_symptoms": parsed,
            "diagnosis": diagnosis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/external/drug-info', methods=['POST'])
def external_drug_info():
    data = request.get_json(silent=True) or {}
    drug_name = (data.get('drug') or '').strip()

    if not drug_name:
        return jsonify({"success": False, "error": "Le nom du médicament est requis"}), 400
    
    result = MedicalAPIs.search_drug(drug_name)
    return jsonify(result)

@app.route('/api/symptoms-list', methods=['GET'])
def get_symptoms_list():
    all_symptoms = set()
    for disease, info in DISEASE_DATABASE.items():
        for keyword in info['keywords']:
            all_symptoms.add(keyword)
    
    return jsonify({
        "symptoms": sorted(list(all_symptoms)),
        "count": len(all_symptoms)
    })

@app.route('/api/diseases-list', methods=['GET'])
def get_diseases_list():
    return jsonify({
        "diseases": list(DISEASE_DATABASE.keys()),
        "count": len(DISEASE_DATABASE)
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 SHIFAAAI MEDICAL API v3.0")
    print("="*60)
    print(f"🌐 Serveur: http://{HOST}:{PORT}")
    print("📋 Endpoints disponibles:")
    print("   POST /api/analyze              - Analyse médicale")
    print("   GET  /api/symptoms-list        - Liste des symptômes")
    print("   GET  /api/diseases-list        - Liste des maladies")
    print("   POST /api/external/disease-info - Infos maladie (Disease Ontology)")
    print("   POST /api/external/drug-info    - Infos médicament (OpenFDA)")
    print("="*60 + "\n")
    app.run(host=HOST, port=PORT, debug=True)