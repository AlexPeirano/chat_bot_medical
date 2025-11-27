import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1) Charger le JSON ---
with open("/Users/test/Desktop/PCE/chat_bot_medicale/v_llm2/thorax_test.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --- 2) Transformer chaque entrée en texte RAG ---
documents = []
doc_ids = []
for item in data:
    text = (
        f"id: {item['id']}\n"
        f"système: {item['systeme']}\n"
        f"pathologie: {item['pathologie']}\n"
        f"modalité: {item['modalite']}\n"
        f"population: {', '.join(item['population'])}\n"
        f"conditions: {item['conditions']}\n"
        f"questions: {item['questions']}\n"
        f"dépendances: {item['dependances']}\n"
        f"exclusions: {item['exclusions']}\n"
        f"résumé: {item['resume']}\n"
        f"priorité: {item['priorite']}\n"
    )
    documents.append(text)
    doc_ids.append(item['id'])

# --- 3) Créer un vectoriseur TF-IDF ---
vectorizer = TfidfVectorizer()
doc_vectors = vectorizer.fit_transform(documents)

# --- 4) Fonction de recherche simple ---
def rechercher_cas(question, top_k=3):
    question_vec = vectorizer.transform([question])
    simil = cosine_similarity(question_vec, doc_vectors)
    # Récupérer les indices des top_k documents les plus proches
    indices = simil[0].argsort()[::-1][:top_k]
    # Retourner les documents et leur score
    results = []
    for idx in indices:
        results.append({
            "id": doc_ids[idx],
            "score": simil[0][idx],
            "texte": documents[idx]
        })
    return results

# --- 5) Exemple d'utilisation ---
if __name__ == "__main__":
    print("✅ RAG simplifié chargé")
    while True:
        question = input("\nMédecin : ")
        if question.lower() in ["quit", "exit"]:
            break
        results = rechercher_cas(question)
        print("\nCas pertinents trouvés :")
        for r in results:
            print(f"- {r['id']} (score {r['score']:.2f})")
            print(f"Résumé : {r['texte'].split('résumé:')[1].split('priorité:')[0].strip()}\n")
