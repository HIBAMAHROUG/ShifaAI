const DO_API_BACKEND = `${(typeof window !== 'undefined' && window.__SHIFAAI_API_BASE_URL)
  ? String(window.__SHIFAAI_API_BASE_URL).replace(/\/$/, '')
  : (typeof window !== 'undefined' && window.location && window.location.protocol !== 'file:'
      ? `${window.location.protocol}//${window.location.hostname}:5000`
      : 'http://127.0.0.1:5000')}/api/external/disease-info`;

async function searchDisease(query, limit = 5) {
  const response = await fetch(DO_API_BACKEND, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ disease: query, limit })
  });

  if (!response.ok) {
    throw new Error(`Erreur recherche Disease Ontology (${response.status})`);
  }

  return response.json();
}

async function getDiseaseDetails(diseaseId) {
  const response = await fetch(DO_API_BACKEND, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ disease: diseaseId })
  });

  if (!response.ok) {
    throw new Error(`Erreur détails Disease Ontology (${response.status})`);
  }

  const payload = await response.json();

  if (payload?.results?.length) {
    return payload.results[0];
  }

  return payload;
}

window.DiseaseOntologyApi = {
  searchDisease,
  getDiseaseDetails,
};
