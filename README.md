# SHIFAAAI
## Plateforme d’Analyse Médicale par Intelligence Artificielle

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

---

# Présentation

SHIFAAAI est une plateforme basée sur l’intelligence artificielle permettant d’analyser des symptômes médicaux rédigés en langage naturel afin de prédire des maladies probables grâce aux techniques de Traitement du Langage Naturel (NLP) et de Machine Learning.

L’application traite les données utilisateurs à travers plusieurs étapes :
- tokenisation,
- analyse lexicale,
- analyse syntaxique,
- extraction des symptômes,
- génération de prédictions médicales.

L’objectif du projet est de combiner les technologies de l’IA avec l’assistance médicale dans un environnement interactif et moderne.

---

# Fonctionnalités Principales

## Analyse Lexicale
- Tokenisation du texte
- Détection automatique des symptômes
- Détection des négations
- Analyse des intensificateurs
- Extraction des expressions temporelles

Exemples :
- « pas de fièvre »
- « forte migraine »
- « depuis hier »

---

## Analyse Syntaxique
- POS Tagging
- Analyse de la structure des phrases
- Classification grammaticale des mots
- Analyse des relations syntaxiques

---

## Prédiction des Maladies

Le système peut prédire plusieurs maladies comme :
- Grippe
- Bronchite
- Angine
- Gastro-entérite
- Infections respiratoires

Chaque prédiction contient :
- un score de confiance,
- une estimation de probabilité,
- une recommandation médicale.

---

# Pipeline de Traitement IA

```text
Texte Utilisateur
        ↓
Tokenisation
        ↓
Analyse Lexicale
        ↓
Analyse Syntaxique
        ↓
Extraction des Caractéristiques
        ↓
Modèle de Machine Learning
        ↓
Prédiction Médicale
```

---

# Technologies Utilisées

## Frontend
- HTML5
- CSS3
- JavaScript ES6
- Bootstrap 5

## Backend
- Python 3.10+
- Flask
- Flask-CORS
- SQLite

## Machine Learning
- scikit-learn
- pandas
- numpy

---

---

# Installation

## Cloner le Dépôt

```bash
git clone https://github.com/HIBAMAHROUG/ShifaaAI.git
cd ShifaaAI
```

---

## Créer un Environnement Virtuel

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Installer les Dépendances

```bash
pip install -r requirements.txt
```

---

## Créer la Base de Données

```bash
cd backend
python create_database.py --force
```

---

## Entraîner le Modèle IA

```bash
python train.py
```

---

# Exécution de l’Application

## Lancer le Backend

```bash
cd backend
python app.py
```

Serveur backend :
```text
http://127.0.0.1:5000
```

---

## Lancer le Frontend

```bash
python serve_frontend.py
```

Application :
```text
http://localhost:3000
```

---

# Endpoint API

## Analyse des Symptômes

```http
POST /api/predict/
```

### Exemple de Requête

```json
{
  "text": "fièvre et toux depuis 3 jours"
}
```

### Exemple de Réponse

```json
{
  "success": true,
  "predicted_disease": "Grippe",
  "confidence": 85
}
```

---

# Exemples de Tests

```text
J’ai une forte fièvre et une toux sèche.
J’ai une douleur dans la poitrine et du mal à respirer.
Je ressens des nausées et des douleurs abdominales.
```

---

# Limites Actuelles

- Possibles confusions entre le COVID-19 et la grippe
- Détection des migraines encore limitée
- Dataset médical restreint
- Les résultats dépendent de la qualité des symptômes saisis

---

# Améliorations Futures

- Amélioration de la précision des prédictions
- Intégration de modèles Deep Learning
- Support multilingue
- Intégration d’APIs médicales externes
- Extension du dataset médical
- Optimisation de l’analyse NLP

---

# Avertissement

Ce projet est destiné :
- à des fins éducatives,
- à l’expérimentation en intelligence artificielle,
- à la recherche en NLP.

Il ne remplace en aucun cas un diagnostic médical professionnel.

---

# Auteur

Hiba Mahroug   
Étudiante en Génie Logiciel  
Passionnée par l’IA et le NLP

GitHub :
https://github.com/HIBAMAHROUG

---

# Licence

Ce projet est sous licence MIT.
