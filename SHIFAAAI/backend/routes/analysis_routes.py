"""Defines analysis routes for tokenization, parsing, and classification."""

from flask import request, jsonify, Blueprint
import json
import time
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from tokenizer_model import MedicalTokenizer, AdvancedMedicalTokenizer
    from parser_model import MedicalTextParser, AdvancedMedicalParser, parse_symptoms
    from classifier_model import ShifaaClassifier
except ImportError as e:
    print(f"Import error: {e}")
    print("Using simplified fallbacks")

    class SimpleTokenizer:
        def tokenize(self, text):
            tokens = text.lower().split()
            return type('obj', (object,), {
                'tokens': [type('obj', (object,), {'text': t, 'type': 'word'}) for t in tokens],
                'num_tokens': len(tokens),
                'num_medical_terms': 0,
                'num_symptoms': 0,
                'medical_terms': [],
                'symptoms_list': [],
                'processing_time_ms': 0
            })
    
    MedicalTokenizer = SimpleTokenizer
    AdvancedMedicalTokenizer = SimpleTokenizer
    MedicalTextParser = None
    AdvancedMedicalParser = None
    
    class SimpleClassifier:
        def load(self):
            return True
        def predict(self, text):
            words = text.lower().split()
            if 'fièvre' in words and 'toux' in words:
                return {'disease': 'Grippe', 'confidence': 85.0}
            elif 'gorge' in words:
                return {'disease': 'Angine', 'confidence': 70.0}
            else:
                return {'disease': 'Non spécifié', 'confidence': 40.0}
        def predict_proba_multiple(self, text, top_n=3):
            return [self.predict(text)]
    
    ShifaaClassifier = SimpleClassifier

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

tokenizer = MedicalTokenizer()
advanced_tokenizer = AdvancedMedicalTokenizer() if hasattr(MedicalTokenizer, 'tokenize_advanced') else None

parser = MedicalTextParser() if MedicalTextParser else None
advanced_parser = AdvancedMedicalParser() if AdvancedMedicalParser else None

classifier = ShifaaClassifier()
classifier.load()

@analysis_bp.route('/tokenize', methods=['POST'])
def tokenize_endpoint():
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        advanced = data.get('advanced', False)
        
        if advanced and advanced_tokenizer:
            result = advanced_tokenizer.tokenize_advanced(text)
        else:
            result = tokenizer.tokenize(text)
            result = result.__dict__ if hasattr(result, '__dict__') else result
        
        if 'basic' in result:
            tokens_json = result['basic']['tokens']
            if hasattr(tokens_json[0], '__dict__') if tokens_json else False:
                tokens_json = [t.__dict__ for t in tokens_json]
        else:
            tokens_json = result.get('tokens', [])
            if tokens_json and hasattr(tokens_json[0], '__dict__'):
                tokens_json = [t.__dict__ for t in tokens_json]
            result = {k: v for k, v in result.items() if not k.startswith('_')}
            result['tokens'] = tokens_json
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            "success": True,
            "text": text,
            "advanced": advanced,
            "result": result,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": "tokenization_error"
        }), 500


@analysis_bp.route('/parse', methods=['POST'])
def parse_endpoint():
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        advanced = data.get('advanced', False)
        
        if advanced and advanced_parser:
            result = advanced_parser.parse_advanced(text)
        elif parser:
            result = parser.parse(text)
            result = result.__dict__ if hasattr(result, '__dict__') else result
            
            if 'symptoms' in result and result['symptoms']:
                result['symptoms'] = [s.__dict__ if hasattr(s, '__dict__') else s for s in result['symptoms']]
            if 'temporal_info' in result and hasattr(result['temporal_info'], '__dict__'):
                result['temporal_info'] = result['temporal_info'].__dict__
        else:
            result = simple_parse(text)
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            "success": True,
            "text": text,
            "advanced": advanced,
            "result": result,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": "parsing_error"
        }), 500


@analysis_bp.route('/classify', methods=['POST'])
def classify_endpoint():
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        top_n = data.get('top_n', 3)
        top_n = min(max(top_n, 1), 5)
        predictions = classifier.predict_proba_multiple(text, top_n=top_n)
        single_result = classifier.predict(text)
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            "success": True,
            "input_text": text,
            "top_prediction": single_result,
            "all_predictions": predictions,
            "model_used": "shifaa-v2",
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "⚠️ Ceci est une analyse assistée par IA. Consultez un médecin pour un diagnostic officiel."
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": "classification_error"
        }), 500


