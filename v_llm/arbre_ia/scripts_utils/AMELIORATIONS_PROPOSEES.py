"""Idées d'amélioration de la robustesse du système NLU pour céphalées.

Ce document propose des améliorations concrètes basées sur l'analyse des tests
et des patterns médicaux français courants.
"""

# ============================================================================
# 1. AMÉLIORATIONS EXTRACTION TEMPORELLE
# ============================================================================

TEMPORAL_IMPROVEMENTS = {
    "description": "Améliorer extraction durées implicites et relatives",
    "priority": "HIGH",
    "examples": [
        {
            "pattern": "depuis ce matin",
            "current": "profile=acute détecté mais duration=None",
            "improvement": "Calculer heures réelles selon heure actuelle (ex: 10h si maintenant 18h)",
            "implementation": "Ajouter fonction calculate_implicit_duration(text, current_time)"
        },
        {
            "pattern": "depuis hier soir",
            "current": "profile=acute détecté mais duration=None",
            "improvement": "~12-18h selon contexte",
            "implementation": "Parser 'hier soir' → environ 20h hier → calculer delta"
        },
        {
            "pattern": "il y a 3 jours",
            "current": "Non détecté",
            "improvement": "Ajouter pattern 'il y a X j/h/sem/mois'",
            "implementation": "Regex: r'il y a (\\d+)\\s*(j|h|sem|mois)' dans extract_duration_hours"
        },
        {
            "pattern": "ça fait 2 semaines que",
            "current": "Non détecté",
            "improvement": "Détecter tournure familière",
            "implementation": "Pattern: r'(?:ça|cela) fait (\\d+)\\s*(semaines?|mois|jours?)'"
        }
    ]
}

# ============================================================================
# 2. AMÉLIORATIONS EXTRACTION INTENSITÉ
# ============================================================================

INTENSITY_IMPROVEMENTS = {
    "description": "Gérer multiple EVA values et nuances",
    "priority": "MEDIUM",
    "examples": [
        {
            "pattern": "EVA 3/10 habituellement, crises à 8/10",
            "current": "Prend premier (3/10)",
            "improvement": "Prendre maximum (8/10) ou séparer fond vs crises",
            "implementation": "find_all EVA puis max(), ou extraire EVA_fond et EVA_crise"
        },
        {
            "pattern": "douleur 2-9/10 variable",
            "current": "Prend moyenne (5.5)",
            "improvement": "Identifier variabilité comme red flag",
            "implementation": "Détecter 'variable' + range large → flag instabilité"
        },
        {
            "pattern": "pas si intense que ça",
            "current": "Non détecté",
            "improvement": "Détecter négations nuancées → mild",
            "implementation": "Patterns négatifs: 'pas si...', 'plutôt supportable'"
        }
    ]
}

# ============================================================================
# 3. AMÉLIORATIONS DÉTECTION RED FLAGS
# ============================================================================

RED_FLAG_IMPROVEMENTS = {
    "description": "Améliorer sensibilité et spécificité red flags",
    "priority": "CRITICAL",
    "examples": [
        {
            "pattern": "T° 37.8",
            "current": "Détecté comme fièvre (seuil non défini)",
            "improvement": "Fièvre si ≥38°C uniquement (critère médical)",
            "implementation": "Ajouter validation numérique: temp >= 38 dans FEVER_PATTERNS"
        },
        {
            "pattern": "nuque un peu raide",
            "current": "Détecté comme syndrome méningé (trop sensible)",
            "improvement": "Distinguer raideur légère vs syndrome méningé franc",
            "implementation": "Patterns: 'très raide', 'impossibilité fléchir' → True strict"
        },
        {
            "pattern": "troubles visuels brefs au réveil",
            "current": "Peut être manqué",
            "improvement": "Détecter troubles transitoires vs persistants",
            "implementation": "Séparer neuro_deficit_transient vs neuro_deficit_persistent"
        },
        {
            "pattern": "confusion mentale",
            "current": "Non détecté systématiquement",
            "improvement": "Ajouter troubles conscience comme red flag",
            "implementation": "Nouveau champ: altered_consciousness (confusion, somnolence)"
        }
    ]
}

# ============================================================================
# 4. AMÉLIORATIONS PROFILS CLINIQUES
# ============================================================================

