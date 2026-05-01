# disease_service.py - Service de gestion des maladies pour SHIFAAAI

import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import re

# =========================================================
# CLASSES DE DONNÉES
# =========================================================

@dataclass
class Disease:
    """Structure d'une maladie"""
    id: int
    name: str
    scientific_name: Optional[str]
    category: str
    risk_level: str
    urgency_level: int
    consultation_needed: bool
    contagious: bool
    incubation_days: Optional[str]
    typical_duration: Optional[str]
    common_symptoms: List[str]
    critical_symptoms: List[str]
    treatment: str
    prevention: str
    recommendation: str
    when_to_consult: str
    icd11_code: Optional[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class Symptom:
    """Structure d'un symptôme"""
    id: int
    name: str
    category: str
    severity_level: int
    icd11_code: Optional[str]

@dataclass
class DiseaseSymptomRelation:
    """Relation maladie-symptôme"""
    disease_id: int
    symptom_id: int
    weight: float
    is_primary: bool

# =========================================================
# SERVICE DE GESTION DES MALADIES
# =========================================================

class DiseaseService:
    """Service pour gérer les maladies et symptômes"""
    
    def __init__(self, db_path: str = "shifaa.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialiser la base de données avec les tables nécessaires"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Table des maladies
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                scientific_name VARCHAR(255),
                category VARCHAR(100),
                risk_level VARCHAR(50),
                urgency_level INTEGER DEFAULT 2,
                consultation_needed BOOLEAN DEFAULT 0,
                contagious BOOLEAN DEFAULT 0,
                incubation_days VARCHAR(50),
                typical_duration VARCHAR(100),
                common_symptoms TEXT,
                critical_symptoms TEXT,
                treatment TEXT,
                prevention TEXT,
                recommendation TEXT,
                when_to_consult TEXT,
                icd11_code VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table des symptômes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL UNIQUE,
                category VARCHAR(100),
                severity_level INTEGER DEFAULT 1,
                icd11_code VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table de relation maladie-symptôme
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disease_symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_id INTEGER NOT NULL,
                symptom_id INTEGER NOT NULL,
                weight FLOAT DEFAULT 1.0,
                is_primary BOOLEAN DEFAULT 0,
                FOREIGN KEY (disease_id) REFERENCES diseases(id),
                FOREIGN KEY (symptom_id) REFERENCES symptoms(id),
                UNIQUE(disease_id, symptom_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insérer les données par défaut si la table est vide
        self._insert_default_data()
    
    def _get_connection(self):
        """Obtenir une connexion à la base de données"""
        return sqlite3.connect(self.db_path)
    
    def _insert_default_data(self):
        """Insérer les données par défaut des maladies"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Vérifier si la table est vide
        cursor.execute("SELECT COUNT(*) FROM diseases")
        count = cursor.fetchone()[0]
        
        if count == 0:
            diseases = self._get_default_diseases()
            for disease in diseases:
                self._insert_disease(conn, disease)
        
        conn.close()
    
    def _get_default_diseases(self) -> List[Dict]:
        """Retourner la liste des maladies par défaut"""
        return [
            {
                "name": "Grippe",
                "scientific_name": "Influenza",
                "category": "infectieuse",
                "risk_level": "modéré",
                "urgency_level": 2,
                "consultation_needed": False,
                "contagious": True,
                "incubation_days": "1-4 jours",
                "typical_duration": "5-7 jours",
                "common_symptoms": ["fièvre", "toux", "fatigue", "courbatures", "frissons"],
                "critical_symptoms": ["essoufflement", "confusion"],
                "treatment": "Repos, hydratation, antipyrétiques",
                "prevention": "Vaccination annuelle, lavage des mains",
                "recommendation": "Repos à domicile, isolement pendant 24h après la fin de la fièvre",
                "when_to_consult": "Fièvre > 3 jours, difficultés respiratoires",
                "icd11_code": "1E30"
            },
            {
                "name": "COVID-19",
                "scientific_name": "SARS-CoV-2 infection",
                "category": "infectieuse",
                "risk_level": "élevé",
                "urgency_level": 4,
                "consultation_needed": True,
                "contagious": True,
                "incubation_days": "2-14 jours",
                "typical_duration": "7-14 jours",
                "common_symptoms": ["fièvre", "toux", "fatigue", "perte goût", "perte odorat"],
                "critical_symptoms": ["essoufflement", "douleur poitrine", "confusion"],
                "treatment": "Isolement, traitement symptomatique, oxygénothérapie si nécessaire",
                "prevention": "Vaccination, masque, distanciation sociale",
                "recommendation": "Test PCR recommandé, isolement immédiat",
                "when_to_consult": "Dès l'apparition des symptômes",
                "icd11_code": "RA01"
            },
            {
                "name": "Angine",
                "scientific_name": "Pharyngite",
                "category": "ORL",
                "risk_level": "faible",
                "urgency_level": 2,
                "consultation_needed": False,
                "contagious": True,
                "incubation_days": "1-3 jours",
                "typical_duration": "3-5 jours",
                "common_symptoms": ["mal de gorge", "douleur gorge", "difficulté avaler", "fièvre"],
                "critical_symptoms": ["difficulté respiratoire", "impossibilité d'avaler"],
                "treatment": "Antalgiques, anti-inflammatoires, gargarismes",
                "prevention": "Lavage des mains, éviter partage ustensiles",
                "recommendation": "Boissons chaudes, repos vocal",
                "when_to_consult": "Persistance > 48h, difficulté avaler",
                "icd11_code": "CA0A"
            },
            {
                "name": "Gastro-entérite",
                "scientific_name": "Gastroenteritis",
                "category": "digestif",
                "risk_level": "modéré",
                "urgency_level": 3,
                "consultation_needed": False,
                "contagious": True,
                "incubation_days": "1-3 jours",
                "typical_duration": "2-4 jours",
                "common_symptoms": ["nausée", "vomissement", "diarrhée", "douleur ventre"],
                "critical_symptoms": ["déshydratation sévère", "sang dans selles"],
                "treatment": "Hydratation, repos, régime sans lactose",
                "prevention": "Lavage des mains, cuisson des aliments",
                "recommendation": "Boire par petites quantités",
                "when_to_consult": "Signes déshydratation, fièvre > 40°C",
                "icd11_code": "1A02"
            },
            {
                "name": "Bronchite",
                "scientific_name": "Bronchitis",
                "category": "respiratoire",
                "risk_level": "modéré",
                "urgency_level": 3,
                "consultation_needed": True,
                "contagious": False,
                "incubation_days": None,
                "typical_duration": "1-3 semaines",
                "common_symptoms": ["toux", "expectoration", "fatigue", "essoufflement"],
                "critical_symptoms": ["essoufflement sévère", "fièvre élevée prolongée"],
                "treatment": "Repos, bronchodilatateurs, kinésithérapie respiratoire",
                "prevention": "Éviter le tabac, se laver les mains",
                "recommendation": "Hydratation, humidifier l'air",
                "when_to_consult": "Toux > 3 semaines, difficultés respiratoires",
                "icd11_code": "CA20"
            },
            {
                "name": "Migraine",
                "scientific_name": "Migraine",
                "category": "neurologique",
                "risk_level": "modéré",
                "urgency_level": 2,
                "consultation_needed": False,
                "contagious": False,
                "incubation_days": None,
                "typical_duration": "4-72 heures",
                "common_symptoms": ["maux de tête", "nausée", "sensibilité lumière", "vision floue"],
                "critical_symptoms": ["maux de tête soudain sévère", "paralysie"],
                "treatment": "Repos dans l'obscurité, antimigraineux, AINS",
                "prevention": "Identifier les déclencheurs, éviter le stress",
                "recommendation": "Repos au calme, hydratation",
                "when_to_consult": "Crises fréquentes (>4/mois)",
                "icd11_code": "8A80"
            },
            {
                "name": "Pneumonie",
                "scientific_name": "Pneumonia",
                "category": "respiratoire",
                "risk_level": "critique",
                "urgency_level": 5,
                "consultation_needed": True,
                "contagious": True,
                "incubation_days": "1-3 jours",
                "typical_duration": "2-4 semaines",
                "common_symptoms": ["fièvre élevée", "toux", "expectoration", "douleur poitrine", "fatigue"],
                "critical_symptoms": ["essoufflement sévère", "confusion", "lèvres bleues"],
                "treatment": "Antibiotiques, repos, hospitalisation possible",
                "prevention": "Vaccination, hygiène des mains",
                "recommendation": "URGENCE - Consultation médicale immédiate",
                "when_to_consult": "Immédiatement - Appeler le 15",
                "icd11_code": "CA40"
            }
        ]
    
    def _insert_disease(self, conn, disease_data: Dict):
        """Insérer une maladie dans la base"""
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO diseases (
                name, scientific_name, category, risk_level, urgency_level,
                consultation_needed, contagious, incubation_days, typical_duration,
                common_symptoms, critical_symptoms, treatment, prevention,
                recommendation, when_to_consult, icd11_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            disease_data["name"],
            disease_data.get("scientific_name"),
            disease_data.get("category"),
            disease_data["risk_level"],
            disease_data["urgency_level"],
            disease_data["consultation_needed"],
            disease_data["contagious"],
            disease_data.get("incubation_days"),
            disease_data.get("typical_duration"),
            json.dumps(disease_data["common_symptoms"]),
            json.dumps(disease_data.get("critical_symptoms", [])),
            disease_data["treatment"],
            disease_data.get("prevention", ""),
            disease_data["recommendation"],
            disease_data.get("when_to_consult", ""),
            disease_data.get("icd11_code")
        ))
        
        disease_id = cursor.lastrowid
        
        # Insérer les symptômes et relations
        for symptom in disease_data["common_symptoms"]:
            # Vérifier si le symptôme existe
            cursor.execute("SELECT id FROM symptoms WHERE name = ?", (symptom,))
            symptom_row = cursor.fetchone()
            
            if symptom_row:
                symptom_id = symptom_row[0]
            else:
                cursor.execute("INSERT INTO symptoms (name) VALUES (?)", (symptom,))
                symptom_id = cursor.lastrowid
            
            # Insérer la relation
            cursor.execute("""
                INSERT OR IGNORE INTO disease_symptoms (disease_id, symptom_id, weight, is_primary)
                VALUES (?, ?, ?, ?)
            """, (disease_id, symptom_id, 1.0, True))
        
        conn.commit()
    
    # =========================================================
    # CRUD OPERATIONS
    # =========================================================
    
    def get_all_diseases(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Récupérer toutes les maladies"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, scientific_name, category, risk_level, urgency_level,
                   consultation_needed, contagious, incubation_days, typical_duration,
                   common_symptoms, critical_symptoms, treatment, prevention,
                   recommendation, when_to_consult, icd11_code, created_at
            FROM diseases
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        diseases = []
        for row in cursor.fetchall():
            disease = {
                "id": row[0],
                "name": row[1],
                "scientific_name": row[2],
                "category": row[3],
                "risk_level": row[4],
                "urgency_level": row[5],
                "consultation_needed": bool(row[6]),
                "contagious": bool(row[7]),
                "incubation_days": row[8],
                "typical_duration": row[9],
                "common_symptoms": json.loads(row[10]) if row[10] else [],
                "critical_symptoms": json.loads(row[11]) if row[11] else [],
                "treatment": row[12],
                "prevention": row[13],
                "recommendation": row[14],
                "when_to_consult": row[15],
                "icd11_code": row[16],
                "created_at": row[17]
            }
            diseases.append(disease)
        
        conn.close()
        return diseases
    
    def get_disease_by_id(self, disease_id: int) -> Optional[Dict]:
        """Récupérer une maladie par son ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, scientific_name, category, risk_level, urgency_level,
                   consultation_needed, contagious, incubation_days, typical_duration,
                   common_symptoms, critical_symptoms, treatment, prevention,
                   recommendation, when_to_consult, icd11_code, created_at
            FROM diseases
            WHERE id = ?
        """, (disease_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "scientific_name": row[2],
                "category": row[3],
                "risk_level": row[4],
                "urgency_level": row[5],
                "consultation_needed": bool(row[6]),
                "contagious": bool(row[7]),
                "incubation_days": row[8],
                "typical_duration": row[9],
                "common_symptoms": json.loads(row[10]) if row[10] else [],
                "critical_symptoms": json.loads(row[11]) if row[11] else [],
                "treatment": row[12],
                "prevention": row[13],
                "recommendation": row[14],
                "when_to_consult": row[15],
                "icd11_code": row[16],
                "created_at": row[17]
            }
        
        return None
    
    def get_disease_by_name(self, name: str) -> Optional[Dict]:
        """Récupérer une maladie par son nom"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, scientific_name, category, risk_level, urgency_level,
                   consultation_needed, contagious, incubation_days, typical_duration,
                   common_symptoms, critical_symptoms, treatment, prevention,
                   recommendation, when_to_consult, icd11_code, created_at
            FROM diseases
            WHERE LOWER(name) = LOWER(?)
        """, (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "scientific_name": row[2],
                "category": row[3],
                "risk_level": row[4],
                "urgency_level": row[5],
                "consultation_needed": bool(row[6]),
                "contagious": bool(row[7]),
                "incubation_days": row[8],
                "typical_duration": row[9],
                "common_symptoms": json.loads(row[10]) if row[10] else [],
                "critical_symptoms": json.loads(row[11]) if row[11] else [],
                "treatment": row[12],
                "prevention": row[13],
                "recommendation": row[14],
                "when_to_consult": row[15],
                "icd11_code": row[16],
                "created_at": row[17]
            }
        
        return None
    
    def search_diseases(self, query: str, limit: int = 20) -> List[Dict]:
        """Rechercher des maladies par nom ou symptômes"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Recherche par nom
        cursor.execute("""
            SELECT id, name, scientific_name, category, risk_level, urgency_level,
                   consultation_needed, common_symptoms, treatment
            FROM diseases
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(scientific_name) LIKE LOWER(?)
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        diseases = []
        for row in cursor.fetchall():
            diseases.append({
                "id": row[0],
                "name": row[1],
                "scientific_name": row[2],
                "category": row[3],
                "risk_level": row[4],
                "urgency_level": row[5],
                "consultation_needed": bool(row[6]),
                "common_symptoms": json.loads(row[7]) if row[7] else [],
                "treatment": row[8]
            })
        
        conn.close()
        return diseases
    
    def get_diseases_by_symptom(self, symptom: str, limit: int = 20) -> List[Dict]:
        """Trouver les maladies associées à un symptôme"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT d.id, d.name, d.category, d.risk_level, d.urgency_level,
                   ds.weight, ds.is_primary
            FROM diseases d
            JOIN disease_symptoms ds ON d.id = ds.disease_id
            JOIN symptoms s ON ds.symptom_id = s.id
            WHERE LOWER(s.name) LIKE LOWER(?)
            ORDER BY ds.weight DESC, ds.is_primary DESC
            LIMIT ?
        """, (f"%{symptom}%", limit))
        
        diseases = []
        for row in cursor.fetchall():
            diseases.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "risk_level": row[3],
                "urgency_level": row[4],
                "weight": row[5],
                "is_primary": bool(row[6])
            })
        
        conn.close()
        return diseases
    
    # =========================================================
    # STATISTIQUES
    # =========================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir des statistiques sur les maladies"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Nombre total
        cursor.execute("SELECT COUNT(*) FROM diseases")
        total = cursor.fetchone()[0]
        
        # Par catégorie
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM diseases
            GROUP BY category
            ORDER BY count DESC
        """)
        by_category = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Par niveau de risque
        cursor.execute("""
            SELECT risk_level, COUNT(*) as count
            FROM diseases
            GROUP BY risk_level
        """)
        by_risk = [{"risk_level": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Consultation nécessaire
        cursor.execute("""
            SELECT consultation_needed, COUNT(*) as count
            FROM diseases
            GROUP BY consultation_needed
        """)
        by_consultation = [{"consultation_needed": bool(row[0]), "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_diseases": total,
            "by_category": by_category,
            "by_risk_level": by_risk,
            "by_consultation_needed": by_consultation
        }
    
    # =========================================================
    # SYMPTOMS MANAGEMENT
    # =========================================================
    
    def get_all_symptoms(self, limit: int = 100) -> List[Dict]:
        """Récupérer tous les symptômes"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, category, severity_level, icd11_code
            FROM symptoms
            LIMIT ?
        """, (limit,))
        
        symptoms = []
        for row in cursor.fetchall():
            symptoms.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "severity_level": row[3],
                "icd11_code": row[4]
            })
        
        conn.close()
        return symptoms
    
    def add_symptom(self, name: str, category: str = None, severity_level: int = 1) -> int:
        """Ajouter un nouveau symptôme"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO symptoms (name, category, severity_level)
                VALUES (?, ?, ?)
            """, (name.lower(), category, severity_level))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Symptôme existe déjà
            cursor.execute("SELECT id FROM symptoms WHERE name = ?", (name.lower(),))
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    # =========================================================
    # EXPORT/IMPORT
    # =========================================================
    
    def export_to_json(self) -> str:
        """Exporter toutes les maladies en JSON"""
        diseases = self.get_all_diseases(limit=1000)
        return json.dumps(diseases, ensure_ascii=False, indent=2)
    
    def import_from_json(self, json_data: str) -> int:
        """Importer des maladies depuis un JSON"""
        diseases = json.loads(json_data)
        count = 0
        
        conn = self._get_connection()
        for disease in diseases:
            try:
                self._insert_disease(conn, disease)
                count += 1
            except Exception as e:
                print(f"Erreur importation {disease.get('name')}: {e}")
        
        conn.close()
        return count

# =========================================================
# SERVICE SINGLETON
# =========================================================

_disease_service_instance = None

def get_disease_service() -> DiseaseService:
    """Obtenir l'instance unique du service"""
    global _disease_service_instance
    if _disease_service_instance is None:
        _disease_service_instance = DiseaseService()
    return _disease_service_instance

# =========================================================
# TESTS
# =========================================================

def test_disease_service():
    """Tester le service des maladies"""
    service = get_disease_service()
    
    print("\n" + "="*60)
    print("🏥 TEST DU DISEASE SERVICE")
    print("="*60)
    
    # 1. Récupérer toutes les maladies
    diseases = service.get_all_diseases()
    print(f"\n📋 {len(diseases)} maladies trouvées")
    
    # 2. Rechercher une maladie
    flu = service.get_disease_by_name("Grippe")
    if flu:
        print(f"\n🦠 Maladie trouvée: {flu['name']}")
        print(f"   - Risque: {flu['risk_level']}")
        print(f"   - Symptômes: {', '.join(flu['common_symptoms'][:3])}")
    
    # 3. Rechercher par symptôme
    fever_diseases = service.get_diseases_by_symptom("fièvre")
    print(f"\n🔥 Maladies associées à la fièvre: {len(fever_diseases)}")
    
    # 4. Statistiques
    stats = service.get_statistics()
    print(f"\n📊 Statistiques:")
    print(f"   - Total: {stats['total_diseases']}")
    print(f"   - Par risque: {stats['by_risk_level']}")
    
    # 5. Recherche textuelle
    search_results = service.search_diseases("grippe")
    print(f"\n🔍 Recherche 'grippe': {len(search_results)} résultats")
    
    return service

if __name__ == "__main__":
    test_disease_service()