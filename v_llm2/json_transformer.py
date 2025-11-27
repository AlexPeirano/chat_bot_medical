import json
import os
from typing import Any, Dict, List

INPUT_PATH = "/Users/test/Desktop/PCE/chat_bot_medicale/v_llm2/thorax_test2.json"
OUTPUT_DIR = "documents_rag"
OUTPUT_JSON = "documents_rag.json"


def safe_join(val: Any) -> str:
    """Convertit proprement toute valeur JSON en texte."""
    if val is None:
        return ""
    if isinstance(val, bool):
        return "oui" if val else "non"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val)
    return str(val)


def json_to_text(entry: Dict[str, Any]) -> str:
    """Convertit une fiche JSON en texte lisible pour RAG."""
    lines = []

    lines.append(f"ID : {entry.get('id','')}")
    lines.append(f"Système : {entry.get('systeme','')}")
    lines.append(f"Pathologie : {entry.get('pathologie','')}")
    lines.append(f"Modalité recommandée : {entry.get('modalite','')}")
    lines.append(f"Population : {safe_join(entry.get('populations'))}")
    lines.append(f"Symptômes : {safe_join(entry.get('symptomes'))}")
    lines.append(f"Indications positives : {safe_join(entry.get('indications_positives'))}")
    lines.append(f"Indications négatives : {safe_join(entry.get('indications_negatives'))}")
    lines.append(f"Résumé : {entry.get('resume','')}")
    lines.append(f"Urgence : {entry.get('urgence_enum','')}")
    lines.append(f"Ionisant : {safe_join(entry.get('ionisant'))}")
    lines.append(f"Produit de contraste : {safe_join(entry.get('requires_contrast'))}")
    lines.append(f"Priorité : {entry.get('priorite','')}")
    lines.append(f"Dose : {entry.get('dose','')}")
    lines.append(f"Synonymes : {safe_join(entry.get('synonymes'))}")
    lines.append(f"Source : {entry.get('source','')} ({entry.get('year','')})")

    lines.append(f"-- Fin fiche {entry.get('id','')} --")

    return "\n".join(lines)


def main():
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"Impossible de trouver {INPUT_PATH}")
    
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    documents = []

    for entry in data:
        text = json_to_text(entry)
        documents.append({"id": entry.get("id",""), "text": text})

        file_id = entry.get("id","fiche").replace("/", "_")
        path_out = os.path.join(OUTPUT_DIR, f"{file_id}.txt")

        with open(path_out, "w", encoding="utf-8") as out_f:
            out_f.write(text)

    with open(os.path.join(OUTPUT_DIR, OUTPUT_JSON), "w", encoding="utf-8") as jf:
        json.dump(documents, jf, ensure_ascii=False, indent=2)

    print(f"✓ {len(documents)} documents générés dans {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
