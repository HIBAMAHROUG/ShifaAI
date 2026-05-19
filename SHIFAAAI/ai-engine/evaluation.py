"""Evaluates SHIFAAAI models and reports common ML metrics."""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.model_selection import cross_val_score, train_test_split
import warnings
warnings.filterwarnings('ignore')

class EvaluationConfig:
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    CV_FOLDS = 5
    
    METRICS = [
        'accuracy', 'precision', 'recall', 'f1',
        'sensitivity', 'specificity', 'auc_roc'
    ]
    
    PLOT_STYLE = 'seaborn-v0_8-darkgrid'
    FIGURE_SIZE = (12, 8)

class ModelEvaluator:
    def __init__(self, model=None, vectorizer=None, label_encoder=None):
        self.model = model
        self.vectorizer = vectorizer
        self.label_encoder = label_encoder
        self.results = {}
        self.predictions_history = []
    
    def load_model(self, model_path: str, vectorizer_path: str = None, encoder_path: str = None):
        import pickle
        
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Model loaded: {model_path}")
            
            if vectorizer_path:
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print(f"Vectorizer loaded: {vectorizer_path}")
            
            if encoder_path:
                with open(encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                print(f"Label encoder loaded: {encoder_path}")
            
            return True
        except Exception as e:
            print(f"Model load error: {e}")
            return False
    
    def evaluate_classification(self, y_true, y_pred, y_proba=None, 
                                labels: List[str] = None) -> Dict[str, Any]:
        """
        Évaluer un modèle de classification
        
        Args:
            y_true: Valeurs réelles
            y_pred: Prédictions
            y_proba: Probabilités (optionnel)
            labels: Liste des labels
            
        Returns:
            Dictionnaire des métriques
        """
        results = {}
        
        # Métriques de base
        results['accuracy'] = accuracy_score(y_true, y_pred)
        results['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        results['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        results['f1_score'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Rapport détaillé
        results['classification_report'] = classification_report(
            y_true, y_pred, 
            target_names=labels, 
            zero_division=0,
            output_dict=True
        )
        
        # Matrice de confusion
        results['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()
        
        # AUC-ROC si probabilités disponibles
        if y_proba is not None and len(np.unique(y_true)) == 2:
            try:
                results['auc_roc'] = roc_auc_score(y_true, y_proba[:, 1])
            except:
                results['auc_roc'] = None
        
        # Sensibilité et spécificité
        cm = confusion_matrix(y_true, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            results['sensitivity'] = tp / (tp + fn) if (tp + fn) > 0 else 0
            results['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        return results
    
    def evaluate_regression(self, y_true, y_pred) -> Dict[str, Any]:
        """
        Évaluer un modèle de régression
        
        Args:
            y_true: Valeurs réelles
            y_pred: Prédictions
            
        Returns:
            Dictionnaire des métriques
        """
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'r2': r2_score(y_true, y_pred)
        }
    
    def cross_validate(self, X, y, cv_folds: int = 5) -> Dict[str, Any]:
        """
        Validation croisée
        
        Args:
            X: Features
            y: Labels
            cv_folds: Nombre de folds
            
        Returns:
            Résultats de validation croisée
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        scoring = ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted']
        results = {}
        
        for metric in scoring:
            scores = cross_val_score(
                self.model, X, y, 
                cv=cv_folds, 
                scoring=metric,
                n_jobs=-1
            )
            results[metric] = {
                'mean': scores.mean(),
                'std': scores.std(),
                'scores': scores.tolist()
            }
        
        return results
    
    def evaluate_on_test_set(self, X_test, y_test) -> Dict[str, Any]:
        """
        Évaluer le modèle sur un ensemble de test
        
        Args:
            X_test: Features de test
            y_test: Labels réels
            
        Returns:
            Métriques d'évaluation
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        # Prédictions
        y_pred = self.model.predict(X_test)
        
        # Probabilités si disponibles
        y_proba = None
        if hasattr(self.model, 'predict_proba'):
            y_proba = self.model.predict_proba(X_test)
        
        # Métriques
        results = self.evaluate_classification(y_test, y_pred, y_proba)
        
        # Ajouter les prédictions à l'historique
        self.predictions_history.append({
            'timestamp': datetime.now().isoformat(),
            'y_true': y_test.tolist() if isinstance(y_test, np.ndarray) else y_test,
            'y_pred': y_pred.tolist(),
            'metrics': results
        })
        
        return results
    
    def analyze_errors(self, X_test, y_test, feature_names: List[str] = None) -> pd.DataFrame:
        """
        Analyser les erreurs de prédiction
        
        Args:
            X_test: Features de test
            y_test: Labels réels
            feature_names: Noms des features
            
        Returns:
            DataFrame des erreurs analysées
        """
        if self.model is None:
            raise ValueError("Modèle non chargé")
        
        y_pred = self.model.predict(X_test)
        
        # Identifier les erreurs
        errors = y_test != y_pred
        error_indices = np.where(errors)[0]
        
        error_analysis = []
        for idx in error_indices[:100]:  # Limiter pour performance
            error_info = {
                'index': idx,
                'true_label': y_test[idx],
                'predicted_label': y_pred[idx],
                'is_error': True
            }
            
            # Ajouter les features si disponibles
            if feature_names and hasattr(X_test, 'toarray'):
                features = X_test[idx].toarray()[0]
                for i, name in enumerate(feature_names[:10]):
                    if features[i] > 0:
                        error_info[f'feature_{name}'] = features[i]
            elif feature_names and isinstance(X_test, (list, np.ndarray)):
                for i, name in enumerate(feature_names[:10]):
                    if i < len(X_test[idx]):
                        error_info[f'feature_{name}'] = X_test[idx][i]
            
            error_analysis.append(error_info)
        
        return pd.DataFrame(error_analysis)

# =========================================================
# VISUALISATION DES RÉSULTATS
# =========================================================

class ResultVisualizer:
    """Visualisation des résultats d'évaluation"""
    
    def __init__(self):
        self.set_style()
    
    def set_style(self):
        """Configurer le style des graphiques"""
        try:
            plt.style.use(EvaluationConfig.PLOT_STYLE)
        except:
            pass
        sns.set_palette("husl")
    
    def plot_confusion_matrix(self, cm: np.ndarray, labels: List[str], 
                              title: str = "Matrice de Confusion"):
        """
        Afficher la matrice de confusion
        
        Args:
            cm: Matrice de confusion
            labels: Labels des classes
            title: Titre du graphique
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=labels, yticklabels=labels, ax=ax)
        
        ax.set_xlabel('Prédictions', fontsize=12)
        ax.set_ylabel('Vérités terrain', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def plot_metrics_bar(self, metrics: Dict[str, float], 
                         title: str = "Métriques de Performance"):
        """
        Afficher les métriques sous forme de barres
        
        Args:
            metrics: Dictionnaire des métriques
            title: Titre du graphique
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        
        colors = ['#2ecc71' if v > 0.7 else '#f39c12' if v > 0.5 else '#e74c3c' 
                  for v in metric_values]
        
        bars = ax.bar(metric_names, metric_values, color=colors, edgecolor='black')
        
        # Ajouter les valeurs sur les barres
        for bar, value in zip(bars, metric_values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontsize=10)
        
        ax.set_ylim(0, 1.1)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticklabels(metric_names, rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    
    def plot_cv_results(self, cv_results: Dict[str, Dict], 
                        title: str = "Résultats Validation Croisée"):
        """
        Afficher les résultats de validation croisée
        
        Args:
            cv_results: Résultats de validation croisée
            title: Titre du graphique
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        metrics = list(cv_results.keys())
        means = [cv_results[m]['mean'] for m in metrics]
        stds = [cv_results[m]['std'] for m in metrics]
        
        x = np.arange(len(metrics))
        bars = ax.bar(x, means, yerr=stds, capsize=5, color='#3498db', 
                      edgecolor='black', alpha=0.8)
        
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.1)
        
        # Ajouter les valeurs
        for bar, mean, std in zip(bars, means, stds):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{mean:.3f}±{std:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def save_plots(self, output_dir: str = "evaluation_plots"):
        """Sauvegarder tous les graphiques"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for fig_name, fig in self.figures.items():
            fig.savefig(f"{output_dir}/{fig_name}.png", dpi=150, bbox_inches='tight')
            plt.close(fig)
        
        print(f"✅ Graphiques sauvegardés dans '{output_dir}'")

# =========================================================
# TESTS ET VALIDATION
# =========================================================

class ModelTester:
    """Testeur pour le modèle SHIFAAAI"""
    
    def __init__(self, evaluator: ModelEvaluator):
        self.evaluator = evaluator
        self.test_results = []
    
    def test_with_synthetic_data(self, n_samples: int = 1000) -> Dict[str, Any]:
        """
        Tester le modèle avec des données synthétiques
        
        Args:
            n_samples: Nombre d'échantillons
            
        Returns:
            Résultats du test
        """
        from sklearn.datasets import make_classification
        
        # Générer des données synthétiques
        X, y = make_classification(
            n_samples=n_samples,
            n_features=20,
            n_informative=15,
            n_redundant=5,
            n_classes=5,
            random_state=42
        )
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=EvaluationConfig.TEST_SIZE,
            random_state=EvaluationConfig.RANDOM_STATE
        )
        
        # Entraîner un modèle simple si nécessaire
        if self.evaluator.model is None:
            from sklearn.ensemble import RandomForestClassifier
            self.evaluator.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.evaluator.model.fit(X_train, y_train)
        
        # Évaluer
        results = self.evaluator.evaluate_on_test_set(X_test, y_test)
        
        return {
            'test_type': 'synthetic',
            'n_samples': n_samples,
            'results': results
        }
    
    def test_edge_cases(self) -> List[Dict[str, Any]]:
        """
        Tester le modèle sur des cas limites
        
        Returns:
            Liste des résultats des cas limites
        """
        if self.evaluator.model is None:
            raise ValueError("Modèle non chargé")
        
        edge_cases = [
            "fièvre",
            "toux sèche",
            "mal de gorge intense",
            "texte très long avec beaucoup de mots et des symptômes répétés plusieurs fois",
            "symptômes contradictoires exemple fièvre sans fièvre",
            "mots sans aucun sens médical comme xyz abc 123"
        ]
        
        results = []
        for case in edge_cases:
            try:
                # Prédiction (à adapter selon votre interface)
                if hasattr(self.evaluator.model, 'predict'):
                    # Pour texte, besoin de vectorizer
                    if self.evaluator.vectorizer:
                        X = self.evaluator.vectorizer.transform([case])
                        pred = self.evaluator.model.predict(X)[0]
                        
                        if self.evaluator.label_encoder:
                            pred = self.evaluator.label_encoder.inverse_transform([pred])[0]
                    else:
                        pred = "Prédiction non disponible"
                else:
                    pred = "Modèle non compatible"
                
                results.append({
                    'input': case,
                    'prediction': str(pred),
                    'success': True
                })
            except Exception as e:
                results.append({
                    'input': case,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Exécuter tous les tests
        
        Returns:
            Résumé des tests
        """
        print("\n" + "="*60)
        print("🧪 EXÉCUTION DES TESTS DU MODÈLE")
        print("="*60)
        
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': []
        }
        
        # Test avec données synthétiques
        print("\n📊 Test avec données synthétiques...")
        try:
            synth_results = self.test_with_synthetic_data()
            all_results['tests'].append(synth_results)
            print(f"   ✅ Accuracy: {synth_results['results']['accuracy']:.2%}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        # Test des cas limites
        print("\n🔍 Test des cas limites...")
        try:
            edge_results = self.test_edge_cases()
            all_results['tests'].append({
                'test_type': 'edge_cases',
                'results': edge_results
            })
            success_count = sum(1 for r in edge_results if r['success'])
            print(f"   ✅ {success_count}/{len(edge_results)} cas réussis")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        
        return all_results

# =========================================================
# FONCTION PRINCIPALE D'ÉVALUATION
# =========================================================

def evaluate_model(model_path: str, test_data_path: str = None) -> Dict[str, Any]:
    """
    Évaluer le modèle SHIFAAAI
    
    Args:
        model_path: Chemin du modèle
        test_data_path: Chemin des données de test (optionnel)
        
    Returns:
        Résultats complets de l'évaluation
    """
    print("\n" + "="*60)
    print("🎯 ÉVALUATION DU MODÈLE SHIFAAAI")
    print("="*60)
    
    # Initialiser l'évaluateur
    evaluator = ModelEvaluator()
    
    # Charger le modèle
    if not evaluator.load_model(model_path):
        return {'success': False, 'error': 'Model loading failed'}
    
    # Charger les données de test
    if test_data_path:
        try:
            df = pd.read_csv(test_data_path)
            print(f"📊 Données de test chargées: {len(df)} échantillons")
            
            # Préparer les données (à adapter)
            X_test = df['symptoms'] if 'symptoms' in df.columns else None
            y_test = df['disease'] if 'disease' in df.columns else None
            
            if X_test is not None and y_test is not None:
                # Vectoriser si nécessaire
                if evaluator.vectorizer:
                    X_test_vec = evaluator.vectorizer.transform(X_test)
                    results = evaluator.evaluate_on_test_set(X_test_vec, y_test)
                else:
                    results = evaluator.evaluate_on_test_set(X_test, y_test)
                
                print(f"\n📈 Résultats:")
                print(f"   Accuracy: {results['accuracy']:.2%}")
                print(f"   F1 Score: {results['f1_score']:.2%}")
                
                return results
        except Exception as e:
            print(f"❌ Erreur chargement données: {e}")
    
    # Test avec données synthétiques
    tester = ModelTester(evaluator)
    test_results = tester.run_all_tests()
    
    return test_results

# =========================================================
# RAPPORT D'ÉVALUATION
# =========================================================

def generate_report(evaluation_results: Dict[str, Any], output_file: str = "evaluation_report.json"):
    """
    Générer un rapport d'évaluation
    
    Args:
        evaluation_results: Résultats de l'évaluation
        output_file: Fichier de sortie
    """
    report = {
        'generated_at': datetime.now().isoformat(),
        'model': 'SHIFAAAI Medical Classifier',
        'version': '2.0.0',
        'results': evaluation_results
    }
    
    # Sauvegarder
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Rapport généré: {output_file}")
    
    # Afficher un résumé
    print("\n📊 RÉSUMÉ DE L'ÉVALUATION")
    print("-" * 40)
    
    if 'accuracy' in evaluation_results:
        print(f"  Accuracy: {evaluation_results['accuracy']:.2%}")
    if 'f1_score' in evaluation_results:
        print(f"  F1 Score: {evaluation_results['f1_score']:.2%}")
    if 'precision' in evaluation_results:
        print(f"  Precision: {evaluation_results['precision']:.2%}")
    if 'recall' in evaluation_results:
        print(f"  Recall: {evaluation_results['recall']:.2%}")

# =========================================================
# MAIN
# =========================================================

def main():
    """Fonction principale"""
    
    print("\n" + "="*60)
    print("🔬 SHIFAAAI - SCRIPT D'ÉVALUATION")
    print("="*60)
    
    # Chemins par défaut
    model_path = "models/shifaa_model.pkl"
    test_data_path = "data/test_dataset.csv"
    
    # Vérifier si le modèle existe
    import os
    if not os.path.exists(model_path):
        print(f"⚠️ Modèle non trouvé: {model_path}")
        print("   Utilisation d'un modèle temporaire pour l'évaluation")
        model_path = None
    
    # Évaluer
    if model_path:
        results = evaluate_model(model_path, test_data_path)
    else:
        # Créer un évaluateur avec un modèle temporaire
        evaluator = ModelEvaluator()
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Données d'exemple
        texts = [
            "fièvre toux fatigue", "mal de gorge fièvre", "nausée vomissement",
            "maux de tête vision floue", "douleur poitrine essoufflement"
        ]
        labels = ["Grippe", "Angine", "Gastro", "Migraine", "Cardiaque"]
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(texts)
        
        model = RandomForestClassifier()
        model.fit(X, labels)
        
        evaluator.model = model
        evaluator.vectorizer = vectorizer
        
        # Tester
        tester = ModelTester(evaluator)
        results = tester.run_all_tests()
    
    # Générer rapport
    generate_report(results)
    
    print("\n✅ Évaluation terminée")

if __name__ == "__main__":
    main()
