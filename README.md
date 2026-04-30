# ShifaAI
# 🏥 SHIFAAAI - Plateforme d'Analyse Médicale par Intelligence Artificielle

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/HIBAMAHROUG/ShifaaAI)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 📋 Table des Matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Démarrage Rapide](#démarrage-rapide)
- [Utilisation](#utilisation)
- [API Endpoints](#api-endpoints)
- [Structure du Projet](#structure-du-projet)
- [Technologies](#technologies)
- [Dépannage](#dépannage)
- [Contributions](#contributions)
- [Licence](#licence)

---

## 🎯 Aperçu

**ShifaaAI** (signifiant "guérison" en arabe) est une plateforme innovante d'analyse médicale qui utilise le **Traitement du Langage Naturel (NLP)** et l'**Intelligence Artificielle** pour analyser les symptômes décrits en langage naturel et prédire les maladies probables.

L'application décompose le texte en **tokens**, effectue une **analyse lexicale** (détection des symptômes, négations, intensificateurs), une **analyse syntaxique** (POS tagging), puis génère une **prédiction** avec un score de confiance et des recommandations médicales.

---

## ✨ Fonctionnalités

### 🔤 Analyse Lexicale Avancée
- **Tokenisation** : Découpage du texte en unités lexicales
- **Détection des symptômes** : Reconnaissance automatique des termes médicaux
- **Identification des négations** : "pas de fièvre", "sans douleur"
- **Intensificateurs** : "très forte fièvre", "légère douleur"
- **Extraction temporelle** : "depuis 3 jours", "hier"

### 📐 Analyse Syntaxique
- **POS Tagging** : Classification grammaticale des mots (VERBE, NOM, DÉTERMINANT, PRÉPOSITION)
- **Structure de phrase** : Visualisation de l'arbre syntaxique
- **Relations grammaticales** : Identification des fonctions syntaxiques

### 🩺 Prédiction Médicale
- **Classification des maladies** : Grippe, Bronchite, Angine, Gastro-entérite
- **Score de confiance** : Pourcentage de fiabilité de la prédiction
- **Recommandations personnalisées** : Conseils médicaux adaptés

### 🎨 Interface Utilisateur
- **Design moderne** : Glassmorphism, animations fluides
- **Responsive** : Adapté à tous les écrans (mobile, tablette, desktop)
- **Feedback visuel** : Spinner de chargement, notifications
- **Accessibilité** : Haut contraste, couleurs distinctes

---

## 🏗 Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ HTML5 │ │ CSS3 │ │ JavaScript (ES6) │ │
│ │ Structure │ │ Styles │ │ Interactions │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Flask API │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ Routes │ │ Services │ │ Models │ │ │
│ │ │ (REST) │ │ (NLP/ML) │ │ (ML) │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ BASE DE DONNÉES │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ SQLite │ │
│ │ users │ symptoms │ diseases │ analyses │ feedback │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prérequis

- **Python 3.10 ou supérieur**
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel)

### Étape 1 : Cloner le dépôt

```bash
git clone https://github.com/HIBAMAHROUG/ShifaaAI.git
cd ShifaaAI
```

### Étape 2 : Créer l'environnement virtuel
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Étape 3 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 : Créer la base de données
```bash
cd backend
python create_database.py --force
```

### Étape 5 : Entraîner le modèle IA (optionnel)
```bash
python train.py
```

---

## 🚀 Démarrage Rapide

### Lancer le Backend
```bash
cd backend
python app.py
```
Le serveur démarre sur http://127.0.0.1:5000

### Lancer le Frontend
```bash
cd frontend
python -m http.server 3000
```

Ouvrez votre navigateur : http://localhost:3000

---

## 💻 Utilisation

1. **Saisie des symptômes** :
   - Dans la zone de texte, décrivez vos symptômes en langage naturel :
     > Je tousse depuis une semaine, j'ai du mal à respirer et une douleur dans la poitrine.
2. **Analyse** :
   - Cliquez sur "Analyser les symptômes" ou pressez Ctrl + Entrée
3. **Résultats** :
   - Analyse Lexicale : Tokens colorés par type
   - Statistiques : Nombre de symptômes, négations, intensificateurs
   - Analyse Syntaxique : Tableau des POS tags
   - Structure de phrase : Arbre syntaxique
   - Prédiction : Maladie + score de confiance + recommandation

### Exemples de phrases de test
```
1. J'ai une forte fièvre, une toux sèche et je suis fatigué depuis 3 jours.
2. J'ai mal à la gorge et j'ai du mal à avaler.
3. Je vomis depuis cette nuit, j'ai mal au ventre et je n'arrête pas d'aller aux toilettes.
4. J'ai du mal à respirer et j'ai une douleur dans la poitrine.
```

---

## 🔌 API Endpoints

| Méthode | Endpoint           | Description                        |
|---------|--------------------|------------------------------------|
| GET     | /health            | Vérification de l'état du serveur   |
| GET     | /info              | Informations sur l'API             |
| POST    | /api/predict/      | Analyse et prédiction des symptômes|

#### Exemple d'appel API
```bash
curl -X POST http://127.0.0.1:5000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "fièvre et toux depuis 3 jours"}'
```

#### Réponse attendue
```json
{
  "success": true,
  "input_text": "fièvre et toux depuis 3 jours",
  "predicted_disease": "Grippe",
  "confidence": 85,
  "probability": "85.0%"
}
```

---

## 📁 Structure du Projet
```
ShifaaAI/
├── backend/
│   ├── app.py                 # Point d'entrée Flask
│   ├── create_database.py     # Script création DB
│   ├── train.py               # Script entraînement ML
│   ├── requirements.txt       # Dépendances Python
│   ├── models/                # Modèles IA sauvegardés
│   └── data/                  # Données d'entraînement
│
├── frontend/
│   ├── index.html             # Page principale
│   ├── style.css              # Styles CSS
│   └── script.js              # JavaScript
│
├── README.md                  # Documentation
└── LICENSE                    # Licence
```

---

## 🛠 Technologies

### Frontend

| Technologie   | Version | Utilisation                  |
|--------------|---------|------------------------------|
| HTML5        | -       | Structure de la page         |
| CSS3         | -       | Styles et animations         |
| JavaScript   | ES6     | Logique métier et interactions|
| Bootstrap    | 5.3.3   | Composants UI responsives    |
| Font Awesome | 6.5.1   | Icônes vectorielles          |

### Backend

| Technologie   | Version | Utilisation                  |
|--------------|---------|------------------------------|
| Python       | 3.10+   | Langage principal            |
| Flask        | 2.3.0   | Framework web                |
| Flask-CORS   | 4.0.0   | Gestion CORS                 |
| SQLite       | 3       | Base de données légère       |

### Machine Learning

| Technologie   | Version | Utilisation                  |
|--------------|---------|------------------------------|
| scikit-learn | 1.3.0   | Modèles ML                   |
| pandas       | 2.0.3   | Manipulation données         |
| numpy        | 1.24.3  | Calculs numériques           |

---

## 🐛 Dépannage

**Erreur : ModuleNotFoundError: No module named 'flask'**
```bash
pip install flask flask-cors
```

**Erreur : ImportError: cannot import name 'main'**
Vérifiez que vous utilisez la bonne version de Python :
```bash
python --version  # Doit être 3.10+
```

**Erreur : Address already in use**
Changez le port dans app.py :
```python
app.run(host='127.0.0.1', port=5001, debug=True)
```

**Le frontend ne communique pas avec le backend**
Vérifiez que le backend tourne : http://127.0.0.1:5000/health

Vérifiez que l'URL dans script.js est correcte :
```javascript
const API_URL = 'http://127.0.0.1:5000/api/predict/';
```

---

## 🤝 Contributions

Les contributions sont les bienvenues ! Voici comment contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push sur la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

### Convention de commit
- feat: Nouvelle fonctionnalité
- fix: Correction de bug
- docs: Documentation
- style: Formatage
- refactor: Refactorisation
- test: Tests
- chore: Maintenance

---

## 📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 👥 Équipe
Lead Developer - @HIBAMAHROUG
NLP Engineer - [Contributor Name]
UI/UX Designer - [Contributor Name]

## 📞 Contact
Pour toute question ou suggestion :

Email : contact@shifaaai.com
GitHub Issues : https://github.com/HIBAMAHROUG/ShifaaAI/issues
Site web : https://shifaaai.com

## 🙏 Remerciements
Université - Pour le support académique
Communauté Open Source - Pour les bibliothèques utilisées
Tous les testeurs - Pour leurs retours précieux

<p align="center"> <strong>© 2026 ShifaaAI - Intelligence Artificielle pour la Santé</strong><br> <i>"La santé est un droit, l'IA est l'outil"</i> </p>
# 🏥 SHIFAAAI - Plateforme d'Analyse Médicale par Intelligence Artificielle

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/your-username/shifaaai)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 📋 Table des Matières

- [Aperçu](#aperçu)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Démarrage Rapide](#démarrage-rapide)
- [Utilisation](#utilisation)
- [API Endpoints](#api-endpoints)
- [Structure du Projet](#structure-du-projet)
- [Technologies](#technologies)
- [Dépannage](#dépannage)
- [Captures d'écran](#captures-décran)
- [Contributions](#contributions)
- [Licence](#licence)

---

## 🎯 Aperçu

**ShifaaAI** (signifiant "guérison" en arabe) est une plateforme innovante d'analyse médicale qui utilise le **Traitement du Langage Naturel (NLP)** et l'**Intelligence Artificielle** pour analyser les symptômes décrits en langage naturel et prédire les maladies probables.

L'application décompose le texte en **tokens**, effectue une **analyse lexicale** (détection des symptômes, négations, intensificateurs), une **analyse syntaxique** (POS tagging), puis génère une **prédiction** avec un score de confiance et des recommandations médicales.

![ShifaaAI Demo](https://via.placeholder.com/800x400?text=ShifaaAI+Interface)

---

## ✨ Fonctionnalités

### 🔤 Analyse Lexicale Avancée
- **Tokenisation** : Découpage du texte en unités lexicales
- **Détection des symptômes** : Reconnaissance automatique des termes médicaux
- **Identification des négations** : "pas de fièvre", "sans douleur"
- **Intensificateurs** : "très forte fièvre", "légère douleur"
- **Extraction temporelle** : "depuis 3 jours", "hier"

### 📐 Analyse Syntaxique
- **POS Tagging** : Classification grammaticale des mots (VERBE, NOM, DÉTERMINANT, PRÉPOSITION)
- **Structure de phrase** : Visualisation de l'arbre syntaxique
- **Relations grammaticales** : Identification des fonctions syntaxiques

### 🩺 Prédiction Médicale
- **Classification des maladies** : Grippe, Bronchite, Angine, Gastro-entérite
- **Score de confiance** : Pourcentage de fiabilité de la prédiction
- **Recommandations personnalisées** : Conseils médicaux adaptés

### 🎨 Interface Utilisateur
- **Design moderne** : Glassmorphism, animations fluides
- **Responsive** : Adapté à tous les écrans (mobile, tablette, desktop)
- **Feedback visuel** : Spinner de chargement, notifications
- **Accessibilité** : Haut contraste, couleurs distinctes

---

## 🏗 Architecture
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ HTML5 │ │ CSS3 │ │ JavaScript (ES6) │ │
│ │ Structure │ │ Styles │ │ Interactions │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Flask API │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │ Routes │ │ Services │ │ Models │ │ │
│ │ │ (REST) │ │ (NLP/ML) │ │ (ML) │ │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ BASE DE DONNÉES │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ SQLite │ │
│ │ users │ symptoms │ diseases │ analyses │ feedback │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

text

---

## 📦 Installation

### Prérequis

- **Python 3.10 ou supérieur**
- **pip** (gestionnaire de paquets Python)
- **Git** (optionnel)

### Étape 1 : Cloner le dépôt

```bash
git clone https://github.com/your-username/shifaaai.git
cd shifaaai
Étape 2 : Créer l'environnement virtuel
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
Étape 3 : Installer les dépendances
bash
pip install -r requirements.txt
Étape 4 : Créer la base de données
bash
cd backend
python create_database.py --force
Étape 5 : Entraîner le modèle IA (optionnel)
bash
python train.py
🚀 Démarrage Rapide
Lancer le Backend
bash
cd backend
python app.py
Le serveur démarre sur http://127.0.0.1:5000

Lancer le Frontend
bash
cd frontend
python -m http.server 3000
Accéder à l'application
Ouvrez votre navigateur : http://localhost:3000

💻 Utilisation
1. Saisie des symptômes
Dans la zone de texte, décrivez vos symptômes en langage naturel :

text
Je tousse depuis une semaine, j'ai du mal à respirer et une douleur dans la poitrine.
2. Analyse
Cliquez sur "Analyser les symptômes" ou pressez Ctrl + Entrée

3. Résultats
L'application affiche :

Analyse Lexicale : Tokens colorés par type

Statistiques : Nombre de symptômes, négations, intensificateurs

Analyse Syntaxique : Tableau des POS tags

Structure de phrase : Arbre syntaxique

Prédiction : Maladie + score de confiance + recommandation

Exemples de phrases de test
text
1. J'ai une forte fièvre, une toux sèche et je suis fatigué depuis 3 jours.
2. J'ai mal à la gorge et j'ai du mal à avaler.
3. Je vomis depuis cette nuit, j'ai mal au ventre et je n'arrête pas d'aller aux toilettes.
4. J'ai du mal à respirer et j'ai une douleur dans la poitrine.
🔌 API Endpoints
Endpoints disponibles
Méthode	Endpoint	Description
GET	/health	Vérification de l'état du serveur
GET	/info	Informations sur l'API
POST	/api/predict/	Analyse et prédiction des symptômes
Exemple d'appel API
bash
curl -X POST http://127.0.0.1:5000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "fièvre et toux depuis 3 jours"}'
Réponse attendue
json
{
  "success": true,
  "input_text": "fièvre et toux depuis 3 jours",
  "predicted_disease": "Grippe",
  "confidence": 85,
  "probability": "85.0%"
}
📁 Structure du Projet
text
shifaaai/
├── backend/
│   ├── app.py                 # Point d'entrée Flask
│   ├── app_simple.py          # Version simplifiée
│   ├── create_database.py     # Script création DB
│   ├── train.py               # Script entraînement ML
│   ├── requirements.txt       # Dépendances Python
│   ├── models/                # Modèles IA sauvegardés
│   │   └── shifaa_model.pkl
│   └── data/                  # Données d'entraînement
│       └── dataset.csv
│
├── frontend/
│   ├── index.html             # Page principale
│   ├── style.css              # Styles CSS
│   └── script.js              # JavaScript
│
├── README.md                  # Documentation
└── LICENSE                    # Licence
🛠 Technologies
Frontend
Technologie	Version	Utilisation
HTML5	-	Structure de la page
CSS3	-	Styles et animations
JavaScript	ES6	Logique métier et interactions
Bootstrap	5.3.3	Composants UI responsives
Font Awesome	6.5.1	Icônes vectorielles
Backend
Technologie	Version	Utilisation
Python	3.10+	Langage principal
Flask	2.3.0	Framework web
Flask-CORS	4.0.0	Gestion CORS
SQLite	3	Base de données légère
Machine Learning
Technologie	Version	Utilisation
scikit-learn	1.3.0	Modèles ML
pandas	2.0.3	Manipulation données
numpy	1.24.3	Calculs numériques
🐛 Dépannage
Erreur : ModuleNotFoundError: No module named 'flask'
bash
pip install flask flask-cors
Erreur : ImportError: cannot import name 'main'
Vérifiez que vous utilisez la bonne version de Python :

bash
python --version  # Doit être 3.10+
Erreur : Address already in use
Changez le port dans app.py :

python
app.run(host='127.0.0.1', port=5001, debug=True)
Le frontend ne communique pas avec le backend
Vérifiez que le backend tourne : http://127.0.0.1:5000/health

Vérifiez que l'URL dans script.js est correcte :

javascript
const API_URL = 'http://127.0.0.1:5000/api/predict/';
🤝 Contributions
Les contributions sont les bienvenues ! Voici comment contribuer :

Fork le projet

Créez une branche (git checkout -b feature/amazing-feature)

Commit vos changements (git commit -m 'Add amazing feature')

Push sur la branche (git push origin feature/amazing-feature)

Ouvrez une Pull Request

Convention de commit
feat: Nouvelle fonctionnalité

fix: Correction de bug

docs: Documentation

style: Formatage

refactor: Refactorisation

test: Tests

chore: Maintenance

📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

👥 Équipe
Lead Developer - @your-username

NLP Engineer - [Contributor Name]

UI/UX Designer - [Contributor Name]

📞 Contact
Pour toute question ou suggestion :

Email : contact@shifaaai.com

GitHub Issues : https://github.com/your-username/shifaaai/issues

Site web : https://shifaaai.com

🙏 Remerciements
Université - Pour le support académique

Communauté Open Source - Pour les bibliothèques utilisées

Tous les testeurs - Pour leurs retours précieux

<p align="center"> <strong>© 2026 ShifaaAI - Intelligence Artificielle pour la Santé</strong><br> <i>"La santé est un droit, l'IA est l'outil"</i> </p> ```
