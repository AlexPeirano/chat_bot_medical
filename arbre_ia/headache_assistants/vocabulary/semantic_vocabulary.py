"""
Semantic Vocabulary - Embedding-Based Medical Term Matching.

This module provides semantic matching of medical terms using word embeddings,
replacing exact keyword matching with similarity-based detection that handles
synonyms, patient vernacular, and term variations.

Architecture
------------
Instead of:
    "fièvre" in text → fever=True (exact match)

We do:
    embed("fièvre") ≈ embed("j'ai chaud") → fever=True (semantic similarity)

This catches:
- Synonyms: "mal de tête" ↔ "céphalée"
- Patient vernacular: "ça tape" → "pulsatile"
- Variations: "fébrile", "fiévreux", "fièvre" → fever
- Partial matches: "un peu raide" → meningeal consideration

Vocabulary Structure
--------------------
Multi-level vocabulary:
1. **Single Terms** (~200): Individual medical words
   - "fièvre", "brutale", "méningé", "déficit"

2. **Short Phrases** (~150): 2-3 word medical expressions
   - "raideur nuque", "coup tonnerre", "vomissements jet"

3. **Patient Expressions** (~150): Vernacular equivalents
   - "mal de crâne", "ça tape", "j'ai super mal"

Each vocabulary entry maps to:
- field: HeadacheCase field name
- value: Value to assign (True/False/"thunderclap"/etc.)
- weight: Confidence weight (0.0-1.0)
- category: Clinical category for organization

Usage
-----
>>> from headache_assistants.vocabulary.semantic_vocabulary import SemanticVocabulary
>>> vocab = SemanticVocabulary()
>>> matches = vocab.match_text("J'ai un mal de crâne terrible qui tape")
>>> for m in matches:
...     print(f"{m.term} → {m.field}={m.value} ({m.similarity:.2f})")
céphalée → headache_profile=migraine_like (0.85)
intense → intensity=severe (0.78)

Author: Medical NLU Team
Version: 1.0
"""

import re
import warnings
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from .base import normalize_text, DetectionResult, ConceptCategory

# Lazy import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    warnings.warn(
        "sentence-transformers not installed. SemanticVocabulary will not work.\n"
        "Install with: pip install sentence-transformers"
    )


# =============================================================================
# MEDICAL VOCABULARY DEFINITIONS
# =============================================================================
# Each entry: "term" → {"field": str, "value": Any, "weight": float, "category": str}
#
# Categories:
# - onset: Mode de début (thunderclap, progressive, chronic)
# - fever: Fièvre et température
# - meningeal: Syndrome méningé
# - htic: Hypertension intracrânienne
# - deficit: Déficit neurologique
# - seizure: Convulsions/épilepsie
# - pregnancy: Grossesse/post-partum
# - trauma: Traumatisme
# - immunosup: Immunodépression
# - profile: Profil céphalée (migraine, tension)
# - intensity: Intensité douleur
# - temporal: Durée/profil temporel
# =============================================================================

