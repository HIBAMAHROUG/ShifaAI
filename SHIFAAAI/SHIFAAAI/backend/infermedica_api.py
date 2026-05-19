"""Handles Infermedica requests for symptom parsing and diagnosis."""

import requests
from typing import List, Dict, Any

class InfermedicaClient:
    def __init__(self, app_id: str, app_key: str):
        self.base_url = "https://api.infermedica.com/v3"
        self.headers = {
            "App-Id": app_id,
            "App-Key": app_key,
            "Content-Type": "application/json"
        }
        self.interview_id = None
    
    def parse_symptoms(self, text: str) -> Dict[str, Any]:
        url = f"{self.base_url}/parse"
        data = {"text": text}
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def search_symptom(self, phrase: str) -> List[Dict]:
        url = f"{self.base_url}/search"
        response = requests.get(url, params={"phrase": phrase}, headers=self.headers)
        return response.json()
    
    def get_diagnosis(self, symptoms: List[Dict], age: int, sex: str) -> Dict[str, Any]:
        url = f"{self.base_url}/diagnosis"
        
        evidence = []
        for s in symptoms:
            evidence.append({
                "id": s.get("id") or s.get("symptom_id"),
                "choice_id": "present"
            })
        
        data = {
            "sex": sex,
            "age": {"value": age},
            "evidence": evidence
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def get_conditions(self) -> List[Dict]:
        url = f"{self.base_url}/conditions"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_symptom_details(self, symptom_id: str) -> Dict:
        url = f"{self.base_url}/symptoms/{symptom_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
