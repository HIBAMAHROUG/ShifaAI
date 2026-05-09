# SHIFAAAI
## AI-Powered Medical Symptom Analysis Platform

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Flask](https://img.shields.io/badge/Flask-2.3-red.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

---

# Overview

SHIFAAAI is an artificial intelligence platform designed to analyze medical symptoms written in natural language and predict possible diseases using Natural Language Processing (NLP) and Machine Learning techniques.

The application processes user input through several stages including:
- tokenization,
- lexical analysis,
- syntax analysis,
- symptom extraction,
- prediction generation.

The objective of the project is to combine AI technologies with healthcare assistance in a simple and interactive environment.

---

# Main Features

## Lexical Analysis
- Tokenization of text
- Symptom detection
- Negation detection
- Intensity detection
- Temporal expression extraction

Examples:
- "no fever"
- "strong headache"
- "since yesterday"

---

## Syntax Analysis
- POS Tagging
- Sentence structure analysis
- Word classification
- Grammatical relation analysis

---

## Disease Prediction
The system predicts possible diseases such as:
- Influenza
- Bronchitis
- Angina
- Gastroenteritis
- Respiratory infections

Each prediction includes:
- confidence score,
- probability estimation,
- medical recommendation.

---

# AI Processing Pipeline

```text
User Input
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

# Project Architecture

```text
Frontend (HTML / CSS / JavaScript)
            ↓
Flask REST API
            ↓
NLP Processing Layer
            ↓
Machine Learning Engine
            ↓
SQLite Database
```

---

# Technologies Used

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

# Project Structure

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

# Installation

## Clone the Repository

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

### Linux / Mac

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

## Create Database

```bash
cd backend
python create_database.py --force
```

---

## Train AI Model

```bash
python train.py
```

---

# Running the Application

## Start Backend

```bash
cd backend
python app.py
```

Backend server:
```text
http://127.0.0.1:5000
```

---

## Start Frontend

```bash
cd frontend
python -m http.server 3000
```

Frontend:
```text
http://localhost:3000
```

---

# API Endpoint

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

# Example Inputs

```text
I have a strong fever and dry cough.
I have chest pain and difficulty breathing.
I feel nauseous and have stomach pain.
```

---

# Current Limitations

- Possible confusion between COVID-19 and influenza symptoms
- Migraine detection is not always accurate
- Limited medical dataset
- Predictions depend on user symptom descriptions

---

# Future Improvements

- Improve prediction accuracy
- Add deep learning models
- Add multilingual support
- Integrate external medical APIs
- Improve symptom classification
- Expand disease dataset

---

# Disclaimer

This project is intended for:
- educational purposes,
- AI experimentation,
- NLP research.

It does not replace professional medical diagnosis or healthcare services.

---

# Author

Hiba Zaroui  
Software Engineering Student  
AI & NLP Enthusiast

GitHub:
https://github.com/HIBAMAHROUG

---

# License

This project is licensed under the MIT License.
