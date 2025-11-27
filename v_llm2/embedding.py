import os
import json
import requests
from dotenv import load_dotenv

# Charger la clé API Mistral
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if mistral_api_key is None:
    raise ValueError("Clé API Mistral introuvable. Vérifie ton fichier .env.")

# Dossier contenant les fichiers à embedder
INPUT_FOLDER = "documents_rag/"
documents = []

# Charger tous les fichiers du dossier
for filename in os.listdir(INPUT_FOLDER):
    file_path = os.path.join(INPUT_FOLDER, filename)

    if filename.endswith(".txt"):   # On lit seulement les fichiers texte
        with open(file_path, "r", encoding="utf-8") as f:
            documents.append(f.read())

print(f"Nombre de documents chargés : {len(documents)}")

# Transformer chaque document en entrées (séparées par deux sauts de lignes)
entries = []
for doc in documents:
    parts = [p.strip() for p in doc.split("\n\n") if p.strip()]
    entries.extend(parts)

print(f"Nombre total d'entrées à embedder : {len(entries)}")

# API Mistral Embeddings
EMBED_URL = "https://api.mistral.ai/v1/embeddings"

embeddings_output = []

for i, entry in enumerate(entries, start=1):
    print(f"Embedding {i}/{len(entries)}...")

    payload = {
        "model": "mistral-embed",
        "input": entry
    }

    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(EMBED_URL, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"Erreur API ({response.status_code}) : {response.text}")
        continue

    vector = response.json()["data"][0]["embedding"]

    embeddings_output.append({
        "text": entry,
        "embedding": vector
    })

# Sauvegarde dans un fichier JSON
OUTPUT_FILE = "embeddings.json"
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(embeddings_output, f, indent=2)

print(f"\n Embeddings générés ! Résultat dans {OUTPUT_FILE}")
