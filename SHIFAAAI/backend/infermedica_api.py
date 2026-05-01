# infermedica_api.py - Intégration de l'API Infermedica

import requests
import json
from typing import List, Dict, Any

class InfermedicaClient:
    """
    Client pour l'API Infermedica
    Inscription gratuite sur: https://developer.infermedica.com/signup
    """
    
    def __init__(self, app_id: str, app_key: str):
        self.base_url = "https://api.infermedica.com/v3"
        self.headers = {
            "App-Id": app_id,
            "App-Key": app_key,
            "Content-Type": "application/json"
        }
        self.interview_id = None
    
    def parse_symptoms(self, text: str) -> Dict[str, Any]:
        """
        🔥 Convertit un texte libre en symptômes structurés
        Exemple: "J'ai une forte fièvre et une toux sèche"
        → retourne les symptômes détectés avec leurs IDs
        """
        url = f"{self.base_url}/parse"
        data = {"text": text}
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def search_symptom(self, phrase: str) -> List[Dict]:
        """
        Recherche des symptômes par mot-clé (auto-complétion)
        Utile pour l'interface utilisateur
        """
        url = f"{self.base_url}/search"
        response = requests.get(url, params={"phrase": phrase}, headers=self.headers)
        return response.json()
    
    def get_diagnosis(self, symptoms: List[Dict], age: int, sex: str) -> Dict[str, Any]:
        """
        🩺 Obtient le diagnostic basé sur les symptômes
        Retourne les maladies probables avec scores de confiance
        """
        url = f"{self.base_url}/diagnosis"
        
        evidence = []
        for s in symptoms:
            evidence.append({
                "id": s.get("id") or s.get("symptom_id"),
                "choice_id": "present"
            })
        
        data = {
            "sex": sex,  # "male" ou "female"
            "age": {"value": age},
            "evidence": evidence
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def get_conditions(self) -> List[Dict]:
        """Liste de toutes les maladies disponibles"""
        url = f"{self.base_url}/conditions"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_symptom_details(self, symptom_id: str) -> Dict:
        """Détails d'un symptôme spécifique"""
        url = f"{self.base_url}/symptoms/{symptom_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