@analysis_bp.route('/full', methods=['POST'])
def full_analysis_endpoint():
    """
    Analyse complète: tokenisation + parsing + classification
    POST /api/analysis/full
    Body: {"text": "texte médical complet"}
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text', '')
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # 1. Tokenisation
        token_result = tokenizer.tokenize(text)
        tokens = [t.__dict__ if hasattr(t, '__dict__') else {'text': t.text, 'type': t.type} 
                  for t in token_result.tokens] if hasattr(token_result, 'tokens') else []
        
        # 2. Parsing
        if parser:
            parse_result = parser.parse(text)
            parse_dict = parse_result.__dict__ if hasattr(parse_result, '__dict__') else {}
            if 'symptoms' in parse_dict and parse_dict['symptoms']:
                parse_dict['symptoms'] = [s.__dict__ if hasattr(s, '__dict__') else s for s in parse_dict['symptoms']]
            if 'temporal_info' in parse_dict and hasattr(parse_dict['temporal_info'], '__dict__'):
                parse_dict['temporal_info'] = parse_dict['temporal_info'].__dict__
        else:
            parse_dict = simple_parse(text)
        
        # 3. Classification
        predictions = classifier.predict_proba_multiple(text, top_n=3)
        top_prediction = classifier.predict(text)
        
        # 4. Statistiques
        stats = {
            "word_count": len(text.split()),
            "char_count": len(text),
            "token_count": len(tokens),
            "symptom_count": len(parse_dict.get('symptoms', [])),
            "negation_count": len(parse_dict.get('negations', [])),
            "has_temporal_info": bool(parse_dict.get('temporal_info', {}).get('duration_value'))
        }
        
        processing_time = (time.time() - start_time) * 1000
        
        return jsonify({
            "success": True,
            "input_text": text,
            "tokenization": {
                "tokens": tokens[:50],  # Limiter pour la réponse
                "num_tokens": token_result.num_tokens if hasattr(token_result, 'num_tokens') else len(tokens),
                "medical_terms": token_result.medical_terms if hasattr(token_result, 'medical_terms') else []
            },
            "parsing": parse_dict,
            "classification": {
                "top_prediction": top_prediction,
                "alternatives": predictions[1:3] if len(predictions) > 1 else [],
                "confidence_score": top_prediction.get('confidence', 0)
            },
            "statistics": stats,
            "processing_time_ms": round(processing_time, 2),
            "timestamp": datetime.now().isoformat(),
            "disclaimer": "⚠️ Ceci est une analyse assistée par IA. Ne remplace pas un avis médical professionnel."
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "type": "full_analysis_error"
        }), 500


@analysis_bp.route('/health', methods=['GET'])
def health_check():
    """Vérifier l'état des modèles d'analyse"""
    
    models_status = {
        "tokenizer": "loaded" if tokenizer else "error",
        "advanced_tokenizer": "loaded" if advanced_tokenizer else "not_available",
        "parser": "loaded" if parser else "error",
        "advanced_parser": "loaded" if advanced_parser else "not_available",
        "classifier": "loaded" if classifier else "error"
    }
    
    return jsonify({
        "success": True,
        "service": "SHIFAAAI Analysis API",
        "version": "2.0.0",
        "status": "operational",
        "models": models_status,
        "timestamp": datetime.now().isoformat()
    }), 200


@analysis_bp.route('/batch', methods=['POST'])
def batch_analysis_endpoint():
    """
    Analyser plusieurs textes en lot
    POST /api/analysis/batch
    Body: {"texts": ["texte1", "texte2", ...], "analysis_type": "full"}
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        texts = data.get('texts', [])
        if not texts or not isinstance(texts, list):
            return jsonify({"error": "Invalid texts array"}), 400
        
        analysis_type = data.get('analysis_type', 'full')  # tokenize, parse, classify, full
        
        results = []
        for i, text in enumerate(texts):
            try:
                if analysis_type == 'tokenize':
                    result = tokenizer.tokenize(text)
                    result = result.__dict__ if hasattr(result, '__dict__') else result
                elif analysis_type == 'parse':
                    if parser:
                        result = parser.parse(text)
                        result = result.__dict__ if hasattr(result, '__dict__') else result
                    else:
                        result = simple_parse(text)
                elif analysis_type == 'classify':
                    result = classifier.predict(text)
                else:  # full
                    # Simplifier pour le batch
                    result = {
                        "text": text[:100],
                        "prediction": classifier.predict(text),
                        "symptom_count": len(simple_parse(text).get('symptoms', []))
                    }
                
                results.append({
                    "index": i,
                    "text": text[:200],  # Tronquer pour l'affichage
                    "success": True,
                    "result": result
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
            "analysis_type": analysis_type,
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
            "type": "batch_analysis_error"
        }), 500


# =========================================================
# FONCTIONS UTILITAIRES
# =========================================================

def simple_parse(text: str) -> Dict[str, Any]:
    """Parsing simplifié pour fallback"""
    text_lower = text.lower()
    
    symptoms_keywords = ['fièvre', 'toux', 'fatigue', 'douleur', 'gorge', 'nausée', 
                         'vomissement', 'diarrhée', 'maux de tête', 'vertige']
    
    symptoms = [s for s in symptoms_keywords if s in text_lower]
    
    negations = ['pas', 'ne', 'non', 'jamais']
    found_negations = [n for n in negations if n in text_lower]
    
    return {
        "symptoms": [{"text": s, "type": "symptom"} for s in symptoms],
        "negations": found_negations,
        "temporal_info": {},
        "confidence": 0.7 if symptoms else 0.3
    }


# =========================================================
# INITIALISATION
# =========================================================

def register_analysis_routes(app):
    """Enregistrer les routes d'analyse dans l'application Flask"""
    app.register_blueprint(analysis_bp)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    register_analysis_routes(app)
    
    print("\n" + "="*60)
    print("🏥 SHIFAAAI - ANALYSIS API")
    print("="*60)
    print("📋 Routes disponibles:")
    print("   POST /api/analysis/tokenize  - Tokenisation")
    print("   POST /api/analysis/parse     - Parsing médical")
    print("   POST /api/analysis/classify  - Classification")
    print("   POST /api/analysis/full      - Analyse complète")
    print("   POST /api/analysis/batch     - Analyse par lots")
    print("   GET  /api/analysis/health    - Health check")
    print("="*60 + "\n")
    
    app.run(host="127.0.0.1", port=5000, debug=True)
