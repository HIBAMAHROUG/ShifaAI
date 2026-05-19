"""Creates and initializes the SHIFAAAI SQLite database."""

import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import secrets

DB_NAME = "shifaa.db"
SCHEMA_FILE = "schema.sql"
BACKUP_DIR = "backups"
DATA_DIR = "data"

class Logger:
    @staticmethod
    def info(message):
        print(f"INFO: {message}")
    
    @staticmethod
    def success(message):
        print(f"SUCCESS: {message}")
    
    @staticmethod
    def error(message):
        print(f"ERROR: {message}")
    
    @staticmethod
    def warning(message):
        print(f"WARNING: {message}")
    
    @staticmethod
    def progress(message):
        print(f"PROGRESS: {message}")

logger = Logger()

def ensure_directories():
    try:
        backup_path = Path(BACKUP_DIR)
        if not backup_path.exists():
            backup_path.mkdir(parents=True)
            logger.info(f"Dossier de sauvegarde créé: {BACKUP_DIR}")
        
        data_path = Path(DATA_DIR)
        if not data_path.exists():
            data_path.mkdir(parents=True)
            logger.info(f"Dossier data créé: {DATA_DIR}")
        
        return True
    except Exception as e:
        logger.error(f"Erreur création dossiers: {e}")
        return False

def backup_existing_database():
    db_path = Path(DB_NAME)
    
    if db_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{BACKUP_DIR}/{DB_NAME}.{timestamp}.backup"
        
        try:
            import shutil
            shutil.copy2(DB_NAME, backup_name)
            logger.success(f"Sauvegarde créée: {backup_name}")
            return True
        except Exception as e:
            logger.warning(f"Impossible de créer la sauvegarde: {e}")
            return False
    
    return True

def get_default_schema():
    return """
-- =========================================================
-- SHIFAAAI - SCHEMA DE BASE DE DONNÉES
-- =========================================================

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des symptômes
CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100),
    severity_level INTEGER DEFAULT 1
);

-- Table des maladies
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    risk_level VARCHAR(50),
    consultation_needed BOOLEAN DEFAULT 0
);

-- Table de relation maladie-symptôme
CREATE TABLE IF NOT EXISTS disease_symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id INTEGER NOT NULL,
    symptom_id INTEGER NOT NULL,
    weight REAL DEFAULT 1.0,
    FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(id) ON DELETE CASCADE,
    UNIQUE(disease_id, symptom_id)
);

-- Table des analyses
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    input_text TEXT NOT NULL,
    predicted_disease VARCHAR(255),
    confidence_score REAL,
    all_predictions TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Table des prédictions
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_text TEXT NOT NULL,
    predicted_disease VARCHAR(255),
    confidence_score REAL,
    all_predictions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des feedbacks
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_id INTEGER,
    helpful BOOLEAN,
    rating INTEGER,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE SET NULL
);

-- Insertion des symptômes par défaut
INSERT OR IGNORE INTO symptoms (name, description, severity_level) VALUES
('fièvre', 'Température corporelle élevée', 3),
('toux', 'Expulsion d\'air des poumons', 3),
('fatigue', 'Sensation d\'épuisement', 2),
('courbatures', 'Douleurs musculaires', 2),
('mal de gorge', 'Douleur dans la gorge', 2),
('nez congestionné', 'Nez bouché', 1),
('maux de tête', 'Douleur à la tête', 2),
('nausée', 'Envie de vomir', 2),
('diarrhée', 'Selles liquides', 3),
('essoufflement', 'Difficulté à respirer', 4);

-- Insertion des maladies par défaut
INSERT OR IGNORE INTO diseases (name, description, risk_level) VALUES
('Grippe', 'Infection virale respiratoire', 'modéré'),
('Angine', 'Inflammation de la gorge', 'faible'),
('Gastro-entérite', 'Infection digestive', 'modéré'),
('Bronchite', 'Inflammation des bronches', 'modéré'),
('Rhume', 'Infection bénigne des voies respiratoires', 'faible');

-- Insertion des relations
INSERT OR IGNORE INTO disease_symptoms (disease_id, symptom_id, weight) VALUES
(1, 1, 3.0), (1, 2, 3.0), (1, 3, 2.0),  -- Grippe
(2, 5, 4.0), (2, 1, 2.0),               -- Angine
(3, 8, 3.0), (3, 9, 3.0),               -- Gastro-entérite
(4, 2, 4.0), (4, 10, 3.5),              -- Bronchite
(5, 6, 3.0), (5, 7, 2.0);               -- Rhume

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);
"""

def get_schema_content():
    schema_path = Path(SCHEMA_FILE)
    
    if schema_path.exists():
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"Schéma chargé depuis {SCHEMA_FILE}")
            return content
        except Exception as e:
            logger.warning(f"Erreur lecture {SCHEMA_FILE}: {e}")
    
    logger.info("Utilisation du schéma par défaut")
    return get_default_schema()

