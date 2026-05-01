# helpers.py - Fonctions utilitaires pour SHIFAAAI

import re
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import wraps
import unicodedata

# =========================================================
# VALIDATION DES DONNÉES
# =========================================================

def validate_email(email: str) -> bool:
    """
    Valider le format d'un email
    
    Args:
        email: Adresse email à valider
        
    Returns:
        True si l'email est valide, False sinon
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Valider le format d'un numéro de téléphone français
    
    Args:
        phone: Numéro de téléphone
        
    Returns:
        True si valide, False sinon
    """
    # Accepte: 0612345678, 06 12 34 56 78, +33612345678
    pattern = r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]?\d{2}){4}$'
    return bool(re.match(pattern, phone))

def validate_symptom_text(text: str) -> Tuple[bool, Optional[str]]:
    """
    Valider le texte des symptômes
    
    Args:
        text: Texte des symptômes
        
    Returns:
        (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Le texte ne peut pas être vide"
    
    if len(text) < 3:
        return False, "Le texte est trop court (minimum 3 caractères)"
    
    if len(text) > 5000:
        return False, "Le texte est trop long (maximum 5000 caractères)"
    
    # Vérifier la présence de caractères valides
    if not any(c.isalpha() for c in text):
        return False, "Le texte doit contenir au moins une lettre"
    
    return True, None

def validate_disease_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Valider le nom d'une maladie
    
    Args:
        name: Nom de la maladie
        
    Returns:
        (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Le nom ne peut pas être vide"
    
    if len(name) < 2:
        return False, "Le nom est trop court"
    
    if len(name) > 200:
        return False, "Le nom est trop long"
    
    return True, None

# =========================================================
# NORMALISATION ET NETTOYAGE
# =========================================================

def normalize_text(text: str, lower: bool = True, remove_accents: bool = True) -> str:
    """
    Normaliser le texte (minuscules, sans accents, etc.)
    
    Args:
        text: Texte à normaliser
        lower: Convertir en minuscules
        remove_accents: Supprimer les accents
        
    Returns:
        Texte normalisé
    """
    if not text:
        return ""
    
    if remove_accents:
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ASCII', 'ignore').decode('utf-8')
    
    if lower:
        text = text.lower()
    
    # Supprimer les caractères spéciaux
    text = re.sub(r'[^\w\s-]', ' ', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def clean_symptoms_list(symptoms: List[str]) -> List[str]:
    """
    Nettoyer une liste de symptômes
    
    Args:
        symptoms: Liste des symptômes
        
    Returns:
        Liste nettoyée sans doublons
    """
    if not symptoms:
        return []
    
    cleaned = []
    for s in symptoms:
        if s and isinstance(s, str):
            s_clean = normalize_text(s, lower=True, remove_accents=True)
            if s_clean and s_clean not in cleaned:
                cleaned.append(s_clean)
    
    return cleaned

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extraire les mots-clés d'un texte
    
    Args:
        text: Texte source
        min_length: Longueur minimale des mots
        
    Returns:
        Liste des mots-clés
    """
    if not text:
        return []
    
    # Stopwords communs
    stopwords = {
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou', 'donc',
        'car', 'mais', 'est', 'sont', 'a', 'au', 'aux', 'avec', 'sans', 'pour',
        'par', 'dans', 'sur', 'chez', 'entre', 'je', 'tu', 'il', 'elle', 'nous',
        'vous', 'ils', 'elles', 'ce', 'cette', 'ces', 'mon', 'ton', 'son'
    }
    
    words = normalize_text(text).split()
    keywords = [w for w in words if len(w) >= min_length and w not in stopwords]
    
    # Supprimer les doublons tout en gardant l'ordre
    seen = set()
    unique_keywords = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique_keywords.append(k)
    
    return unique_keywords

# =========================================================
# FORMATAGE DES DONNÉES
# =========================================================

def format_date(date: Union[str, datetime], format_type: str = 'fr') -> str:
    """
    Formater une date
    
    Args:
        date: Date à formater
        format_type: 'fr' (DD/MM/YYYY) ou 'iso' (YYYY-MM-DD)
        
    Returns:
        Date formatée
    """
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date)
        except ValueError:
            return date
    
    if format_type == 'fr':
        return date.strftime('%d/%m/%Y %H:%M')
    elif format_type == 'time':
        return date.strftime('%H:%M:%S')
    else:
        return date.isoformat()

def format_probability(prob: Union[int, float], decimals: int = 1) -> str:
    """
    Formater une probabilité en pourcentage
    
    Args:
        prob: Probabilité (0-100 ou 0-1)
        decimals: Nombre de décimales
        
    Returns:
        Chaîne formatée (ex: "85.5%")
    """
    if prob <= 1:
        prob *= 100
    
    return f"{prob:.{decimals}f}%"

