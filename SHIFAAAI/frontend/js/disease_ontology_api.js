const DO_API_BACKEND = 'http://127.0.0.1:5000/api/external/disease';

async function searchDisease(query, limit = 5) {
  const response = await fetch(`${DO_API_BACKEND}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, limit })
  });

  if (!response.ok) {
    throw new Error(`Erreur recherche Disease Ontology (${response.status})`);
  }

  return response.json();
}

async function getDiseaseDetails(diseaseId) {
  const response = await fetch(`${DO_API_BACKEND}/terms/${encodeURIComponent(diseaseId)}`);

  if (!response.ok) {
    throw new Error(`Erreur détails Disease Ontology (${response.status})`);
  }

  return response.json();
}

window.DiseaseOntologyApi = {
  searchDisease,
  getDiseaseDetails,
};
