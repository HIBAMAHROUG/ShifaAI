import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from services.disease_ontology_service import DiseaseOntologyService


def main() -> None:
    service = DiseaseOntologyService()
    seed_queries = ["influenza", "pharyngitis", "pneumonia", "gastroenteritis", "migraine"]

    collected = []
    seen_ids = set()

    for query in seed_queries:
        results = service.search(query, limit=8)
        print(f"[{query}] {len(results)} resultats")
        for item in results:
            disease_id = item.get("id")
            if not disease_id or disease_id in seen_ids:
                continue
            seen_ids.add(disease_id)
            collected.append(item)

    print(f"\nNombre total de maladies externes: {len(collected)}")
    print(json.dumps(collected[:5], indent=2, ensure_ascii=False))

    output_path = Path(__file__).resolve().parents[1] / "data" / "diseases.json"
    output = {"source": "Disease Ontology / OLS4", "count": len(collected), "diseases": collected}
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFichier mis a jour: {output_path}")


if __name__ == "__main__":
    main()
