"""Service for querying Disease Ontology APIs with resilient fallbacks."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import re

import requests


class DiseaseOntologyService:
    """Fetch disease terms from external ontology sources."""

    PRIMARY_BASE = "https://api.disease-ontology.org/v1"
    OLS_BASE = "https://www.ebi.ac.uk/ols4/api"

    def __init__(self, timeout: int = 12):
        self.timeout = timeout

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query = (query or "").strip()
        if not query:
            return []

        primary_results = self._search_primary(query, limit)
        if primary_results:
            return primary_results

        return self._search_ols(query, limit)

    def get_term(self, disease_id: str) -> Dict[str, Any]:
        disease_id = (disease_id or "").strip()
        if not disease_id:
            return {}

        primary_term = self._get_term_primary(disease_id)
        if primary_term:
            return primary_term

        return self._get_term_ols(disease_id)

    def _search_primary(self, query: str, limit: int) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.PRIMARY_BASE}/search",
                params={"q": query},
                timeout=self.timeout,
            )
            if response.status_code != 200:
                return []

            payload = response.json()
            rows = payload.get("results") or payload.get("data") or []
            return [self._normalize_primary_result(item) for item in rows[:limit]]
        except Exception:
            return []

    def _get_term_primary(self, disease_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.PRIMARY_BASE}/terms/{disease_id}",
                timeout=self.timeout,
            )
            if response.status_code != 200:
                return {}
            payload = response.json()
            return self._normalize_primary_term(payload)
        except Exception:
            return {}

    def _search_ols(self, query: str, limit: int) -> List[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.OLS_BASE}/search",
                params={"q": query, "ontology": "doid", "rows": max(1, limit)},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            docs = payload.get("response", {}).get("docs", [])
            return [self._normalize_ols_doc(doc) for doc in docs[:limit]]
        except Exception:
            return []

    def _get_term_ols(self, disease_id: str) -> Dict[str, Any]:
        short_form = disease_id.replace(":", "_")
        try:
            response = requests.get(
                f"{self.OLS_BASE}/ontologies/doid/terms",
                params={"short_form": short_form},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            terms = payload.get("_embedded", {}).get("terms", [])
            if not terms:
                return {}
            return self._normalize_ols_term(terms[0])
        except Exception:
            return {}

    @staticmethod
    def _extract_symptoms(text: str) -> List[str]:
        if not text:
            return []
        matches = re.findall(r"has_symptom\s+([a-zA-Z\-\s]+?)(?:,|\.| and |$)", text)
        cleaned = []
        for raw in matches:
            symptom = re.sub(r"\s+", " ", raw.strip().lower())
            if symptom and symptom not in cleaned:
                cleaned.append(symptom)
        return cleaned[:10]

    def _normalize_primary_result(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": item.get("id") or item.get("diseaseId") or item.get("obo_id"),
            "label": item.get("label") or item.get("name") or "Unknown",
            "description": item.get("description") or "",
            "source": "disease-ontology-v1",
            "synonyms": item.get("synonyms") or [],
        }

    def _normalize_primary_term(self, item: Dict[str, Any]) -> Dict[str, Any]:
        description = item.get("description") or ""
        if isinstance(description, list):
            description = description[0] if description else ""
        return {
            "id": item.get("id") or item.get("obo_id"),
            "label": item.get("label") or item.get("name") or "Unknown",
            "description": description,
            "synonyms": item.get("synonyms") or [],
            "symptoms": self._extract_symptoms(description),
            "source": "disease-ontology-v1",
        }

    def _normalize_ols_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        description = doc.get("description") or []
        if isinstance(description, list):
            description = description[0] if description else ""
        return {
            "id": doc.get("obo_id") or doc.get("short_form"),
            "label": doc.get("label") or "Unknown",
            "description": description,
            "synonyms": doc.get("exact_synonyms") or [],
            "source": "ols4-doid",
        }

    def _normalize_ols_term(self, term: Dict[str, Any]) -> Dict[str, Any]:
        description = term.get("description") or []
        if isinstance(description, list):
            description = description[0] if description else ""

        synonyms = term.get("synonyms") or []
        if not isinstance(synonyms, list):
            synonyms = []

        return {
            "id": term.get("obo_id") or term.get("short_form"),
            "label": term.get("label") or "Unknown",
            "description": description,
            "synonyms": synonyms,
            "symptoms": self._extract_symptoms(description),
            "source": "ols4-doid",
            "iri": term.get("iri"),
        }
