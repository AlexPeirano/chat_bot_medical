# Proposition : NLU Hybride (Règles + Embedding)

## Architecture

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class HybridNLU:
    def __init__(self):
        # Layer 1: Règles (existant)
        self.rule_nlu = NLUv2()
        
        # Layer 2: Embedding (nouveau)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.medical_examples = self._load_examples()
        self.example_embeddings = self.embedder.encode(
            [ex['text'] for ex in self.medical_examples]
        )
    
    def parse(self, text: str):
        # Étape 1: Essayer règles
        case, metadata = self.rule_nlu.parse_free_text_to_case(text)
        
        # Étape 2: Si faible confiance, utiliser embedding
        if metadata['overall_confidence'] < 0.7:
            case = self._enhance_with_embedding(text, case)
        
        return case, metadata
    
    def _enhance_with_embedding(self, text: str, case):
        # Encoder le texte
        query_emb = self.embedder.encode([text])[0]
        
        # Trouver exemple le plus similaire
        similarities = np.dot(self.example_embeddings, query_emb)
        best_idx = np.argmax(similarities)
        best_example = self.medical_examples[best_idx]
        
        # Enrichir les champs manquants
        if case.fever is None and best_example.get('fever') is not None:
            case = case.model_copy(update={'fever': best_example['fever']})
        
        # ... autres champs
        
        return case
    
    def _load_examples(self):
        """Charge exemples annotés (à créer)."""
        return [
            {
                'text': 'Patient avec céphalée et sensibilité à la lumière',
                'fever': False,
                'headache_profile': 'migraine_like'
            },
            # ... 100-200 exemples
        ]
```

## Avantages de cette approche

1. **Rétrocompatibilité totale** : Règles actuelles restent primaires
2. **Performance** : 90% des cas traités par règles (<10ms), 10% par embedding (~50ms)
3. **Amélioration continue** : Ajouter exemples au fil de l'eau
4. **Traçabilité** : Source toujours identifiée (rule vs embedding)
5. **RGPD-compliant** : Tout en local, pas de données envoyées

## Données requises

**Corpus d'exemples médicaux (100-200 cas annotés) :**
```json
[
  {
    "text": "Céphalée brutale pire douleur de ma vie",
    "onset": "thunderclap",
    "profile": "acute",
    "fever": null,
    "meningeal_signs": null
  },
  {
    "text": "Mal de tête avec sensibilité lumière et bruit",
    "headache_profile": "migraine_like",
    "fever": false
  }
]
```

**Source :** 
- Vos cas réels anonymisés
- Littérature médicale
- Guidelines officielles

## Performance attendue

| Métrique | Règles seules | Hybride (Règles + Embedding) |
|----------|---------------|------------------------------|
| Précision patterns connus | 95% | 95% |
| Précision nouveaux patterns | 40% | 85% ⬆️ |
| Latence moyenne | 8ms | 25ms |
| Latence P95 | 15ms | 80ms |
| RAM requise | 50 MB | 300 MB |

## Migration progressive

**Phase 1 (1 semaine) :**
- Implémenter architecture hybride
- Créer 50 exemples annotés de base
- Mode "shadow" : compare règles vs embedding sans impacter prod

**Phase 2 (2 semaines) :**
- Collecter 100-200 exemples réels anonymisés
- Fine-tuner seuils de confiance
- A/B test avec médecins

**Phase 3 (ongoing) :**
- Monitoring : quand embedding est utilisé
- Enrichissement continu corpus
- Feedback médecins → nouveaux exemples

## Alternative : LLM si temps réponse OK

Si l'hôpital accepte 2-3s de latence, **Phi-3-mini** (3.8B) est excellent :

```bash
# Installation Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3

# Test
ollama run phi3 "Analyser: Céphalée brutale avec raideur nuque"
```

**Prompt structuré :**
```python
prompt = f"""Tu es un assistant médical expert. Analyse ce cas clinique.

CAS: {user_input}

Extraire au format JSON strict :
{{
  "onset": "thunderclap|progressive|chronic|unknown",
  "fever": true|false|null,
  "meningeal_signs": true|false|null,
  "confidence": 0.0-1.0
}}

Réponse JSON uniquement, pas d'explication :"""
```

**Latence :** 2-4s sur CPU moderne (acceptable ?)