PROFILE_IMPROVEMENTS = {
    "description": "Affiner classification migraine/tension/cluster",
    "priority": "MEDIUM",
    "examples": [
        {
            "pattern": "unilatéral battant photo+ mais Ø N/V",
            "current": "Score migraine vs tension proche",
            "improvement": "Critères IHS: 2/4 suffit pour migraine probable",
            "implementation": "Système de scoring IHS avec seuils: 4/4→migraine certaine, 2-3/4→probable"
        },
        {
            "pattern": "douleur en casque serrement",
            "current": "tension_like",
            "improvement": "Vérifier durée: <4h atypique pour CTT",
            "implementation": "CTT valide si durée >30min et <7j selon IHS"
        },
        {
            "pattern": "périorbitaire + larmoiement + rhinorrhée",
            "current": "Peut manquer AVF",
            "improvement": "Détecter signes autonomes = AVF probable",
            "implementation": "Nouveau pattern AVF: signes_autonomiques + périorbitaire + <3h"
        }
    ]
}

# ============================================================================
# 5. AMÉLIORATIONS GESTION CONTRADICTIONS
# ============================================================================

CONTRADICTION_DETECTION = {
    "description": "Détecter et signaler contradictions dans le texte",
    "priority": "HIGH",
    "examples": [
        {
            "pattern": "fièvre mais apyrétique",
            "current": "Dernier pattern matché gagne",
            "improvement": "Détecter contradiction → marquer comme uncertain",
            "implementation": "Flag: contradictions_detected: ['fever'] → demander clarification"
        },
        {
            "pattern": "céphalée brutale progressive",
            "current": "Un seul onset détecté",
            "improvement": "Contradiction onset → uncertain",
            "implementation": "Si thunderclap ET progressive → onset='conflicting'"
        },
        {
            "pattern": "depuis 2j chronique",
            "current": "Peut classifier incorrectement",
            "improvement": "2j incompatible avec 'chronique' → signaler",
            "implementation": "Validation: si chronic détecté mais duration<90j → warning"
        }
    ]
}

# ============================================================================
# 6. AMÉLIORATIONS VARIANTES LINGUISTIQUES
# ============================================================================

LINGUISTIC_IMPROVEMENTS = {
    "description": "Supporter davantage de variantes françaises",
    "priority": "MEDIUM",
    "examples": [
        {
            "pattern": "mal de crâne", 
            "current": "Non détecté",
            "improvement": "Synonyme familier de céphalée",
            "implementation": "Ajouter à liste synonymes: mal de crâne, migraine (usage populaire)"
        },
        {
            "pattern": "tête qui explose",
            "current": "Peut manquer intensité",
            "improvement": "Expression imagée = sévère",
            "implementation": "Patterns métaphoriques: 'explose', 'éclate', 'va exploser' → severe"
        },
        {
            "pattern": "ça tape / ça cogne",
            "current": "Non détecté",
            "improvement": "Langage familier pour pulsatile",
            "implementation": "Patterns familiers: 'tape', 'cogne', 'bat' → pulsatile"
        },
        {
            "pattern": "depuis toujours",
            "current": "Non détecté",
            "improvement": "= chronique longue durée",
            "implementation": "Pattern: 'depuis toujours', 'depuis que je me souviens' → chronic"
        }
    ]
}

# ============================================================================
# 7. AMÉLIORATIONS EXTRACTION CONTEXTE
# ============================================================================

CONTEXT_IMPROVEMENTS = {
    "description": "Extraire plus de contexte médical pertinent",
    "priority": "LOW",
    "examples": [
        {
            "pattern": "traitement habituel inefficace",
            "current": "Non capturé",
            "improvement": "Red flag: échec traitement habituel",
            "implementation": "Nouveau champ: treatment_failure: bool"
        },
        {
            "pattern": "première fois de ma vie",
            "current": "Détecté dans certains cas",
            "improvement": "Systématiser: first_episode comme red flag",
            "implementation": "Améliorer FIRST_EPISODE patterns"
        },
        {
            "pattern": "aggravation progressive sur 3 semaines",
            "current": "Durée détectée mais pas aggravation",
            "improvement": "Pattern d'aggravation = red flag",
            "implementation": "Nouveau champ: progressive_worsening: bool"
        },
        {
            "pattern": "réveil nocturne par la douleur",
            "current": "Peut être dans HTIC mais pas systématique",
            "improvement": "Red flag: réveils nocturnes répétés",
            "implementation": "Pattern: 'réveillé par', 'réveils nocturnes' → HTIC ou tumeur"
        }
    ]
}

# ============================================================================
# 8. AMÉLIORATIONS VALIDATION & QUALITÉ
# ============================================================================

