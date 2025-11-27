import os
import json
import requests
from dotenv import load_dotenv
from chromadb import Client

# Charger la clé API Mistral
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
if mistral_api_key is None:
    raise ValueError("Clé API Mistral introuvable. Vérifie ton fichier .env.")

# Charger la base Chroma
client = Client()
collection = client.get_collection("documents_rag")  # nom de la collection que tu as créée

# Endpoint embeddings Mistral
EMBED_URL = "https://api.mistral.ai/v1/embeddings"

def get_embedding(text):
    """Génère l'embedding pour un texte avec Mistral."""
    payload = {
        "model": "mistral-embed",
        "input": text
    }
    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(EMBED_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Erreur API ({response.status_code}) : {response.text}")
    return response.json()["data"][0]["embedding"]

def search_documents(query, top_k=3):
    """Recherche les documents les plus proches d'une requête."""
    query_embedding = get_embedding(query)
    
    # Requête dans la base Chroma
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    return results

# Exemple d'utilisation
user_query = "Enfant avec douleur thoracique et suspicion pneumothorax"
results = search_documents(user_query)

print("Documents trouvés :")
for i, doc in enumerate(results['documents'][0], start=1):
    print(f"\nDocument {i} :")
    print(doc)
    print("Distance :", results['distances'][0][i-1])
