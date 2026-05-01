// api.js - Version améliorée

// Utiliser l'API Flask réelle
const API_URL = "http://127.0.0.1:5000/api/analyze";

// Configuration de l'API
const API_CONFIG = {
    timeout: 30000, // 30 secondes
    retries: 3,
    retryDelay: 1000
};

/*
|--------------------------------------------------------------------------
| Send Symptoms To Backend
|--------------------------------------------------------------------------
*/

async function sendSymptoms(symptoms) {
    // Validation des entrées
    if (!symptoms || symptoms.trim() === "") {
        showToast("Veuillez saisir des symptômes à analyser.", "error");
        return null;
    }

    try {
        showLoading("Analyse IA en cours...", "Le modèle NLP analyse vos symptômes");

        // Appel API avec timeout et retry
        const data = await fetchWithRetry(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                text: symptoms,
                timestamp: new Date().toISOString()
            })
        });

        console.log("✅ Réponse API reçue :", data);
        console.log("⏱️ Temps de réponse :", data.processing_time || "N/A");

        hideLoading();

        // Afficher les résultats
        displayResults(data);

        // Afficher un résumé dans la console
        displayConsoleSummary(data, symptoms);

        return data;

    } catch (error) {
        hideLoading();
        
        console.error("❌ Erreur API :", error);
        
        // Gérer les différents types d'erreurs
        handleApiError(error);
        
        return null;
    }
}

/*
|--------------------------------------------------------------------------
| Fetch avec retry et timeout
|--------------------------------------------------------------------------
*/

async function fetchWithRetry(url, options, retries = API_CONFIG.retries) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
        }
        
        const data = await response.json();
        
        // Vérifier si la réponse contient une erreur
        if (data.error) {
            throw new Error(data.error);
        }
        
        return data;
        
    } catch (error) {
        clearTimeout(timeoutId);
        
        if (error.name === 'AbortError') {
            throw new Error("Délai d'attente dépassé. Le serveur met trop de temps à répondre.");
        }
        
        if (retries > 0 && error.message.includes("Failed to fetch")) {
            console.log(`🔄 Nouvelle tentative... (${API_CONFIG.retries - retries + 1}/${API_CONFIG.retries})`);
            await delay(API_CONFIG.retryDelay);
            return fetchWithRetry(url, options, retries - 1);
        }
        
        throw error;
    }
}

/*
|--------------------------------------------------------------------------
| Affichage des résultats
|--------------------------------------------------------------------------
*/

function displayResults(data) {
    // Nettoyer les anciens affichages
    clearAllDisplays();
    
    // Afficher l'analyse lexicale
    if (data.tokens) {
        displayLexical(data.tokens, {
            totalWords: data.tokens.length,
            symptomsCount: data.symptoms_count || data.tokens.filter(t => 
                ["fièvre", "toux", "gorge", "fatigue", "douleur"].includes(t.toLowerCase())
            ).length,
            uniqueTerms: new Set(data.tokens).size
        });
    }
    
    // Afficher l'analyse syntaxique
    if (data.syntax) {
        displaySyntax(data.syntax, {
            intensifiersCount: data.intensifiers_count || 0,
            connectorsCount: data.connectors_count || 0,
            symptomGroupsCount: data.symptom_groups || 0
        });
    }
    
    // Afficher les maladies prédites
    if (data.diseases || data.predictions) {
        const predictionResult = {
            topPrediction: data.top_prediction || (data.diseases ? data.diseases[0] : null),
            predictions: data.diseases || data.predictions || [],
            recommendations: data.recommendations || generateFallbackRecommendations(data),
            requiresImmediateConsultation: data.requires_consultation || false,
            analysisTimestamp: data.timestamp || new Date().toLocaleString()
        };
        displayDiseases(predictionResult);
    }
    
    // Afficher la visualisation du pipeline
    if (data.pipeline) {
        displayPipeline(data.pipeline, data.processing_time);
    } else if (data.processing_steps) {
        displayPipeline(data.processing_steps, data.processing_time);
    }
    
    // Afficher la confiance globale
    if (data.confidence_score) {
        displayConfidenceScore(data.confidence_score);
    }
    
    // Scroll vers les résultats
    scrollToResults();
}

/*
|--------------------------------------------------------------------------
| Loading UI amélioré
|--------------------------------------------------------------------------
*/

function showLoading(message = "Analyse IA en cours...", subtitle = null) {
    let loader = document.getElementById("loader");
    
    if (!loader) {
        loader = document.createElement("div");
        loader.id = "loader";
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(8px);
            z-index: 9998;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        `;
        
        loader.innerHTML = `
            <div class="text-center" style="animation: pulse 1.5s infinite;">
                <div class="spinner-border text-primary mb-3" role="status" style="width: 50px; height: 50px;">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <h4 class="text-white mb-2">${message}</h4>
                ${subtitle ? `<p class="text-muted mb-0">${subtitle}</p>` : ''}
                <div class="mt-3">
                    <div class="progress" style="width: 250px; height: 4px; background: #1e293b;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" 
                             role="progressbar" 
                             style="width: 100%; background: linear-gradient(90deg, #8b5cf6, #c4b5fd);">
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(loader);
    } else {
        // Mettre à jour le message si le loader existe déjà
        const titleEl = loader.querySelector("h4");
        const subtitleEl = loader.querySelector("p");
        if (titleEl) titleEl.textContent = message;
        if (subtitleEl && subtitle) subtitleEl.textContent = subtitle;
    }
}