VALIDATION_IMPROVEMENTS = {
    "description": "Améliorer qualité et confiance des extractions",
    "priority": "HIGH",
    "examples": [
        {
            "pattern": "Âge incohérent (500 ans)",
            "current": "Accepté si pattern matche",
            "improvement": "Validation: 0 < age < 120",
            "implementation": "Post-validation dans parse_free_text_to_case"
        },
        {
            "pattern": "Durée > 10 ans mais 'acute'",
            "current": "Possible si patterns contradictoires",
            "improvement": "Cross-validation durée vs profile",
            "implementation": "Si duration>2160h mais profile=acute → recalculer ou flag"
        },
        {
            "pattern": "Confiance d'extraction basse",
            "current": "Score global mais pas par champ",
            "improvement": "Score de confiance par champ extrait",
            "implementation": "Déjà partiellement implémenté, systématiser"
        },
        {
            "pattern": "Champs critiques manquants",
            "current": "Identifiés mais pas scorés",
            "improvement": "Score de complétude: % champs critiques remplis",
            "implementation": "Métrique: completeness_score = fields_filled / critical_fields_total"
        }
    ]
}

# ============================================================================
# 9. OPTIMISATIONS PERFORMANCE
# ============================================================================

PERFORMANCE_IMPROVEMENTS = {
    "description": "Optimiser vitesse et efficacité",
    "priority": "LOW",
    "examples": [
        {
            "improvement": "Compiler regex patterns une seule fois",
            "implementation": "Pre-compiler tous patterns au module load",
            "impact": "Réduction temps extraction ~30-50%"
        },
        {
            "improvement": "Cache pour textes similaires",
            "implementation": "LRU cache sur parse_free_text_to_case",
            "impact": "Utile si requêtes répétées (tests, dev)"
        },
        {
            "improvement": "Extraction parallèle des champs indépendants",
            "implementation": "ThreadPoolExecutor pour champs sans dépendances",
            "impact": "Gain marginal, complexité accrue"
        }
    ]
}

# ============================================================================
# 10. PRÉPARATION INTÉGRATION LLM
# ============================================================================

LLM_PREPARATION = {
    "description": "Préparer architecture pour intégration LLM future",
    "priority": "MEDIUM",
    "examples": [
        {
            "improvement": "Wrapper unifié extraction",
            "implementation": """
def extract_field(text, field_name, method='rule_based'):
    if method == 'rule_based':
        return rule_based_extraction(text, field_name)
    elif method == 'llm':
        return llm_extraction(text, field_name)
    elif method == 'hybrid':
        rule_result = rule_based_extraction(text, field_name)
        if rule_result['confidence'] < 0.7:
            return llm_extraction(text, field_name)
        return rule_result
            """,
            "benefit": "Migration progressive vers LLM sans réécriture totale"
        },
        {
            "improvement": "Format de sortie structuré pour LLM",
            "implementation": "JSON schema strict pour prompts LLM → validation Pydantic",
            "benefit": "Garantit compatibilité règles + LLM"
        },
        {
            "improvement": "Fallback gracieux",
            "implementation": "Si LLM fail → règles, Si règles fail → valeurs par défaut",
            "benefit": "Robustesse maximale"
        }
    ]
}

# ============================================================================
# PRIORISATION RECOMMANDÉE
# ============================================================================

PRIORITY_ROADMAP = """
PHASE 1 - CRITIQUE (Sécurité patient)
======================================
✅ Red flags: Température ≥38°C strict
✅ Red flags: Troubles conscience (nouveau champ)
✅ Contradictions: Détection et signalement
✅ Validation: Cross-validation durée vs profile

PHASE 2 - HAUTE (Robustesse)
=============================
⚠️ Temporel: "il y a X j/h", "ça fait X que"
⚠️ Temporel: Durées implicites (ce matin, hier)
⚠️ Intensité: Multiple EVA → max
⚠️ Validation: Âges et valeurs aberrantes

PHASE 3 - MOYENNE (Confort)
============================
💡 Profils: Scoring IHS pour migraine
💡 Linguistique: Variantes familières
💡 Contexte: Treatment failure, progressive worsening
💡 LLM: Architecture hybride

PHASE 4 - BASSE (Optimisation)
===============================
🔧 Performance: Regex compilation
🔧 Performance: Caching
🔧 UX: Scores de complétude
"""

if __name__ == "__main__":
    print("=" * 80)
    print("IDÉES D'AMÉLIORATION SYSTÈME NLU CÉPHALÉES")
    print("=" * 80)
    print("\n10 catégories d'amélioration identifiées:")
    print("1. Extraction temporelle")
    print("2. Extraction intensité")
    print("3. Détection red flags")
    print("4. Profils cliniques")
    print("5. Gestion contradictions")
    print("6. Variantes linguistiques")
    print("7. Extraction contexte")
    print("8. Validation & qualité")
    print("9. Performance")
    print("10. Préparation LLM")
    print("\n" + PRIORITY_ROADMAP)
