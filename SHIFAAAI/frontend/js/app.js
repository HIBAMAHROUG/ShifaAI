// app.js - Version complète

// Sélection des éléments DOM
const analyzeButton = document.querySelector(".analyze-btn");
const textarea = document.querySelector("textarea");

// Nouvelle logique : appel API Flask
analyzeButton.addEventListener("click", async () => {
    const text = textarea.value.trim();
    if (text === "") {
        showNotification("Veuillez saisir vos symptômes.", "warning");
        return;
    }
    showLoadingState();
    try {
        // Appel API Flask via sendSymptoms (api.js)
        const data = await sendSymptoms(text);
        // Afficher les résultats du back-end
        if (data) displayResults(data);
    } catch (e) {
        showNotification("Erreur lors de l'analyse : " + (e.message || e), "error");
    }
    hideLoadingState();
});

// ============================================
// 1. ANALYSE LEXICALE
// ============================================
function lexicalAnalysis(text) {
    
    // Nettoyage et tokenisation
    const cleanedText = text.toLowerCase()
        .replace(/[^\w\sàâäéèêëîïôöùûüç]/g, '')
        .replace(/\s+/g, ' ');
    
    const tokens = cleanedText.split(' ');
    
    // Dictionnaire de mots médicaux (symptômes courants)
    const medicalTerms = {
        fievre: { type: "symptome", severity: "élevé", category: "température" },
        toux: { type: "symptome", severity: "moyen", category: "respiratoire" },
        gorge: { type: "symptome", severity: "moyen", category: "ORL" },
        douleur: { type: "symptome", severity: "variable", category: "douleur" },
        fatigue: { type: "symptome", severity: "moyen", category: "général" },
        maux: { type: "symptome", severity: "moyen", category: "douleur" },
        tete: { type: "symptome", severity: "moyen", category: "neurologique" },
        nausée: { type: "symptome", severity: "moyen", category: "digestif" },
        vomissement: { type: "symptome", severity: "élevé", category: "digestif" },
        diarrhée: { type: "symptome", severity: "élevé", category: "digestif" },
        essoufflement: { type: "symptome", severity: "critique", category: "respiratoire" },
        frissons: { type: "symptome", severity: "moyen", category: "température" },
        courbatures: { type: "symptome", severity: "moyen", category: "musculaire" },
        nez: { type: "symptome", severity: "faible", category: "ORL" },
        rhume: { type: "symptome", severity: "faible", category: "ORL" }
    };
    
    // Extraction des termes médicaux
    const foundTerms = [];
    const unknownTerms = [];
    
    tokens.forEach(token => {
        if (medicalTerms[token]) {
            foundTerms.push({
                term: token,
                ...medicalTerms[token]
            });
        } else if (token.length > 2) {
            unknownTerms.push(token);
        }
    });
    
    // Statistiques lexicales
    const stats = {
        totalWords: tokens.length,
        medicalTermsCount: foundTerms.length,
        uniqueTerms: [...new Set(foundTerms.map(t => t.term))].length,
        severityLevels: {
            faible: foundTerms.filter(t => t.severity === "faible").length,
            moyen: foundTerms.filter(t => t.severity === "moyen").length,
            élevé: foundTerms.filter(t => t.severity === "élevé").length,
            critique: foundTerms.filter(t => t.severity === "critique").length
        }
    };
    
    console.log("✅ Analyse lexicale complétée:", { foundTerms, stats, unknownTerms });
    
    return {
        success: true,
        tokens: tokens,
        medicalTerms: foundTerms,
        unknownTerms: unknownTerms,
        statistics: stats
    };
}

// ============================================
// 2. ANALYSE SYNTAXIQUE
// ============================================
function syntaxAnalysis(text) {
    
    // Détection des négations
    const negationWords = ["pas", "ne", "non", "jamais", "plus", "aucun", "sans"];
    const textLower = text.toLowerCase();
    
    // Mots de liaison et structure
    const connectors = ["et", "avec", "ainsi que", "mais", "ou", "donc"];
    const intensifiers = ["très", "beaucoup", "extrêmement", "trop", "fortement", "légèrement"];
    
    // Détection des négations dans les symptômes
    const negations = [];
    negationWords.forEach(neg => {
        if (textLower.includes(neg)) {
            negations.push(neg);
        }
    });
    
    // Détection des intensificateurs
    const detectedIntensifiers = [];
    intensifiers.forEach(int => {
        if (textLower.includes(int)) {
            detectedIntensifiers.push(int);
        }
    });
    
    // Détection des connecteurs
    const detectedConnectors = [];
    connectors.forEach(conn => {
        if (textLower.includes(conn)) {
            detectedConnectors.push(conn);
        }
    });
    
    // Analyse de la structure de la phrase
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const sentenceStructure = sentences.map(sentence => ({
        text: sentence.trim(),
        length: sentence.trim().split(' ').length,
        hasNegation: negationWords.some(neg => sentence.toLowerCase().includes(neg))
    }));
    
    // Détermination de la complexité syntaxique
    let complexity = "simple";
    const avgWordsPerSentence = sentenceStructure.reduce((sum, s) => sum + s.length, 0) / sentenceStructure.length;
    if (avgWordsPerSentence > 15) complexity = "complexe";
    else if (avgWordsPerSentence > 8) complexity = "moyen";
    
    console.log("✅ Analyse syntaxique complétée:", { negations, detectedIntensifiers, sentenceStructure, complexity });
    
    return {
        success: true,
        negations: negations,
        intensifiers: detectedIntensifiers,
        connectors: detectedConnectors,
        sentenceCount: sentences.length,
        sentenceStructure: sentenceStructure,
        complexity: complexity,
        hasNegation: negations.length > 0
    };
document.head.appendChild(styleSheet);

console.log("🚀 Application ShifaaAI chargée avec succès !");
// app.js - Version mise à jour
const analyzeButton = document.querySelector(".analyze-btn");
const textarea = document.querySelector("textarea");

analyzeButton.addEventListener("click", () => {
    const text = textarea.value.trim();

    if (text === "") {
        showToast("Veuillez saisir vos symptômes.", "error");
        return;
    }

    // Nettoyer les anciens affichages
    clearAllDisplays();
    
    // Afficher le chargement
    analyzeButton.disabled = true;
    analyzeButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyse en cours...';

    setTimeout(() => {
        // Analyser
        const lexicalResult = lexicalAnalysis(text);
        const syntaxResult = syntaxAnalysis(text);
        const predictionResult = predictDisease(text);
        
        // Réactiver le bouton
        analyzeButton.disabled = false;
        analyzeButton.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Analyser';
        
        showToast("Analyse terminée avec succès !", "success");
    }, 500);
});