SEMANTIC_VOCABULARY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # ONSET - Mode de début (CRITICAL for HSA detection)
    # =========================================================================
    # Thunderclap indicators
    "brutal": {"field": "onset", "value": "thunderclap", "weight": 0.90, "category": "onset"},
    "brutale": {"field": "onset", "value": "thunderclap", "weight": 0.90, "category": "onset"},
    "soudain": {"field": "onset", "value": "thunderclap", "weight": 0.85, "category": "onset"},
    "soudaine": {"field": "onset", "value": "thunderclap", "weight": 0.85, "category": "onset"},
    "explosif": {"field": "onset", "value": "thunderclap", "weight": 0.90, "category": "onset"},
    "explosive": {"field": "onset", "value": "thunderclap", "weight": 0.90, "category": "onset"},
    "foudroyant": {"field": "onset", "value": "thunderclap", "weight": 0.92, "category": "onset"},
    "foudroyante": {"field": "onset", "value": "thunderclap", "weight": 0.92, "category": "onset"},
    "instantané": {"field": "onset", "value": "thunderclap", "weight": 0.88, "category": "onset"},
    "instantanée": {"field": "onset", "value": "thunderclap", "weight": 0.88, "category": "onset"},
    "subite": {"field": "onset", "value": "thunderclap", "weight": 0.85, "category": "onset"},
    "subit": {"field": "onset", "value": "thunderclap", "weight": 0.85, "category": "onset"},
    "coup de tonnerre": {"field": "onset", "value": "thunderclap", "weight": 0.95, "category": "onset"},
    "thunderclap": {"field": "onset", "value": "thunderclap", "weight": 0.95, "category": "onset"},
    "d'emblée maximale": {"field": "onset", "value": "thunderclap", "weight": 0.95, "category": "onset"},
    "maximale d'emblée": {"field": "onset", "value": "thunderclap", "weight": 0.95, "category": "onset"},
    "pire douleur de ma vie": {"field": "onset", "value": "thunderclap", "weight": 0.95, "category": "onset"},
    "pire mal de tête": {"field": "onset", "value": "thunderclap", "weight": 0.90, "category": "onset"},
    "jamais eu aussi mal": {"field": "onset", "value": "thunderclap", "weight": 0.90, "category": "onset"},
    "d'un coup": {"field": "onset", "value": "thunderclap", "weight": 0.80, "category": "onset"},
    "tout d'un coup": {"field": "onset", "value": "thunderclap", "weight": 0.82, "category": "onset"},
    "comme une explosion": {"field": "onset", "value": "thunderclap", "weight": 0.88, "category": "onset"},
    "tête qui explose": {"field": "onset", "value": "thunderclap", "weight": 0.85, "category": "onset"},

    # Progressive indicators
    "progressif": {"field": "onset", "value": "progressive", "weight": 0.85, "category": "onset"},
    "progressive": {"field": "onset", "value": "progressive", "weight": 0.85, "category": "onset"},
    "progressivement": {"field": "onset", "value": "progressive", "weight": 0.82, "category": "onset"},
    "graduel": {"field": "onset", "value": "progressive", "weight": 0.80, "category": "onset"},
    "graduelle": {"field": "onset", "value": "progressive", "weight": 0.80, "category": "onset"},
    "insidieux": {"field": "onset", "value": "progressive", "weight": 0.78, "category": "onset"},
    "insidieuse": {"field": "onset", "value": "progressive", "weight": 0.78, "category": "onset"},
    "qui augmente": {"field": "onset", "value": "progressive", "weight": 0.75, "category": "onset"},
    "qui empire": {"field": "onset", "value": "progressive", "weight": 0.75, "category": "onset"},
    "de plus en plus fort": {"field": "onset", "value": "progressive", "weight": 0.78, "category": "onset"},

    # Chronic indicators
    "chronique": {"field": "onset", "value": "chronic", "weight": 0.90, "category": "onset"},
    "permanent": {"field": "onset", "value": "chronic", "weight": 0.85, "category": "onset"},
    "permanente": {"field": "onset", "value": "chronic", "weight": 0.85, "category": "onset"},
    "quotidien": {"field": "onset", "value": "chronic", "weight": 0.85, "category": "onset"},
    "quotidienne": {"field": "onset", "value": "chronic", "weight": 0.85, "category": "onset"},
    "tous les jours": {"field": "onset", "value": "chronic", "weight": 0.82, "category": "onset"},
    "depuis des années": {"field": "onset", "value": "chronic", "weight": 0.88, "category": "onset"},
    "depuis des mois": {"field": "onset", "value": "chronic", "weight": 0.85, "category": "onset"},
    "de longue date": {"field": "onset", "value": "chronic", "weight": 0.85, "category": "onset"},
    "habituel": {"field": "onset", "value": "chronic", "weight": 0.75, "category": "onset"},
    "habituelle": {"field": "onset", "value": "chronic", "weight": 0.75, "category": "onset"},

    # =========================================================================
    # FEVER - Fièvre (RED FLAG with meningeal)
    # =========================================================================
    "fièvre": {"field": "fever", "value": True, "weight": 0.95, "category": "fever"},
    "fébrile": {"field": "fever", "value": True, "weight": 0.95, "category": "fever"},
    "fiévreux": {"field": "fever", "value": True, "weight": 0.90, "category": "fever"},
    "fiévreuse": {"field": "fever", "value": True, "weight": 0.90, "category": "fever"},
    "hyperthermie": {"field": "fever", "value": True, "weight": 0.95, "category": "fever"},
    "pyrexie": {"field": "fever", "value": True, "weight": 0.95, "category": "fever"},
    "température élevée": {"field": "fever", "value": True, "weight": 0.88, "category": "fever"},
    "chaud": {"field": "fever", "value": True, "weight": 0.60, "category": "fever"},
    "frissons": {"field": "fever", "value": True, "weight": 0.75, "category": "fever"},
    "sueurs": {"field": "fever", "value": True, "weight": 0.65, "category": "fever"},
    "brûlant": {"field": "fever", "value": True, "weight": 0.70, "category": "fever"},
    # Negations
    "apyrétique": {"field": "fever", "value": False, "weight": 0.95, "category": "fever"},
    "apyrexie": {"field": "fever", "value": False, "weight": 0.95, "category": "fever"},
    "pas de fièvre": {"field": "fever", "value": False, "weight": 0.92, "category": "fever"},
    "sans fièvre": {"field": "fever", "value": False, "weight": 0.92, "category": "fever"},
    "afébril": {"field": "fever", "value": False, "weight": 0.90, "category": "fever"},
    "afébrile": {"field": "fever", "value": False, "weight": 0.90, "category": "fever"},

    # =========================================================================
    # MENINGEAL SIGNS - Syndrome méningé (CRITICAL RED FLAG)
    # =========================================================================
    "méningé": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "méningée": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "syndrome méningé": {"field": "meningeal_signs", "value": True, "weight": 0.98, "category": "meningeal"},
    "méningite": {"field": "meningeal_signs", "value": True, "weight": 0.90, "category": "meningeal"},
    "raideur nuque": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "raideur de nuque": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "nuque raide": {"field": "meningeal_signs", "value": True, "weight": 0.92, "category": "meningeal"},
    "cou raide": {"field": "meningeal_signs", "value": True, "weight": 0.85, "category": "meningeal"},
    "kernig": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "brudzinski": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "chien de fusil": {"field": "meningeal_signs", "value": True, "weight": 0.95, "category": "meningeal"},
    "position fœtale": {"field": "meningeal_signs", "value": True, "weight": 0.80, "category": "meningeal"},
    "photophobie": {"field": "meningeal_signs", "value": True, "weight": 0.75, "category": "meningeal"},
    "phonophobie": {"field": "meningeal_signs", "value": True, "weight": 0.70, "category": "meningeal"},
    "lumière fait mal": {"field": "meningeal_signs", "value": True, "weight": 0.72, "category": "meningeal"},
    "bruit fait mal": {"field": "meningeal_signs", "value": True, "weight": 0.68, "category": "meningeal"},
    "ne peut pas tourner la tête": {"field": "meningeal_signs", "value": True, "weight": 0.80, "category": "meningeal"},
    "cou bloqué": {"field": "meningeal_signs", "value": True, "weight": 0.82, "category": "meningeal"},
    # Negations
    "nuque souple": {"field": "meningeal_signs", "value": False, "weight": 0.95, "category": "meningeal"},
    "pas de raideur": {"field": "meningeal_signs", "value": False, "weight": 0.90, "category": "meningeal"},

    # =========================================================================
    # HTIC - Hypertension Intracrânienne (RED FLAG)
    # =========================================================================
    "htic": {"field": "htic_pattern", "value": True, "weight": 0.95, "category": "htic"},
    "hypertension intracrânienne": {"field": "htic_pattern", "value": True, "weight": 0.98, "category": "htic"},
    "vomissements en jet": {"field": "htic_pattern", "value": True, "weight": 0.95, "category": "htic"},
    "vomissement en jet": {"field": "htic_pattern", "value": True, "weight": 0.95, "category": "htic"},
    "œdème papillaire": {"field": "htic_pattern", "value": True, "weight": 0.95, "category": "htic"},
    "papilloedème": {"field": "htic_pattern", "value": True, "weight": 0.95, "category": "htic"},
    "céphalée matutinale": {"field": "htic_pattern", "value": True, "weight": 0.85, "category": "htic"},
    "pire le matin": {"field": "htic_pattern", "value": True, "weight": 0.75, "category": "htic"},
    "pire au réveil": {"field": "htic_pattern", "value": True, "weight": 0.75, "category": "htic"},
    "aggravé par toux": {"field": "htic_pattern", "value": True, "weight": 0.82, "category": "htic"},
    "aggravé par effort": {"field": "htic_pattern", "value": True, "weight": 0.80, "category": "htic"},
    "éclipses visuelles": {"field": "htic_pattern", "value": True, "weight": 0.88, "category": "htic"},
    "je vois flou": {"field": "htic_pattern", "value": True, "weight": 0.65, "category": "htic"},
    "vision trouble": {"field": "htic_pattern", "value": True, "weight": 0.68, "category": "htic"},

    # =========================================================================
    # NEUROLOGICAL DEFICIT (CRITICAL RED FLAG)
    # =========================================================================
    "déficit": {"field": "neuro_deficit", "value": True, "weight": 0.85, "category": "deficit"},
    "déficit neurologique": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "déficit moteur": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "déficit sensitif": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "paralysie": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "parésie": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "hémiplégie": {"field": "neuro_deficit", "value": True, "weight": 0.98, "category": "deficit"},
    "hémiparésie": {"field": "neuro_deficit", "value": True, "weight": 0.98, "category": "deficit"},
    "aphasie": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "dysarthrie": {"field": "neuro_deficit", "value": True, "weight": 0.92, "category": "deficit"},
    "diplopie": {"field": "neuro_deficit", "value": True, "weight": 0.90, "category": "deficit"},
    "vision double": {"field": "neuro_deficit", "value": True, "weight": 0.88, "category": "deficit"},
    "hémianopsie": {"field": "neuro_deficit", "value": True, "weight": 0.95, "category": "deficit"},
    "ataxie": {"field": "neuro_deficit", "value": True, "weight": 0.92, "category": "deficit"},
    "confusion": {"field": "neuro_deficit", "value": True, "weight": 0.80, "category": "deficit"},
    "désorientation": {"field": "neuro_deficit", "value": True, "weight": 0.82, "category": "deficit"},
    "perte de connaissance": {"field": "neuro_deficit", "value": True, "weight": 0.85, "category": "deficit"},
    "faiblesse bras": {"field": "neuro_deficit", "value": True, "weight": 0.85, "category": "deficit"},
    "faiblesse jambe": {"field": "neuro_deficit", "value": True, "weight": 0.85, "category": "deficit"},
    "ne peut plus bouger": {"field": "neuro_deficit", "value": True, "weight": 0.82, "category": "deficit"},
    "trouble parole": {"field": "neuro_deficit", "value": True, "weight": 0.88, "category": "deficit"},
    "parle bizarrement": {"field": "neuro_deficit", "value": True, "weight": 0.75, "category": "deficit"},
    "mots qui sortent pas": {"field": "neuro_deficit", "value": True, "weight": 0.72, "category": "deficit"},
    "engourdissement": {"field": "neuro_deficit", "value": True, "weight": 0.70, "category": "deficit"},
    "fourmillements": {"field": "neuro_deficit", "value": True, "weight": 0.65, "category": "deficit"},
    "paresthésies": {"field": "neuro_deficit", "value": True, "weight": 0.75, "category": "deficit"},
    # Negations
    "pas de déficit": {"field": "neuro_deficit", "value": False, "weight": 0.95, "category": "deficit"},
    "sans déficit": {"field": "neuro_deficit", "value": False, "weight": 0.95, "category": "deficit"},
    "examen neurologique normal": {"field": "neuro_deficit", "value": False, "weight": 0.95, "category": "deficit"},

    # =========================================================================
    # SEIZURES - Convulsions/Épilepsie (RED FLAG)
    # =========================================================================
    "convulsion": {"field": "seizure", "value": True, "weight": 0.95, "category": "seizure"},
    "convulsions": {"field": "seizure", "value": True, "weight": 0.95, "category": "seizure"},
    "crise épileptique": {"field": "seizure", "value": True, "weight": 0.95, "category": "seizure"},
    "épilepsie": {"field": "seizure", "value": True, "weight": 0.90, "category": "seizure"},
    "crise comitiale": {"field": "seizure", "value": True, "weight": 0.95, "category": "seizure"},
    "crise tonico-clonique": {"field": "seizure", "value": True, "weight": 0.98, "category": "seizure"},
    "a convulsé": {"field": "seizure", "value": True, "weight": 0.95, "category": "seizure"},
    "secousses": {"field": "seizure", "value": True, "weight": 0.75, "category": "seizure"},
    "mouvements anormaux": {"field": "seizure", "value": True, "weight": 0.70, "category": "seizure"},
    "tremblements": {"field": "seizure", "value": True, "weight": 0.60, "category": "seizure"},

    # =========================================================================
    # PREGNANCY/POSTPARTUM (HIGH RISK context)
    # =========================================================================
    "enceinte": {"field": "pregnancy_postpartum", "value": True, "weight": 0.95, "category": "pregnancy"},
    "grossesse": {"field": "pregnancy_postpartum", "value": True, "weight": 0.95, "category": "pregnancy"},
    "gestante": {"field": "pregnancy_postpartum", "value": True, "weight": 0.95, "category": "pregnancy"},
    "parturiente": {"field": "pregnancy_postpartum", "value": True, "weight": 0.95, "category": "pregnancy"},
    "post-partum": {"field": "pregnancy_postpartum", "value": True, "weight": 0.95, "category": "pregnancy"},
    "postpartum": {"field": "pregnancy_postpartum", "value": True, "weight": 0.95, "category": "pregnancy"},
    "accouchement": {"field": "pregnancy_postpartum", "value": True, "weight": 0.90, "category": "pregnancy"},
    "vient d'accoucher": {"field": "pregnancy_postpartum", "value": True, "weight": 0.92, "category": "pregnancy"},
    "péridurale": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.90, "category": "pregnancy"},
    "épidurale": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.90, "category": "pregnancy"},

    # =========================================================================
    # TRAUMA (context)
    # =========================================================================
    "traumatisme": {"field": "trauma", "value": True, "weight": 0.95, "category": "trauma"},
    "trauma": {"field": "trauma", "value": True, "weight": 0.90, "category": "trauma"},
    "traumatisme crânien": {"field": "trauma", "value": True, "weight": 0.98, "category": "trauma"},
    "chute": {"field": "trauma", "value": True, "weight": 0.75, "category": "trauma"},
    "accident": {"field": "trauma", "value": True, "weight": 0.70, "category": "trauma"},
    "coup sur la tête": {"field": "trauma", "value": True, "weight": 0.88, "category": "trauma"},
    "choc à la tête": {"field": "trauma", "value": True, "weight": 0.88, "category": "trauma"},
    "cogné la tête": {"field": "trauma", "value": True, "weight": 0.85, "category": "trauma"},
    "tombé": {"field": "trauma", "value": True, "weight": 0.65, "category": "trauma"},
    "avp": {"field": "trauma", "value": True, "weight": 0.90, "category": "trauma"},
    # Negations
    "pas de traumatisme": {"field": "trauma", "value": False, "weight": 0.92, "category": "trauma"},
    "sans traumatisme": {"field": "trauma", "value": False, "weight": 0.92, "category": "trauma"},

    # =========================================================================
    # IMMUNOSUPPRESSION (HIGH RISK context)
    # =========================================================================
    "immunodéprimé": {"field": "immunosuppression", "value": True, "weight": 0.95, "category": "immunosup"},
    "immunodéprimée": {"field": "immunosuppression", "value": True, "weight": 0.95, "category": "immunosup"},
    "immunosuppression": {"field": "immunosuppression", "value": True, "weight": 0.95, "category": "immunosup"},
    "vih": {"field": "immunosuppression", "value": True, "weight": 0.95, "category": "immunosup"},
    "sida": {"field": "immunosuppression", "value": True, "weight": 0.95, "category": "immunosup"},
    "chimiothérapie": {"field": "immunosuppression", "value": True, "weight": 0.90, "category": "immunosup"},
    "chimio": {"field": "immunosuppression", "value": True, "weight": 0.88, "category": "immunosup"},
    "greffe": {"field": "immunosuppression", "value": True, "weight": 0.85, "category": "immunosup"},
    "greffé": {"field": "immunosuppression", "value": True, "weight": 0.88, "category": "immunosup"},
    "cancer": {"field": "immunosuppression", "value": True, "weight": 0.80, "category": "immunosup"},
    "corticothérapie": {"field": "immunosuppression", "value": True, "weight": 0.78, "category": "immunosup"},

    # =========================================================================
    # HEADACHE PROFILE - Migraine-like
    # =========================================================================
    "pulsatile": {"field": "headache_profile", "value": "migraine_like", "weight": 0.85, "category": "profile"},
    "pulsatilité": {"field": "headache_profile", "value": "migraine_like", "weight": 0.85, "category": "profile"},
    "battant": {"field": "headache_profile", "value": "migraine_like", "weight": 0.82, "category": "profile"},
    "battante": {"field": "headache_profile", "value": "migraine_like", "weight": 0.82, "category": "profile"},
    "ça bat": {"field": "headache_profile", "value": "migraine_like", "weight": 0.80, "category": "profile"},
    "ça tape": {"field": "headache_profile", "value": "migraine_like", "weight": 0.78, "category": "profile"},
    "lancinant": {"field": "headache_profile", "value": "migraine_like", "weight": 0.80, "category": "profile"},
    "lancinante": {"field": "headache_profile", "value": "migraine_like", "weight": 0.80, "category": "profile"},
    "unilatéral": {"field": "headache_profile", "value": "migraine_like", "weight": 0.75, "category": "profile"},
    "unilatérale": {"field": "headache_profile", "value": "migraine_like", "weight": 0.75, "category": "profile"},
    "hémicrânie": {"field": "headache_profile", "value": "migraine_like", "weight": 0.85, "category": "profile"},
    "migraine": {"field": "headache_profile", "value": "migraine_like", "weight": 0.90, "category": "profile"},
    "migraineuse": {"field": "headache_profile", "value": "migraine_like", "weight": 0.88, "category": "profile"},
    "migraineux": {"field": "headache_profile", "value": "migraine_like", "weight": 0.88, "category": "profile"},
    "aura": {"field": "headache_profile", "value": "migraine_like", "weight": 0.85, "category": "profile"},
    "scotome": {"field": "headache_profile", "value": "migraine_like", "weight": 0.82, "category": "profile"},
    "nausées": {"field": "headache_profile", "value": "migraine_like", "weight": 0.70, "category": "profile"},
    "vomissements": {"field": "headache_profile", "value": "migraine_like", "weight": 0.72, "category": "profile"},

    # HEADACHE PROFILE - Tension-like
    "tension": {"field": "headache_profile", "value": "tension_like", "weight": 0.75, "category": "profile"},
    "pression": {"field": "headache_profile", "value": "tension_like", "weight": 0.75, "category": "profile"},
    "pesanteur": {"field": "headache_profile", "value": "tension_like", "weight": 0.78, "category": "profile"},
    "en casque": {"field": "headache_profile", "value": "tension_like", "weight": 0.85, "category": "profile"},
    "en étau": {"field": "headache_profile", "value": "tension_like", "weight": 0.88, "category": "profile"},
    "serrement": {"field": "headache_profile", "value": "tension_like", "weight": 0.82, "category": "profile"},
    "serre": {"field": "headache_profile", "value": "tension_like", "weight": 0.78, "category": "profile"},
    "bilatéral": {"field": "headache_profile", "value": "tension_like", "weight": 0.72, "category": "profile"},
    "bilatérale": {"field": "headache_profile", "value": "tension_like", "weight": 0.72, "category": "profile"},
    "diffuse": {"field": "headache_profile", "value": "tension_like", "weight": 0.70, "category": "profile"},
    "diffus": {"field": "headache_profile", "value": "tension_like", "weight": 0.70, "category": "profile"},
    "comme un bandeau": {"field": "headache_profile", "value": "tension_like", "weight": 0.85, "category": "profile"},
    "oppressif": {"field": "headache_profile", "value": "tension_like", "weight": 0.80, "category": "profile"},
    "oppressive": {"field": "headache_profile", "value": "tension_like", "weight": 0.80, "category": "profile"},

    # =========================================================================
    # INTENSITY - Pain severity
    # =========================================================================
    "intense": {"field": "intensity", "value": "severe", "weight": 0.85, "category": "intensity"},
    "sévère": {"field": "intensity", "value": "severe", "weight": 0.88, "category": "intensity"},
    "atroce": {"field": "intensity", "value": "maximum", "weight": 0.92, "category": "intensity"},
    "insupportable": {"field": "intensity", "value": "maximum", "weight": 0.95, "category": "intensity"},
    "terrible": {"field": "intensity", "value": "severe", "weight": 0.85, "category": "intensity"},
    "horrible": {"field": "intensity", "value": "severe", "weight": 0.85, "category": "intensity"},
    "épouvantable": {"field": "intensity", "value": "maximum", "weight": 0.92, "category": "intensity"},
    "intolérable": {"field": "intensity", "value": "maximum", "weight": 0.92, "category": "intensity"},
    "maximale": {"field": "intensity", "value": "maximum", "weight": 0.90, "category": "intensity"},
    "maximum": {"field": "intensity", "value": "maximum", "weight": 0.90, "category": "intensity"},
    "super mal": {"field": "intensity", "value": "severe", "weight": 0.78, "category": "intensity"},
    "très mal": {"field": "intensity", "value": "severe", "weight": 0.80, "category": "intensity"},
    "énorme": {"field": "intensity", "value": "severe", "weight": 0.82, "category": "intensity"},
    "modérée": {"field": "intensity", "value": "moderate", "weight": 0.85, "category": "intensity"},
    "modéré": {"field": "intensity", "value": "moderate", "weight": 0.85, "category": "intensity"},
    "moyenne": {"field": "intensity", "value": "moderate", "weight": 0.80, "category": "intensity"},
    "gênante": {"field": "intensity", "value": "moderate", "weight": 0.75, "category": "intensity"},
    "légère": {"field": "intensity", "value": "mild", "weight": 0.85, "category": "intensity"},
    "léger": {"field": "intensity", "value": "mild", "weight": 0.85, "category": "intensity"},
    "faible": {"field": "intensity", "value": "mild", "weight": 0.82, "category": "intensity"},
    "peu intense": {"field": "intensity", "value": "mild", "weight": 0.80, "category": "intensity"},

    # =========================================================================
    # PATIENT VERNACULAR - Common expressions
    # =========================================================================
    "mal de tête": {"field": "headache_type", "value": "cephalee", "weight": 0.70, "category": "general"},
    "mal de crâne": {"field": "headache_type", "value": "cephalee", "weight": 0.72, "category": "general"},
    "mal au crâne": {"field": "headache_type", "value": "cephalee", "weight": 0.72, "category": "general"},
    "céphalée": {"field": "headache_type", "value": "cephalee", "weight": 0.95, "category": "general"},
    "céphalées": {"field": "headache_type", "value": "cephalee", "weight": 0.95, "category": "general"},
    "maux de tête": {"field": "headache_type", "value": "cephalee", "weight": 0.72, "category": "general"},
    "tête qui tourne": {"field": "vertigo", "value": True, "weight": 0.75, "category": "vestibular"},
    "vertiges": {"field": "vertigo", "value": True, "weight": 0.90, "category": "vestibular"},
    "vertige": {"field": "vertigo", "value": True, "weight": 0.90, "category": "vestibular"},

    # =========================================================================
    # RECENT LP / PONCTION LOMBAIRE
    # =========================================================================
    "ponction lombaire": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.95, "category": "procedure"},
    "pl récente": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.92, "category": "procedure"},
    "après pl": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.90, "category": "procedure"},
    "rachianesthésie": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.92, "category": "procedure"},
    "post-pl": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.92, "category": "procedure"},
    "soulagé allongé": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.80, "category": "procedure"},
    "pire debout": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.78, "category": "procedure"},
    "céphalée positionnelle": {"field": "recent_pl_or_peridural", "value": True, "weight": 0.85, "category": "procedure"},

    # =========================================================================
    # PATTERN CHANGE (for chronic headaches)
    # =========================================================================
    "changé": {"field": "recent_pattern_change", "value": True, "weight": 0.70, "category": "pattern_change"},
    "différent": {"field": "recent_pattern_change", "value": True, "weight": 0.72, "category": "pattern_change"},
    "différente": {"field": "recent_pattern_change", "value": True, "weight": 0.72, "category": "pattern_change"},
    "pas comme d'habitude": {"field": "recent_pattern_change", "value": True, "weight": 0.85, "category": "pattern_change"},
    "inhabituel": {"field": "recent_pattern_change", "value": True, "weight": 0.80, "category": "pattern_change"},
    "inhabituelle": {"field": "recent_pattern_change", "value": True, "weight": 0.80, "category": "pattern_change"},
    "aggravation": {"field": "recent_pattern_change", "value": True, "weight": 0.82, "category": "pattern_change"},
    "s'aggrave": {"field": "recent_pattern_change", "value": True, "weight": 0.80, "category": "pattern_change"},
    "plus fort que d'habitude": {"field": "recent_pattern_change", "value": True, "weight": 0.85, "category": "pattern_change"},
    "nouveau type": {"field": "recent_pattern_change", "value": True, "weight": 0.88, "category": "pattern_change"},
}


