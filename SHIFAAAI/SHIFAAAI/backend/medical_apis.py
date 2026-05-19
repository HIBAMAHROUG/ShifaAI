"""Handles external medical lookups for disease and drug enrichment."""

import requests
from typing import Dict, List

class MedicalAPIs:
    # Disease Ontology API
    DISEASE_ONTOLOGY_BASE = "https://www.ebi.ac.uk/ols4/api"
    OPENFDA_BASE = "https://api.fda.gov/drug/label.json"
    
    @staticmethod
    def search_mesh_term(disease_name: str) -> Dict:
        try:
            search_url = f"{MedicalAPIs.DISEASE_ONTOLOGY_BASE}/search"
            params = {
                "q": disease_name,
                "ontology": "doid",
                "rows": 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("response", {}).get("docs", [])
                
                if results:
                    top_result = results[0]
                    return {
                        "success": True,
                        "data": {
                            "id": top_result.get("obo_id", ""),
                            "label": top_result.get("label", ""),
                            "description": top_result.get("description", [""])[0] if top_result.get("description") else "",
                            "synonyms": top_result.get("synonym", []),
                            "source": "Disease Ontology"
                        }
                    }
            
            return {"success": False, "error": "No results found"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def search_disease(disease_name: str) -> Dict:
        try:
            results = []
            
            mesh_result = MedicalAPIs.search_mesh_term(disease_name)
            if mesh_result.get("success"):
                results.append(mesh_result["data"])
            
            return {
                "success": True,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def search_drug(drug_name: str) -> Dict:
        try:
            search_url = f"{MedicalAPIs.OPENFDA_BASE}"
            params = {
                "search": f"openfda.brand_name:\"{drug_name}\" OR openfda.generic_name:\"{drug_name}\"",
                "limit": 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    drug_info = []
                    for result in results:
                        drug_data = {
                            "brand_name": result.get("openfda", {}).get("brand_name", [""])[0],
                            "generic_name": result.get("openfda", {}).get("generic_name", [""])[0],
                            "manufacturer": result.get("openfda", {}).get("manufacturer_name", [""])[0],
                            "purpose": result.get("purpose", []),
                            "warnings": result.get("warnings", [])[:2],
                            "dosage_and_administration": result.get("dosage_and_administration", [])
                        }
                        drug_info.append(drug_data)
                    
                    return {
                        "success": True,
                        "results": drug_info,
                        "count": len(drug_info)
                    }
            
            return {"success": False, "error": "Drug not found"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_disease_symptoms(disease_name: str) -> Dict:
        symptom_mapping = {
            "Grippe": ["fièvre", "toux", "fatigue", "courbatures", "maux de tête"],
            "COVID-19": ["fièvre", "toux sèche", "fatigue", "perte d'odorat", "perte de goût"],
            "Bronchite": ["toux", "expectoration", "essoufflement", "douleur thoracique"],
            "Pneumonie": ["fièvre élevée", "toux productive", "essoufflement", "douleur thoracique"],
            "Migraine": ["maux de tête", "sensibilité lumière", "sensibilité son", "nausées"],
            "Gastro-entérite": ["nausées", "vomissements", "diarrhée", "crampes abdominales"]
        }
        
        symptoms = symptom_mapping.get(disease_name, [])
        
        return {
            "success": True,
            "disease": disease_name,
            "symptoms": symptoms,
            "source": "internal_database"
        }
    
    @staticmethod
    def validate_drug_interaction(drugs: List[str]) -> Dict:
        return {
            "success": True,
            "drugs_checked": drugs,
            "interactions": [],
            "warning": "This is a basic implementation. Always consult healthcare professionals.",
            "source": "basic_validation"
        }