def format_duration(seconds: int) -> str:
    """
    Formater une durée en texte lisible
    
    Args:
        seconds: Durée en secondes
        
    Returns:
        Chaîne formatée (ex: "2 jours 3 heures")
    """
    if seconds < 0:
        return "0 seconde"
    
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} jour{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} heure{'s' if hours > 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
    if secs > 0 and not parts:
        parts.append(f"{secs} seconde{'s' if secs > 1 else ''}")
    
    return ', '.join(parts) if parts else "0 seconde"

def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Tronquer un texte
    
    Args:
        text: Texte à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter
        
    Returns:
        Texte tronqué
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

# =========================================================
# ENCRYPTION ET SÉCURITÉ
# =========================================================

def hash_password(password: str) -> str:
    """
    Hasher un mot de passe
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Hash du mot de passe
    """
    salt = secrets.token_hex(16)
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() + ":" + salt

def verify_password(password: str, hashed: str) -> bool:
    """
    Vérifier un mot de passe
    
    Args:
        password: Mot de passe en clair
        hashed: Hash stocké
        
    Returns:
        True si le mot de passe est correct
    """
    try:
        hash_value, salt = hashed.split(':')
        return hash_value == hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    except:
        return False

def generate_token(length: int = 32) -> str:
    """
    Générer un token aléatoire
    
    Args:
        length: Longueur du token
        
    Returns:
        Token aléatoire
    """
    return secrets.token_hex(length)

# =========================================================
# PARSING DE TEXTE
# =========================================================

def parse_symptoms_from_text(text: str) -> List[str]:
    """
    Extraire les symptômes d'un texte
    
    Args:
        text: Texte décrivant les symptômes
        
    Returns:
        Liste des symptômes détectés
    """
    symptom_keywords = [
        'fièvre', 'toux', 'fatigue', 'douleur', 'gorge', 'nausée',
        'vomissement', 'diarrhée', 'maux de tête', 'vertige', 'essoufflement',
        'courbature', 'frisson', 'nez bouché', 'éternuement'
    ]
    
    text_lower = text.lower()
    found = []
    
    for symptom in symptom_keywords:
        if symptom in text_lower:
            found.append(symptom)
    
    return list(set(found))

def parse_duration_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extraire la durée d'un texte
    
    Args:
        text: Texte contenant une durée
        
    Returns:
        Dictionnaire avec la durée ou None
    """
    patterns = [
        (r'(\d+)\s*(?:jours?|journées?)', 'days'),
        (r'(\d+)\s*(?:heures?|h)', 'hours'),
        (r'(\d+)\s*(?:semaines?)', 'weeks'),
        (r'(\d+)\s*(?:mois)', 'months'),
        (r'(\d+)\s*(?:années?|ans?)', 'years')
    ]
    
    for pattern, unit in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return {
                'value': int(match.group(1)),
                'unit': unit,
                'text': match.group(0)
            }
    
    return None

# =========================================================
# STATISTIQUES ET CALCULS
# =========================================================

def calculate_confidence(scores: List[float]) -> float:
    """
    Calculer un score de confiance global
    
    Args:
        scores: Liste des scores individuels
        
    Returns:
        Score de confiance (0-100)
    """
    if not scores:
        return 0
    
    # Moyenne pondérée (le premier score compte plus)
    weights = [1.0 / (i + 1) for i in range(len(scores))]
    total_weight = sum(weights)
    weighted_avg = sum(s * w for s, w in zip(scores, weights)) / total_weight
    
    return min(max(weighted_avg * 100, 0), 100)

def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculer la similarité entre deux textes (ratio Jaccard)
    
    Args:
        text1: Premier texte
        text2: Deuxième texte
        
    Returns:
        Score de similarité (0-1)
    """
    set1 = set(normalize_text(text1).split())
    set2 = set(normalize_text(text2).split())
    
    if not set1 or not set2:
        return 0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0

def get_text_complexity(text: str) -> str:
    """
    Évaluer la complexité d'un texte
    
    Args:
        text: Texte à analyser
        
    Returns:
        'simple', 'moyen', ou 'complexe'
    """
    words = text.split()
    avg_word_len = sum(len(w) for w in words) / max(len(words), 1)
    unique_words = len(set(normalize_text(text).split()))
    
    if len(words) < 10 and avg_word_len < 6:
        return 'simple'
    elif len(words) < 30 and avg_word_len < 8 and unique_words < 20:
        return 'moyen'
    else:
        return 'complexe'

# =========================================================
# GESTION DES FICHIERS
# =========================================================

def load_json_file(filepath: str) -> Optional[Dict]:
    """
    Charger un fichier JSON
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        Données JSON ou None en cas d'erreur
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erreur chargement {filepath}: {e}")
        return None

def save_json_file(filepath: str, data: Dict, indent: int = 2) -> bool:
    """
    Sauvegarder des données en JSON
    
    Args:
        filepath: Chemin du fichier
        data: Données à sauvegarder
        indent: Indentation JSON
        
    Returns:
        True si réussi, False sinon
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        print(f"Erreur sauvegarde {filepath}: {e}")
        return False

# =========================================================
# DÉCORATEURS UTILES
# =========================================================

def timing_decorator(func):
    """
    Décorateur pour mesurer le temps d'exécution
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        print(f"⏱️ {func.__name__}: {elapsed:.2f}ms")
        return result
    return wrapper

def log_error(func):
    """
    Décorateur pour logger les erreurs
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Erreur dans {func.__name__}: {e}")
            raise
    return wrapper

def cache_result(ttl_seconds: int = 300):
    """
    Décorateur pour mettre en cache les résultats
    
    Args:
        ttl_seconds: Durée de vie du cache
    """
    cache = {}
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = datetime.now()
            
            if key in cache:
                result, timestamp = cache[key]
                if (now - timestamp).total_seconds() < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        return wrapper
    return decorator

# =========================================================
# EXEMPLES D'UTILISATION
# =========================================================

def demo_helpers():
    """Démonstration des fonctions helpers"""
    
    print("\n" + "="*60)
    print("🔧 TEST DES FONCTIONS HELPERS")
    print("="*60)
    
    # Validation
    print("\n📧 Validation email:")
    print(f"  test@email.com: {validate_email('test@email.com')}")
    print(f"  invalid: {validate_email('invalid')}")
    
    # Nettoyage
    print("\n🧹 Nettoyage texte:")
    text = "  J'ai une FIÈVRE élevée !!!  "
    print(f"  Original: '{text}'")
    print(f"  Normalisé: '{normalize_text(text)}'")
    
    # Extraction
    print("\n🔑 Extraction mots-clés:")
    keywords = extract_keywords("J'ai une forte fièvre et une toux sèche")
    print(f"  Mots-clés: {keywords}")
    
    # Formatage
    print("\n📊 Formatage:")
    print(f"  Probabilité: {format_probability(0.85)}")
    print(f"  Durée: {format_duration(172800)}")  # 2 jours
    print(f"  Troncature: '{truncate_text('Très long texte à tronquer', 20)}'")
    
    # Parsing
    print("\n📝 Parsing:")
    symptoms = parse_symptoms_from_text("J'ai de la fièvre et je tousse")
    print(f"  Symptômes extraits: {symptoms}")
    
    duration = parse_duration_from_text("depuis 3 jours")
    print(f"  Durée extraite: {duration}")
    
    # Calculs
    print("\n🧮 Calculs:")
    confidence = calculate_confidence([0.9, 0.7, 0.5])
    print(f"  Confiance: {confidence:.1f}%")
    
    similarity = calculate_similarity("fièvre toux", "toux fièvre")
    print(f"  Similarité: {similarity:.2f}")
    
    complexity = get_text_complexity("Je présente une fièvre élevée associée à une toux sèche persistante depuis plusieurs jours")
    print(f"  Complexité: {complexity}")

if __name__ == "__main__":
    demo_helpers()
    
    print("\n" + "="*60)
    print("📦 HELPER FUNCTIONS DISPONIBLES")
    print("="*60)
    print("""
    Validation:
        validate_email() - Valider email
        validate_phone() - Valider téléphone
        validate_symptom_text() - Valider texte symptômes
    
    Nettoyage:
        normalize_text() - Normaliser texte
        clean_symptoms_list() - Nettoyer liste symptômes
        extract_keywords() - Extraire mots-clés
    
    Formatage:
        format_date() - Formater date
        format_probability() - Formater probabilité
        format_duration() - Formater durée
        truncate_text() - Tronquer texte
    
    Sécurité:
        hash_password() - Hasher mot de passe
        verify_password() - Vérifier mot de passe
        generate_token() - Générer token
    
    Parsing:
        parse_symptoms_from_text() - Extraire symptômes
        parse_duration_from_text() - Extraire durée
    
    Calculs:
        calculate_confidence() - Calculer confiance
        calculate_similarity() - Calculer similarité
        get_text_complexity() - Évaluer complexité
    
    Fichiers:
        load_json_file() - Charger JSON
        save_json_file() - Sauvegarder JSON
    """)