# =============================================================================
# SEMANTIC MATCH RESULT
# =============================================================================

@dataclass
class SemanticMatch:
    """
    Result of semantic vocabulary matching.

    Attributes:
        term: The vocabulary term that matched
        input_token: The input text token that was matched
        field: The HeadacheCase field to update
        value: The value to assign
        weight: Base confidence weight from vocabulary
        similarity: Embedding similarity score (0.0-1.0)
        final_confidence: Combined confidence (weight * similarity)
        category: Clinical category of the term
    """
    term: str
    input_token: str
    field: str
    value: Any
    weight: float
    similarity: float
    final_confidence: float
    category: str

    def __hash__(self):
        return hash((self.term, self.field, self.input_token))

    def __eq__(self, other):
        if not isinstance(other, SemanticMatch):
            return False
        return self.term == other.term and self.field == other.field


# =============================================================================
# SEMANTIC VOCABULARY CLASS
# =============================================================================

class SemanticVocabulary:
    """
    Embedding-based medical vocabulary matching.

    This class provides semantic similarity matching between user input
    and a curated medical vocabulary, enabling robust detection of
    clinical concepts even with synonyms and patient vernacular.

    Architecture:
        1. Pre-compute embeddings for all vocabulary terms at init
        2. For each input, tokenize and embed
        3. Find nearest vocabulary terms above similarity threshold
        4. Return matches mapped to clinical fields

    Attributes:
        vocabulary: Dict mapping terms to clinical field definitions
        embedder: SentenceTransformer model for embedding
        term_embeddings: Pre-computed embeddings for vocabulary terms
        term_list: Ordered list of vocabulary terms (for index mapping)
        similarity_threshold: Minimum similarity for a match (default 0.65)

    Example:
        >>> vocab = SemanticVocabulary(similarity_threshold=0.70)
        >>> matches = vocab.match_text("J'ai un mal de crâne terrible")
        >>> for m in matches:
        ...     print(f"{m.field}={m.value} (conf={m.final_confidence:.2f})")
    """

    def __init__(
        self,
        similarity_threshold: float = 0.78,
        embedding_model: str = 'all-MiniLM-L6-v2',
        verbose: bool = False,
        min_token_length: int = 3
    ):
        """
        Initialize semantic vocabulary with pre-computed embeddings.

        Args:
            similarity_threshold: Minimum cosine similarity for matches (0.0-1.0)
                                 Higher = more precise, lower = more recall.
                                 Default 0.78 to avoid false positives from short words.
            embedding_model: Sentence-transformers model name
            verbose: Print initialization progress
            min_token_length: Minimum token length to consider (default 3)
                             Prevents short words like "en" from matching.

        Raises:
            ImportError: If sentence-transformers not available
        """
        self.min_token_length = min_token_length
        if not EMBEDDING_AVAILABLE:
            raise ImportError(
                "sentence-transformers required for SemanticVocabulary. "
                "Install with: pip install sentence-transformers"
            )

        self.vocabulary = SEMANTIC_VOCABULARY
        self.similarity_threshold = similarity_threshold
        self.verbose = verbose

        # Initialize embedder
        if verbose:
            print(f"[SemanticVocabulary] Loading model '{embedding_model}'...")
        self.embedder = SentenceTransformer(embedding_model)

        # Pre-compute vocabulary embeddings
        self.term_list = list(self.vocabulary.keys())
        if verbose:
            print(f"[SemanticVocabulary] Computing embeddings for {len(self.term_list)} terms...")

        self.term_embeddings = self.embedder.encode(
            self.term_list,
            convert_to_numpy=True,
            show_progress_bar=verbose
        )

        if verbose:
            print(f"[SemanticVocabulary] Ready. Shape: {self.term_embeddings.shape}")

    def match_text(self, text: str) -> List[SemanticMatch]:
        """
        Find semantic matches between input text and vocabulary.

        This method:
        1. Tokenizes input into words and n-grams (2-4 words)
        2. Embeds each token
        3. Finds nearest vocabulary terms above threshold
        4. Returns deduplicated matches sorted by confidence

        Args:
            text: Input text to analyze

        Returns:
            List of SemanticMatch objects, sorted by final_confidence descending

        Example:
            >>> matches = vocab.match_text("Céphalée brutale avec fièvre")
            >>> matches[0].field, matches[0].value
            ('onset', 'thunderclap')
        """
        if not text or not text.strip():
            return []

        # Normalize text
        text_normalized = normalize_text(text, preserve_accents=False)
        text_with_accents = text.lower()

        # Generate tokens: words + n-grams (2-4 words)
        tokens = self._generate_tokens(text_normalized, text_with_accents)

        if not tokens:
            return []

        # Embed all tokens at once (batch for efficiency)
        token_embeddings = self.embedder.encode(
            tokens,
            convert_to_numpy=True,
            show_progress_bar=False
        )

        # Find matches for each token
        matches = []
        for i, token in enumerate(tokens):
            token_embedding = token_embeddings[i]

            # Compute similarities with all vocabulary terms
            similarities = np.dot(self.term_embeddings, token_embedding)

            # Find terms above threshold
            above_threshold = np.where(similarities >= self.similarity_threshold)[0]

            for idx in above_threshold:
                term = self.term_list[idx]
                term_info = self.vocabulary[term]
                similarity = float(similarities[idx])

                # Compute final confidence
                final_confidence = term_info["weight"] * similarity

                matches.append(SemanticMatch(
                    term=term,
                    input_token=token,
                    field=term_info["field"],
                    value=term_info["value"],
                    weight=term_info["weight"],
                    similarity=similarity,
                    final_confidence=final_confidence,
                    category=term_info["category"]
                ))

        # Deduplicate: keep highest confidence match per field
        matches = self._deduplicate_matches(matches)

        # Sort by final confidence
        matches.sort(key=lambda m: m.final_confidence, reverse=True)

        return matches

    def _generate_tokens(self, text_normalized: str, text_with_accents: str) -> List[str]:
        """
        Generate tokens (words and n-grams) from input text.

        Generates:
        - Individual words (filtered by min_token_length)
        - 2-grams
        - 3-grams
        - 4-grams (for longer medical expressions)

        Uses both accent-stripped and original text for better matching.
        Filters out very short words to prevent false positive matches.
        """
        tokens = set()
        min_len = self.min_token_length

        # Word tokenization
        words_normalized = re.findall(r'\b[\w-]+\b', text_normalized)
        words_accented = re.findall(r'\b[\w-]+\b', text_with_accents)

        # Single words (filtered by minimum length)
        for w in words_normalized:
            if len(w) >= min_len:
                tokens.add(w)
        for w in words_accented:
            if len(w) >= min_len:
                tokens.add(w)

        # N-grams (2, 3, 4 words)
        for n in [2, 3, 4]:
            # From normalized text
            for i in range(len(words_normalized) - n + 1):
                ngram = ' '.join(words_normalized[i:i+n])
                tokens.add(ngram)
            # From accented text
            for i in range(len(words_accented) - n + 1):
                ngram = ' '.join(words_accented[i:i+n])
                tokens.add(ngram)

        return list(tokens)

    def _deduplicate_matches(self, matches: List[SemanticMatch]) -> List[SemanticMatch]:
        """
        Deduplicate matches, keeping highest confidence per field.

        For each field, keeps only the match with highest final_confidence.
        This prevents multiple matches for the same clinical concept.
        """
        field_best: Dict[str, SemanticMatch] = {}

        for match in matches:
            key = match.field
            if key not in field_best or match.final_confidence > field_best[key].final_confidence:
                field_best[key] = match

        return list(field_best.values())

    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vocabulary.

        Returns:
            Dict with term counts by category, total terms, etc.
        """
        categories = {}
        for term, info in self.vocabulary.items():
            cat = info["category"]
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_terms": len(self.vocabulary),
            "categories": categories,
            "embedding_dim": self.term_embeddings.shape[1] if self.term_embeddings is not None else 0,
            "similarity_threshold": self.similarity_threshold
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_semantic_vocabulary(
    similarity_threshold: float = 0.65,
    verbose: bool = False
) -> Optional[SemanticVocabulary]:
    """
    Factory function to create SemanticVocabulary with error handling.

    Args:
        similarity_threshold: Minimum similarity for matches
        verbose: Print progress messages

    Returns:
        SemanticVocabulary instance or None if embedding unavailable
    """
    if not EMBEDDING_AVAILABLE:
        warnings.warn("SemanticVocabulary unavailable - sentence-transformers not installed")
        return None

    try:
        return SemanticVocabulary(
            similarity_threshold=similarity_threshold,
            verbose=verbose
        )
    except Exception as e:
        warnings.warn(f"Failed to create SemanticVocabulary: {e}")
        return None
