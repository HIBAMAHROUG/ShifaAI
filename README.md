# 🏥 SHIFAAAI
## AI-Powered Medical Symptom Analysis Platform

<p align="center">
  <img src="https://img.shields.io/badge/version-3.0.0-blue.svg">
  <img src="https://img.shields.io/badge/python-3.10+-green.svg">
  <img src="https://img.shields.io/badge/Flask-2.3-red.svg">
  <img src="https://img.shields.io/badge/AI-NLP-purple.svg">
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg">
</p>

---

# 📌 Overview

**SHIFAAAI** is an AI-powered medical analysis platform that combines:

- 🧠 Natural Language Processing (NLP)
- 🤖 Machine Learning
- 🩺 Medical symptom analysis
- 🌐 REST API architecture

The platform analyzes symptoms written in natural language and predicts potential diseases with confidence scores and medical recommendations.

Example:

> “I have a strong fever, dry cough, and fatigue for 3 days.”

The system processes the sentence using:
- lexical analysis,
- tokenization,
- syntax analysis,
- symptom extraction,
- AI prediction models.

---

# ✨ Features

## 🔤 NLP & Lexical Analysis

- Tokenization
- Symptom extraction
- Negation detection
- Temporal expression analysis
- Severity/intensity detection

Example:
- “no fever”
- “very strong headache”
- “since yesterday”

---

## 📐 Syntax Analysis

- POS Tagging
- Sentence structure analysis
- Grammar visualization
- Lexical categorization

---

## 🩺 AI Medical Prediction

The system predicts diseases such as:

- Influenza
- Bronchitis
- Angina
- Gastroenteritis
- Respiratory infections

Includes:
- Confidence score
- Probability estimation
- Personalized recommendations

---

# 🧠 AI Pipeline

```text
User Symptoms
      ↓
Tokenization
      ↓
Lexical Analysis
      ↓
Syntax Analysis
      ↓
Feature Extraction
      ↓
Machine Learning Model
      ↓
Disease Prediction
```

---

# 🏗️ Project Architecture

```text
Frontend (HTML/CSS/JS)
        ↓
Flask REST API
        ↓
NLP Processing Layer
        ↓
ML Prediction Engine
        ↓
SQLite Database
```

---

# 💻 Technologies Used

## Frontend
- HTML5
- CSS3
- JavaScript ES6
- Bootstrap 5
- Font Awesome

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

# 📁 Project Structure

```text
SHIFAAAI/
│
├── backend/
│   ├── app.py
│   ├── train.py
│   ├── create_database.py
│   ├── models/
│   └── data/
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── README.md
└── LICENSE
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/HIBAMAHROUG/ShifaaAI.git
cd ShifaaAI
```

---

## Create Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backend

```bash
cd backend
python app.py
```

Server:
```text
http://127.0.0.1:5000
```

---

## Run Frontend

```bash
cd frontend
python -m http.server 3000
```

Application:
```text
http://localhost:3000
```

---

# 🔌 API Endpoint

## Predict Symptoms

```http
POST /api/predict/
```

### Example Request

```json
{
  "text": "fever and cough for 3 days"
}
```

### Example Response

```json
{
  "success": true,
  "predicted_disease": "Influenza",
  "confidence": 85
}
```

---

# 🧪 Example Inputs

```text
I have a strong fever and dry cough.
I have chest pain and difficulty breathing.
I feel nauseous and have stomach pain.
```

---

# 🚀 Future Improvements

- Deep Learning integration
- Better migraine detection
- Improved COVID/Flu differentiation
- Arabic language support
- Medical chatbot integration
- Real-time medical APIs

---

# ⚠️ Disclaimer

This project is for:
- educational purposes,
- AI experimentation,
- NLP research.

It is NOT intended to replace professional medical diagnosis.

---

# 👩‍💻 Author

## Hiba Zaroui
Software Engineering Student  
AI & NLP Enthusiast

GitHub:
https://github.com/HIBAMAHROUG

---

# 📜 License

This project is licensed under the MIT License.

---

# ❤️ SHIFAAAI

> “Artificial Intelligence for Better Healthcare”
