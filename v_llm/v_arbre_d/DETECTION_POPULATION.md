# Détection Automatique de Population

## Vue d'ensemble

Le système détecte automatiquement la population du patient (enfant, adulte, personne âgée) à partir du texte médical, permettant d'adapter les recommandations d'imagerie selon l'âge.

## Fonctionnement

### 1. Détection par âge

Le système extrait l'âge du patient et le catégorise automatiquement :

| Âge | Population |
|-----|------------|
| < 18 ans | enfant |
| 18-64 ans | adulte |
| ≥ 65 ans | personne_agee |

**Exemples :**
```
"patiente 12 ans avec douleur abdominale"
→ Âge: 12 ans, Population: enfant

"homme 35 ans douleur thoracique"
→ Âge: 35 ans, Population: adulte

"patient 70 ans cancer colorectal"
→ Âge: 70 ans, Population: personne_agee
```

### 2. Détection par mots-clés

Le système reconnaît également des mots-clés spécifiques (prioritaire sur la détection par âge) :

#### Population enfant
- `enfant`, `pédiatrique`, `pédiatr*`
- `nourrisson`, `bébé`, `nouveau-né`
- `adolescent`

#### Population adulte
- `adulte`, `jeune adulte`

#### Population personne âgée
- `personne agée`, `âgé`, `senior`
- `gériatrique`, `gériatr*`

**Exemples :**
```
"enfant avec fièvre et toux"
→ Population: enfant (même sans âge explicite)

"patient pédiatrique avec fièvre"
→ Population: enfant

"personne âgée avec confusion"
→ Population: personne_agee
```

### 3. Impact sur les recommandations

La population détectée influence le score de correspondance :

- **Bonus de +1.0 point** si la population détectée correspond aux populations cibles dans le JSON
- Permet de discriminer automatiquement entre protocoles enfant/adulte

#### Exemple : Appendicite

```
Texte: "enfant 8 ans douleur abdominale FID"
Population détectée: enfant

Scores:
  ★ échographie abdominale (enfant)        Score: 3.0 (2 + 1.0 bonus)
    échographie-Doppler (adulte)           Score: 2.0 (2 + 0 bonus)
    IRM abdominopelvienne (grossesse)      Score: 2.0 (2 + 0 bonus)

→ Le système recommande automatiquement l'échographie simple pour l'enfant
```

## Cas d'usage

### Cas 1 : Discrimination enfant/adulte

**Scénario enfant :**
```
Entrée: "enfant 10 ans douleur fosse iliaque droite"
Détection:
  - Âge: 10 ans
  - Population: enfant
Recommandation: échographie abdominale (1ère intention)
```

**Scénario adulte :**
```
Entrée: "patient 35 ans douleur FID"
Détection:
  - Âge: 35 ans
  - Population: adulte
Recommandation: échographie-Doppler abdominopelvienne
```

### Cas 2 : Protocoles adaptés à l'âge

**Thorax enfant :**
```
Entrée: "enfant 5 ans dyspnée suspicion corps étranger"
Détection:
  - Âge: 5 ans
  - Population: enfant
Recommandation: radiographie thoracique adaptée pédiatrie
```

**Thorax adulte :**
```
Entrée: "homme 50 ans dyspnée aiguë suspicion EP"
Détection:
  - Âge: 50 ans
  - Population: adulte
Recommandation: angioscanner thoracique
```

### Cas 3 : Cas particuliers (grossesse)

```
Entrée: "femme 28 ans enceinte grossesse douleur FID"
Détection:
  - Âge: 28 ans
  - Population: adulte
  - Grossesse: Oui (bonus +2.0)
Recommandation: IRM abdominopelvienne (prioritaire, pas de rayons)
```

## Affichage à l'utilisateur

Lorsque le médecin entre du texte, le système affiche :

```
Médecin : patiente 12 ans avec douleur abdominale
Âge détecté : 12 ans
Population détectée : Enfant
Sexe détecté : femme
```

## Tests de validation

La fonctionnalité a été validée par :

1. **19 tests de détection** (100% réussite)
   - Détection par âge (limites 17/18, 64/65 ans)
   - Détection par mots-clés
   - Cas mixtes (âge + mot-clé)

2. **14 scénarios cliniques** (100% réussite)
   - Thorax : 7/7 ✓
   - Digestif : 7/7 ✓

3. **56 tests unitaires** (98.2% réussite)
   - Thorax : 24/24 ✓
   - Digestif : 31/32 ✓

## Avantages

✅ **Automatique** : Pas besoin de poser de questions supplémentaires  
✅ **Robuste** : Détecte l'âge numérique ET les mots-clés textuels  
✅ **Précis** : Améliore la discrimination entre protocoles similaires  
✅ **Transparent** : Affiche la population détectée à l'utilisateur  
✅ **Adaptatif** : Fonctionne avec tous les systèmes (céphalées, thorax, digestif)

## Implémentation technique

### Fonction principale

```python
def analyse_texte_medical(texte):
    """Extrait et analyse les informations du texte médical."""
    # ... détection d'âge ...
    
    # Détection automatique de la population
    population = None
    if age is not None:
        if age < 18:
            population = "enfant"
        elif 18 <= age < 65:
            population = "adulte"
        else:
            population = "personne_agee"
    
    # Détection par mots-clés (prioritaire)
    if re.search(r"\b(?:enfant|pediatr\w*|nourrisson|...)\b", t_norm):
        population = "enfant"
    # ...
    
    return {
        "age": age,
        "population": population,
        # ...
    }
```

### Scoring avec bonus de population

```python
def _match_best_entry(entries, positives, patient_info):
    """Score les entrées avec bonus de population."""
    for e in entries:
        score = len(symptomes_matchés)
        
        # Bonus population
        populations = e.get("populations") or []
        detected_population = patient_info.get("population")
        if detected_population and detected_population in populations:
            score += 1.0  # Bonus fort
        
        # Bonus grossesse encore plus fort
        if patient_info.get("grossesse") and "enceinte" in populations:
            score += 2.0
```

## Structure JSON

Les fichiers JSON doivent inclure le champ `populations` :

```json
{
  "id": "abdomen_appendicite_enfant_v2",
  "pathologie": "appendicite aiguë",
  "modalite": "échographie abdominale (1ère intention)",
  "populations": ["enfant"],
  "symptomes": ["douleur FID", "douleur abdominale"],
  ...
}
```

Valeurs possibles : `["enfant"]`, `["adulte"]`, `["personne_agee"]`, `["femme", "enceinte"]`, etc.