def create_default_schema_file():
    try:
        with open(SCHEMA_FILE, "w", encoding="utf-8") as f:
            f.write(get_default_schema())
        logger.success(f"Fichier {SCHEMA_FILE} créé")
        return True
    except Exception as e:
        logger.error(f"Erreur création {SCHEMA_FILE}: {e}")
        return False

def execute_schema(conn, schema_content):
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_content)
        conn.commit()
        logger.success("Schéma exécuté avec succès")
        return True
    except sqlite3.Error as e:
        logger.error(f"Erreur SQL: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return False

def verify_database(conn):
    cursor = conn.cursor()
    
    expected_tables = ['users', 'symptoms', 'diseases', 'disease_symptoms', 'analyses', 'predictions', 'feedback']
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
    """)
    
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    logger.info(f"Tables trouvées: {', '.join(existing_tables)}")
    
    missing_tables = set(expected_tables) - set(existing_tables)
    
    if missing_tables:
        logger.warning(f"Tables manquantes: {', '.join(missing_tables)}")
        return False
    
    cursor.execute("SELECT COUNT(*) FROM symptoms")
    symptom_count = cursor.fetchone()[0]
    logger.success(f"Symptômes: {symptom_count}")
    
    cursor.execute("SELECT COUNT(*) FROM diseases")
    disease_count = cursor.fetchone()[0]
    logger.success(f"Maladies: {disease_count}")
    
    return True

def show_database_stats(conn):
    cursor = conn.cursor()
    
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)
    
    if os.path.exists(DB_NAME):
        size_bytes = os.path.getsize(DB_NAME)
        size_mb = size_bytes / (1024 * 1024)
        print(f"Size: {size_mb:.2f} MB")
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count} records")
    
    print("=" * 50 + "\n")

def create_database(force: bool = False, quiet: bool = False):
    global logger
    if quiet:
        class QuietLogger:
            @staticmethod
            def info(message): pass
            @staticmethod
            def success(message): pass
            @staticmethod
            def error(message): pass
            @staticmethod
            def warning(message): pass
            @staticmethod
            def progress(message): pass
        logger = QuietLogger()
    
    print("\n" + "=" * 60)
    print("SHIFAAAI - DATABASE CREATION")
    print("=" * 60 + "\n")
    
    if not ensure_directories():
        return False
    
    backup_existing_database()
    
    if not os.path.exists(SCHEMA_FILE):
        if not create_default_schema_file():
            return False
    
    if os.path.exists(DB_NAME) and not force:
        response = input(f"Database {DB_NAME} already exists. Replace it? (o/N): ")
        if response.lower() != 'o':
            logger.info("Opération annulée")
            return False
    
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            logger.info(f"Base supprimée: {DB_NAME}")
        except Exception as e:
            logger.error(f"Impossible de supprimer: {e}")
            return False
    
    try:
        conn = sqlite3.connect(DB_NAME)
        logger.success(f"Connexion établie: {DB_NAME}")
        
        conn.execute("PRAGMA foreign_keys = ON")
        
        schema_content = get_schema_content()
        if not execute_schema(conn, schema_content):
            return False
        
        if verify_database(conn):
            logger.success("Vérification de la base réussie!")
            show_database_stats(conn)
            return True
        else:
            logger.warning("Certaines tables sont manquantes")
            return False
            
    except sqlite3.Error as e:
        logger.error(f"Erreur SQLite: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("Connexion fermée")

def test_connection():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        logger.success(f"SQLite version: {version}")
        
        # Afficher le contenu
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTables available: {', '.join(tables)}")
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Test de connexion échoué: {e}")
        return False

def insert_test_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        count = cursor.fetchone()[0]
        
        if count == 0:
            test_predictions = [
                ("fièvre toux fatigue", "Grippe", 85.5, '[{"disease": "Grippe", "confidence": 85.5}]'),
                ("mal de gorge fièvre", "Angine", 78.2, '[{"disease": "Angine", "confidence": 78.2}]'),
                ("nausée vomissement diarrhée", "Gastro-entérite", 82.3, '[{"disease": "Gastro-entérite", "confidence": 82.3}]')
            ]
            
            cursor.executemany("""
                INSERT INTO predictions (input_text, predicted_disease, confidence_score, all_predictions)
                VALUES (?, ?, ?, ?)
            """, test_predictions)
            
            conn.commit()
            logger.success("Données de test insérées")
        
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Erreur insertion données test: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SHIFAAAI - Création de la base de données")
    parser.add_argument("--force", "-f", action="store_true", help="Forcer la recréation sans confirmation")
    parser.add_argument("--quiet", "-q", action="store_true", help="Mode silencieux")
    parser.add_argument("--test", "-t", action="store_true", help="Ajouter des données de test")
    
    args = parser.parse_args()
    
    success = create_database(force=args.force, quiet=args.quiet)
    
    if success:
        test_connection()
        
        if args.test:
            insert_test_data()
        
        print("\nBase de données SHIFAAAI prête à l'emploi")
        print(f"Fichier: {DB_NAME}")
        print("Use 'sqlite3 shifaa.db' to interact with the database")
        print("Use '.tables' to list tables and '.schema' to inspect the schema")
    else:
        print("\nDatabase creation failed")
        sys.exit(1)