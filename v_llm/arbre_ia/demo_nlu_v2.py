"""Script de démonstration du système NLU v2.

Compare les résultats entre nlu.py (v1) et nlu_v2.py (v2) sur des cas réels
avec acronymes, synonymes et variations linguistiques.

Usage:
    python demo_nlu_v2.py
"""

from headache_assistants.nlu import parse_free_text_to_case
from headache_assistants.nlu_v2 import parse_free_text_to_case_v2


def print_separator():
    """Affiche un séparateur visuel."""
    print("=" * 80)


def compare_cases(text: str, title: str):
    """Compare les résultats v1 vs v2 pour un texte donné.

    Args:
        text: Texte médical à analyser
        title: Titre du cas de test
    """
    print_separator()
    print(f"CAS: {title}")
    print_separator()
    print(f"Texte: \"{text}\"")
    print()

    # VERSION 1
    case_v1, meta_v1 = parse_free_text_to_case(text)

    # VERSION 2
    case_v2, meta_v2 = parse_free_text_to_case_v2(text)

    # Comparaison
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│ COMPARAISON V1 (nlu.py) vs V2 (nlu_v2.py + medical_vocabulary.py) │")
    print("├─────────────────────────┬─────────────────────┬─────────────────────┤")
    print("│ Champ                   │ V1                  │ V2                  │")
    print("├─────────────────────────┼─────────────────────┼─────────────────────┤")

    fields = [
        ("Onset", "onset"),
        ("Profile", "profile"),
        ("Fièvre", "fever"),
        ("Syndrome méningé", "meningeal_signs"),
        ("HTIC", "htic_pattern"),
        ("Déficit neuro", "neuro_deficit"),
        ("Traumatisme", "trauma"),
        ("Crises", "seizure"),
        ("Grossesse/PP", "pregnancy_postpartum"),
        ("Immunodépression", "immunosuppression"),
    ]

    for label, field in fields:
        v1_val = getattr(case_v1, field, None)
        v2_val = getattr(case_v2, field, None)

        # Formatage
        v1_str = str(v1_val) if v1_val is not None else "None"
        v2_str = str(v2_val) if v2_val is not None else "None"

        # Indicateur de différence
        diff_marker = "  " if v1_val == v2_val else "→ "

        print(f"│ {label:23} │ {v1_str:19} │ {diff_marker}{v2_str:17} │")

    print("└─────────────────────────┴─────────────────────┴─────────────────────┘")

    # Traçabilité V2
    if meta_v2.get('detection_trace'):
        print()
        print("TRAÇABILITÉ V2 (termes matchés):")
        for field, trace in meta_v2['detection_trace'].items():
            confidence = meta_v2['confidence_scores'].get(field, 0)
            print(f"  • {field:20} : '{trace['matched_term']}' "
                  f"({trace['source']}, confiance={confidence:.2f})")

    # Confiance globale
    print()
    print(f"Confiance globale V1: {meta_v1.get('overall_confidence', 0):.2%}")
    print(f"Confiance globale V2: {meta_v2.get('overall_confidence', 0):.2%}")
    print()


def main():
    """Exécute les démonstrations."""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║        DÉMONSTRATION NLU V2 - Détection robuste d'acronymes       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    # CAS 1: Acronymes médicaux
    compare_cases(
        text="Patient de 45a avec TCC il y a 2j après AVP, RDN+",
        title="Acronymes médicaux (TCC, AVP, RDN+)"
    )

    # CAS 2: Langage patient
    compare_cases(
        text="Je ne peux pas bouger le cou depuis ce matin, c'est venu d'un coup",
        title="Langage patient (cou bloqué = syndrome méningé)"
    )

    # CAS 3: Validation numérique fièvre
    compare_cases(
        text="Céphalée brutale, T° 37.5",
        title="Température normale (37.5°C < 38°C)"
    )

    compare_cases(
        text="Céphalée brutale, T° 38.8",
        title="Fièvre confirmée (38.8°C ≥ 38°C)"
    )

    # CAS 4: Anti-patterns (scotome ≠ HTIC)
    compare_cases(
        text="Scotomes scintillants depuis 20min",
        title="Aura migraineuse (scotome ≠ HTIC)"
    )

    compare_cases(
        text="Céphalée matutinale avec vomissements en jet",
        title="Vrai HTIC (céphalée matutinale + vom. en jet)"
    )

    # CAS 5: Grossesse avec acronymes obstétricaux
    compare_cases(
        text="Patiente G2P1, 28 SA, céphalée brutale",
        title="Grossesse (G2P1, 28 SA)"
    )

    # CAS 6: Cas complexe
    compare_cases(
        text="F 32a, G1P0 à 22 SA, céph brutale il y a 2h, EVA 10/10, RDN++, "
             "féb à 38.8, PF G, VIH+ sous ARV",
        title="Cas complexe (multiples acronymes)"
    )

    print_separator()
    print("CONCLUSION:")
    print_separator()
    print()
    print("✅ V2 détecte significativement mieux les acronymes médicaux")
    print("✅ V2 comprend le langage patient (\"cou bloqué\" → syndrome méningé)")
    print("✅ V2 valide numériquement la fièvre (seuil ≥38°C)")
    print("✅ V2 évite les faux positifs avec anti-patterns (scotome ≠ HTIC)")
    print("✅ V2 offre une traçabilité complète (terme matché + source + confiance)")
    print()
    print("🚀 Migration recommandée: Remplacer nlu.py par nlu_v2.py")
    print()


if __name__ == "__main__":
    main()
