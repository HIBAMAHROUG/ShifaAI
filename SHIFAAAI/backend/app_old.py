# app.py - Version corrigée

import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    APP_NAME = "SHIFAAAI API"
    APP_VERSION = "2.0.0"
    DEBUG = True
    PORT = 5000
    HOST = '127.0.0.1'
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5500', 'http://127.0.0.1:5500']

def create_app():
        # Importer et enregistrer le blueprint d'analyse
        from routes.analysis_routes import analysis_bp
        app.register_blueprint(analysis_bp)
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS simplifié
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # Routes de base
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "success": True,
            "service": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }), 200
    
    @app.route('/info', methods=['GET'])
    def get_info():
        return jsonify({
            "success": True,
            "name": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "endpoints": {
                "health": "/health",
                "info": "/info",
                "predict": "/api/predict/"
            }
        }), 200
    
    # Route de prédiction simple
    @app.route('/api/predict/', methods=['POST'])
    def predict():
        try:
            data = request.get_json()
            text = data.get('text', '') or data.get('symptoms', '')
            
            if not text:
                return jsonify({"error": "No symptoms provided"}), 400
            
            # Logique simple de prédiction
            text_lower = text.lower()
            
            if 'fièvre' in text_lower and 'toux' in text_lower:
                disease = "Grippe"
                confidence = 85.0
            elif 'gorge' in text_lower:
                disease = "Angine"
                confidence = 70.0
            elif 'nausée' in text_lower or 'vomissement' in text_lower:
                disease = "Gastro-entérite"
                confidence = 75.0
            elif 'maux de tête' in text_lower:
                disease = "Migraine"
                confidence = 65.0
            else:
                disease = "Non déterminé"
                confidence = 40.0
            
            return jsonify({
                "success": True,
                "input_text": text,
                "predicted_disease": disease,
                "confidence": confidence,
                "probability": f"{confidence}%"
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        """Servir le frontend s'il existe"""
        frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
        if os.path.exists(frontend_path):
            from flask import send_from_directory
            if path and os.path.exists(os.path.join(frontend_path, path)):
                return send_from_directory(frontend_path, path)
            elif os.path.exists(os.path.join(frontend_path, 'index.html')):
                return send_from_directory(frontend_path, 'index.html')
        return jsonify({"error": "Frontend not found"}), 404
    
    return app

if __name__ == "__main__":
    app = create_app()
    
    print("\n" + "="*60)
    print("🏥 SHIFAAAI - API SERVER")
    print("="*60)
    print(f"🌐 Serveur: http://{Config.HOST}:{Config.PORT}")
    print("📋 Endpoints disponibles:")
    print("   GET  /health")
    print("   GET  /info")
    print("   POST /api/predict/")
    print("="*60 + "\n")
    
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)