function hideLoading() {
    const loader = document.getElementById("loader");
    if (loader) {
        loader.style.animation = "fadeOut 0.3s ease";
        setTimeout(() => {
            if (loader && loader.parentNode) loader.remove();
        }, 300);
    }
}

/*
|--------------------------------------------------------------------------
| Pipeline Visualization améliorée
|--------------------------------------------------------------------------
*/

function displayPipeline(pipeline, processingTime = null) {
    let section = document.getElementById("pipeline-section");
    
    if (!section) {
        section = document.createElement("div");
        section.id = "pipeline-section";
        section.className = "container mt-4 mb-5";
        section.style.opacity = "0";
        section.style.transform = "translateY(20px)";
        
        const diseaseSection = document.getElementById("disease-section");
        if (diseaseSection && diseaseSection.parentNode) {
            diseaseSection.parentNode.insertBefore(section, diseaseSection.nextSibling);
        } else {
            document.body.appendChild(section);
        }
    }
    
    // Icônes pour chaque étape du pipeline
    const stepIcons = {
        "tokenization": "fa-solid fa-language",
        "lexical": "fa-solid fa-book",
        "syntaxique": "fa-solid fa-diagram-project",
        "syntax": "fa-solid fa-code-branch",
        "prediction": "fa-solid fa-microchip",
        "ner": "fa-solid fa-tags",
        "classification": "fa-solid fa-chart-line",
        "default": "fa-solid fa-gear"
    };
    
    const stepsHtml = (Array.isArray(pipeline) ? pipeline : []).map((step, index) => {
        const stepLower = step.toLowerCase();
        let icon = stepIcons.default;
        let color = "#8b5cf6";
        
        for (const [key, value] of Object.entries(stepIcons)) {
            if (stepLower.includes(key)) {
                icon = value;
                break;
            }
        }
        
        if (stepLower.includes("token")) color = "#10b981";
        if (stepLower.includes("syntax")) color = "#f59e0b";
        if (stepLower.includes("prediction") || stepLower.includes("classification")) color = "#8b5cf6";
        
        return `
            <div class="d-flex align-items-center">
                <div class="p-3 rounded-circle bg-dark text-center" style="min-width: 70px; background: ${color}20 !important; border: 1px solid ${color}40;">
                    <i class="${icon}" style="color: ${color}; font-size: 24px;"></i>
                    <div class="small mt-1" style="color: ${color};">${step}</div>
                </div>
                ${index < pipeline.length - 1 ? `
                    <div class="mx-2">
                        <i class="fa-solid fa-arrow-right text-muted"></i>
                    </div>
                ` : ''}
            </div>
        `;
    }).join("");
    
    section.innerHTML = `
        <div class="card bg-dark text-white border-0 shadow-lg" style="background: rgba(17, 24, 39, 0.9) !important; backdrop-filter: blur(10px); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 20px;">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center mb-4 flex-wrap">
                    <h3 class="mb-0" style="color: #8b5cf6;">
                        <i class="fa-solid fa-chart-line me-2"></i>
                        Pipeline de Traitement IA
                    </h3>
                    ${processingTime ? `
                        <span class="badge bg-primary px-3 py-2">
                            <i class="fa-regular fa-clock me-1"></i> ${processingTime}ms
                        </span>
                    ` : ''}
                </div>
                
                <div class="d-flex flex-wrap align-items-center justify-content-center gap-2">
                    ${stepsHtml || `
                        <div class="text-center w-100 py-4">
                            <i class="fa-solid fa-microchip fa-3x text-primary mb-3"></i>
                            <p class="text-muted mb-0">Traitement NLP en cours...</p>
                        </div>
                    `}
                </div>
                
                <div class="mt-4 pt-3 border-top border-secondary">
                    <div class="row text-center g-3">
                        <div class="col-4">
                            <small class="text-muted">Étape 1</small>
                            <p class="mb-0 small">Prétraitement</p>
                        </div>
                        <div class="col-4">
                            <small class="text-muted">Étape 2</small>
                            <p class="mb-0 small">Analyse NLP</p>
                        </div>
                        <div class="col-4">
                            <small class="text-muted">Étape 3</small>
                            <p class="mb-0 small">Prédiction</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Animation d'entrée
    setTimeout(() => {
        section.style.transition = "all 0.5s ease";
        section.style.opacity = "1";
        section.style.transform = "translateY(0)";
    }, 100);
}

/*
|--------------------------------------------------------------------------
| Afficher le score de confiance
|--------------------------------------------------------------------------
*/

function displayConfidenceScore(score) {
    let section = document.getElementById("confidence-section");
    
    if (!section) {
        section = document.createElement("div");
        section.id = "confidence-section";
        section.className = "container mt-4";
        
        const pipelineSection = document.getElementById("pipeline-section");
        if (pipelineSection && pipelineSection.parentNode) {
            pipelineSection.parentNode.insertBefore(section, pipelineSection.nextSibling);
        } else {
            document.body.appendChild(section);
        }
    }
    
    const percentage = typeof score === 'number' ? score : (score * 100);
    let color = "#10b981";
    let label = "Confiance élevée";
    
    if (percentage < 50) {
        color = "#ef4444";
        label = "Confiance faible";
    } else if (percentage < 75) {
        color = "#f59e0b";
        label = "Confiance moyenne";
    }
    
    section.innerHTML = `
        <div class="card bg-dark text-white border-0 shadow-lg" style="background: rgba(17, 24, 39, 0.9) !important; backdrop-filter: blur(10px); border: 1px solid rgba(139, 92, 246, 0.3); border-radius: 20px;">
            <div class="card-body p-4">
                <div class="d-flex justify-content-between align-items-center flex-wrap">
                    <div>
                        <h5 class="mb-1" style="color: ${color};">
                            <i class="fa-solid fa-chart-simple me-2"></i>Score de confiance IA
                        </h5>
                        <small class="text-muted">Basé sur la qualité et la quantité des données</small>
                    </div>
                    <div class="text-end">
                        <div class="display-6 fw-bold" style="color: ${color};">${Math.round(percentage)}%</div>
                        <span class="badge" style="background: ${color};">${label}</span>
                    </div>
                </div>
                <div class="progress mt-3" style="height: 8px; background: #1e293b;">
                    <div class="progress-bar" role="progressbar" style="width: ${percentage}%; background: ${color}; transition: width 1s ease;"></div>
                </div>
            </div>
        </div>
    `;
}

/*
|--------------------------------------------------------------------------
| Fonctions utilitaires
|--------------------------------------------------------------------------
*/

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function scrollToResults() {
    setTimeout(() => {
        const resultsContainer = document.querySelector("#lexical-section, #disease-section");
        if (resultsContainer) {
            resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }, 200);
}

function handleApiError(error) {
    const errorMessage = error.message;
    
    if (errorMessage.includes("Failed to fetch") || errorMessage.includes("NetworkError")) {
        showToast("❌ Impossible de contacter le serveur. Vérifiez que le backend est démarré.", "error");
        console.error("💡 Astuce : Assurez-vous que le serveur Flask est lancé sur http://127.0.0.1:5000");
    } else if (errorMessage.includes("timeout") || errorMessage.includes("Délai")) {
        showToast("⏱️ Le serveur met trop de temps à répondre. Réessayez plus tard.", "error");
    } else if (errorMessage.includes("HTTP 500")) {
        showToast("❌ Erreur interne du serveur. Vérifiez les logs du backend.", "error");
    } else if (errorMessage.includes("HTTP 400")) {
        showToast("📝 Format des données invalide. Vérifiez votre saisie.", "error");
    } else {
        showToast(`❌ Erreur: ${errorMessage.substring(0, 100)}`, "error");
    }
}

function generateFallbackRecommendations(data) {
    const recommendations = [
        "📝 Notez l'évolution de vos symptômes",
        "💧 Restez hydraté(e) et reposez-vous"
    ];
    
    if (data.tokens && data.tokens.some(t => ["fièvre", "fievre"].includes(t.toLowerCase()))) {
        recommendations.push("🌡️ Surveillez votre température régulièrement");
    }
    
    if (data.tokens && data.tokens.includes("toux")) {
        recommendations.push("🍯 Le miel peut aider à soulager la toux");
    }
    
    recommendations.push("👨‍⚕️ Consultez un médecin si les symptômes persistent");
    
    return recommendations;
}

function displayConsoleSummary(data, symptoms) {
    console.group("📊 Résumé de l'analyse ShifaaAI");
    console.log("🔍 Symptômes saisis :", symptoms);
    console.log("📝 Tokens extraits :", data.tokens?.length || 0);
    console.log("🏥 Maladies prédites :", data.diseases?.length || 0);
    if (data.top_prediction) {
        console.log("🎯 Diagnostic principal :", data.top_prediction.name, `(${data.top_prediction.probability}%)`);
    }
    console.log("⏱️ Temps de traitement :", data.processing_time || "N/A");
    console.groupEnd();
}

// Ajouter les animations CSS si nécessaires
function addApiAnimations() {
    if (document.getElementById("api-animations")) return;
    
    const style = document.createElement("style");
    style.id = "api-animations";
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
    `;
    document.head.appendChild(style);
}

// Initialiser
addApiAnimations();

// Exporter les fonctions (si module)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { sendSymptoms, showLoading, hideLoading, displayPipeline };
}
