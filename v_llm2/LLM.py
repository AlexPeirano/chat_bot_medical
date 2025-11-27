import os
import requests
from dotenv import load_dotenv

# Charger la clé depuis le fichier .env
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if mistral_api_key is None:
    raise ValueError("Clé Mistral introuvable. Vérifie ton fichier .env.")

# URL de l'API Mistral
url = "https://api.mistral.ai/v1/chat/completions"

conversation_history = []

def ask_mistral(question, conversation_history):
    conversation_history.append({"role": "user", "content": question})

    payload = {
        "model": "mistral-small-latest",  # ou le modèle exact que tu as choisi
        "messages": conversation_history
    }

    headers = {
        "Authorization": f"Bearer {mistral_api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        return f"Erreur API ({response.status_code}) : {response.text}", conversation_history

    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    
    conversation_history.append({"role": "assistant", "content": answer})
    return answer, conversation_history

# Boucle interactive
print("=== Conversation avec Mistral ===")
print("Tape 'exit' pour quitter.\n")

while True:
    user_input = input("Vous : ")
    if user_input.lower() in ["exit", "quit"]:
        break

    answer, conversation_history = ask_mistral(user_input, conversation_history)
    print("Mistral :", answer)
