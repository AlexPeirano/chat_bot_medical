#!/usr/bin/env python3
"""Tests de détection automatique de population."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source'))

from main import analyse_texte_medical

# Scénarios de test pour la détection de population
TEST_CASES = [
    # Tests avec âge explicite
    {
        "texte": "patiente 12 ans avec douleur abdominale",
        "expected_population": "enfant",
        "description": "Âge 12 ans → enfant"
    },
    {
        "texte": "patient 5 ans toux chronique",
        "expected_population": "enfant",
        "description": "Âge 5 ans → enfant"
    },
    {
        "texte": "homme 35 ans douleur thoracique",
        "expected_population": "adulte",
        "description": "Âge 35 ans → adulte"
    },
    {
        "texte": "femme 50 ans dyspnée",
        "expected_population": "adulte",
        "description": "Âge 50 ans → adulte"
    },
    {
        "texte": "patient 70 ans cancer colorectal",
        "expected_population": "personne_agee",
        "description": "Âge 70 ans → personne âgée"
    },
    {
        "texte": "patiente 85 ans chute",
        "expected_population": "personne_agee",
        "description": "Âge 85 ans → personne âgée"
    },
    
    # Tests avec mots-clés explicites
    {
        "texte": "enfant avec fièvre et toux",
        "expected_population": "enfant",
        "description": "Mot-clé 'enfant' détecté"
    },
    {
        "texte": "nourrisson 6 mois difficultés respiratoires",
        "expected_population": "enfant",
        "description": "Mot-clé 'nourrisson' détecté"
    },
    {
        "texte": "adolescent 15 ans traumatisme",
        "expected_population": "enfant",
        "description": "Mot-clé 'adolescent' détecté"
    },
    {
        "texte": "adulte jeune avec appendicite",
        "expected_population": "adulte",
        "description": "Mot-clé 'adulte' détecté"
    },
    {
        "texte": "personne agee avec confusion",
        "expected_population": "personne_agee",
        "description": "Mot-clé 'personne agée' détecté"
    },
    
    # Tests mixtes (âge + mot-clé)
    {
        "texte": "enfant 8 ans douleur abdominale",
        "expected_population": "enfant",
        "description": "Âge 8 ans + mot-clé 'enfant'"
    },
    {
        "texte": "adulte 45 ans suspicion appendicite",
        "expected_population": "adulte",
        "description": "Âge 45 ans + mot-clé 'adulte'"
    },
    
    # Tests pédiatriques spécifiques
    {
        "texte": "patient pediatrique avec fievre",
        "expected_population": "enfant",
        "description": "Mot-clé 'pédiatrique' détecté"
    },
    {
        "texte": "nouveau-ne avec detresse respiratoire",
        "expected_population": "enfant",
        "description": "Mot-clé 'nouveau-né' détecté"
    },
    
    # Cas limites (frontières d'âge)
    {
        "texte": "patient 17 ans traumatisme",
        "expected_population": "enfant",
        "description": "Âge limite 17 ans → enfant"
    },
    {
        "texte": "patient 18 ans consultation",
        "expected_population": "adulte",
        "description": "Âge limite 18 ans → adulte"
    },
    {
        "texte": "patient 64 ans suivi",
        "expected_population": "adulte",
        "description": "Âge limite 64 ans → adulte"
    },
    {
        "texte": "patient 65 ans bilan",
        "expected_population": "personne_agee",
        "description": "Âge limite 65 ans → personne âgée"
    },
]

def test_population_detection():
    """Teste la détection de population."""
    print("=" * 80)
    print("TESTS DE DÉTECTION AUTOMATIQUE DE POPULATION")
    print("=" * 80)
    print(f"\n{len(TEST_CASES)} tests à exécuter\n")
    
    successes = 0
    failures = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        texte = test_case["texte"]
        expected = test_case["expected_population"]
        description = test_case["description"]
        
        # Analyser le texte
        result = analyse_texte_medical(texte)
        actual = result.get("population")
        
        # Vérifier le résultat
        if actual == expected:
            successes += 1
            status = "✓"
            print(f"{status} Test {i}: {description}")
            print(f"   Texte: \"{texte}\"")
            print(f"   → {actual}")
        else:
            failures.append({
                "test_num": i,
                "description": description,
                "texte": texte,
                "expected": expected,
                "actual": actual,
                "age": result.get("age")
            })
            status = "✗"
            print(f"{status} Test {i}: {description}")
            print(f"   Texte: \"{texte}\"")
            print(f"   Attendu: {expected}, Obtenu: {actual}")
            if result.get("age"):
                print(f"   (Âge détecté: {result['age']} ans)")
        print()
    
    # Résumé
    success_rate = (successes / len(TEST_CASES) * 100) if TEST_CASES else 0
    print("=" * 80)
    print("RÉSULTATS")
    print("=" * 80)
    print(f"Total: {len(TEST_CASES)}")
    print(f"✓ Succès: {successes} ({success_rate:.1f}%)")
    print(f"✗ Échecs: {len(failures)}")
    
    if failures:
        print("\n" + "=" * 80)
        print("DÉTAILS DES ÉCHECS")
        print("=" * 80)
        for failure in failures:
            print(f"\nTest {failure['test_num']}: {failure['description']}")
            print(f"  Texte: \"{failure['texte']}\"")
            print(f"  Attendu: {failure['expected']}")
            print(f"  Obtenu: {failure['actual']}")
            if failure['age']:
                print(f"  Âge détecté: {failure['age']} ans")
    
    print("\n" + "=" * 80)
    
    return success_rate >= 95  # Seuil de réussite à 95%

if __name__ == "__main__":
    success = test_population_detection()
    sys.exit(0 if success else 1)
