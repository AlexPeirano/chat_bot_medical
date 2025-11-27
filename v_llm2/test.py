import os
import json
import requests
from dotenv import load_dotenv
from chromadb import Client

# =========================
# Chargement clé Mistral
# =========================
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
if mistral_api_key is None:
    raise ValueError("Clé Mistral introuvable. Vérifie ton fichier .env.")

# =========================
# Charger embeddings
# =========================
with open("/Users/test/Desktop/PCE/chat_bot_medicale/embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# =========================
# Initialiser Chroma
# =========================
client = Client()
collection_name = "documents_rag"

# Créer ou récupérer la collection
if collection_name in [c.name for c in client.list_collections()]:
    collection = client.get_collection(collection_name)
else:
    collection = client.create_collection(name=collection_name)
    for i, item in enumerate(data):
        collection.add(
            ids=[str(i)],
            embeddings=[item["embedding"]],
            metadatas=[{"text": item["text"]}],
            documents=[item["text"]]
        )
    print("Embeddings ajoutés à la collection.")

print("Collections existantes :", client.list_collections())
print("Nombre de documents dans la collection :", len(collection.get()["ids"]))

# =========================
# Fonction pour générer embeddings via Mistral
# =========================
EMBED_URL = "https://api.mistral.ai/v1/embeddings"

def get_embedding(text):
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

# =========================
# Recherche RAG
# =========================
def search_documents(query, top_k=3):
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    return results

# =========================
# Fonction pour poser une question au LLM
# =========================
CHAT_URL = "https://api.mistral.ai/v1/chat/completions"
conversation_history = []

def ask_mistral(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    payload = {
        "model": "mistral-small-latest",
        "messages": conversation_history
    }
    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(CHAT_URL, json=payload, headers=headers)
    if response.status_code != 200:
        return f"Erreur API ({response.status_code}) : {response.text}"
    answer = response.json()["choices"][0]["message"]["content"]
    conversation_history.append({"role": "assistant", "content": answer})
    return answer

# =========================
# Prompt RAG
# =========================
def build_rag_prompt(user_query, retrieved_docs):
    docs_text = "\n\n".join([d["text"] for d in retrieved_docs])
    prompt = (
        f"Voici des documents médicaux extraits de la base vectorielle :\n{docs_text}\n\n"
        f"Utilisateur : {user_query}\n"
        "Réponds en utilisant uniquement les informations disponibles dans les documents.\n"
        "Si certaines informations nécessaires pour donner une recommandation sont manquantes, "
        "pose une question pour obtenir ces informations avant de donner la recommandation.\n"
        "Si aucun document ne correspond ou si les conditions ne sont pas remplies, réponds 'Je ne sais pas'.\n"
        "Fais en sorte que la conversation reste naturelle et compréhensible."
    )
    return prompt

# =========================
# Boucle interactive
# =========================
print("\n=== RAG Chat avec Mistral ===")
print("Tape 'exit' pour quitter.\n")

while True:
    user_input = input("Vous : ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # Recherche RAG
    results = search_documents(user_input)
    retrieved_docs = [{"text": t} for t in results['documents'][0] if t is not None]

    # Construire le prompt avec les documents
    rag_prompt = build_rag_prompt(user_input, retrieved_docs)

    # Poser la question au LLM
    answer = ask_mistral(rag_prompt)
    print("Mistral :", answer)
