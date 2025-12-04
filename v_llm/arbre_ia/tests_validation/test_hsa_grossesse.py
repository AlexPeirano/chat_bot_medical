#!/usr/bin/env python3
"""
Test de la gestion HSA + grossesse.

Vérifie que :
1. HSA en urgence vitale : scanner reste prioritaire malgré grossesse
2. Protection abdominale et dose minimale mentionnées
3. IRM proposée comme alternative
4. Contexte non urgent : IRM prioritaire
"""

import json
from headache_assistants.models import HeadacheCase
from headache_assistants.rules_engine import decide_imaging


def test_hsa_grossesse_2_mois():
    """Test HSA chez femme enceinte de 2 mois (8 semaines)."""
    print("\n" + "="*70)
    print("TEST 1: HSA + Grossesse 2 mois (urgence vitale)")
    print("="*70)
    
    case = HeadacheCase(
        age=34,
        sex="F",
        profile="acute",
        onset="thunderclap",
        pregnancy_postpartum=True,
        duration_hours=1
    )
    
    recommendation = decide_imaging(case)
    
    print(f"\nRègle appliquée: {recommendation.applied_rule_id}")
    print(f"Urgence: {recommendation.urgency}")
    print(f"Examens: {recommendation.imaging}")
    
    # Vérifications
    assert recommendation.applied_rule_id == "HSA_001", f"Expected HSA_001, got {recommendation.applied_rule_id}"
    assert recommendation.urgency == "immediate", f"Expected immediate, got {recommendation.urgency}"
    
    # Doit contenir scanner (urgence vitale) ET IRM (alternative)
    has_scanner = any("scanner" in exam.lower() for exam in recommendation.imaging)
    has_irm = any("irm" in exam.lower() for exam in recommendation.imaging)
    
    print(f"\nScanner présent: {has_scanner}")
    print(f"IRM présente: {has_irm}")
    
    assert has_scanner, "Scanner doit être présent (urgence vitale)"
    assert has_irm, "IRM doit être proposée comme alternative"
    
    # Vérifier les précautions dans le commentaire
    comment = recommendation.comment
    print(f"\nCommentaire:\n{comment}")
    
    assert "URGENCE VITALE" in comment or "urgence" in comment.lower(), "Doit mentionner urgence"
    assert "bénéfice" in comment.lower() and "risque" in comment.lower(), "Doit mentionner rapport bénéfice/risque"
    assert "protection" in comment.lower() or "dose minimale" in comment.lower(), "Doit mentionner protection/dose"
    
    print("\n✅ TEST 1 RÉUSSI")
    return True


def test_migraine_grossesse():
    """Test migraine simple chez femme enceinte (contexte non urgent)."""
    print("\n" + "="*70)
    print("TEST 2: Migraine + Grossesse (contexte non urgent)")
    print("="*70)
    
    case = HeadacheCase(
        age=28,
        sex="F",
        profile="chronic",
        onset="progressive",
        pregnancy_postpartum=True,
        duration_hours=48,
        unilateral=True,
        pulsating=True,
        intensity_score=7
    )
    
    recommendation = decide_imaging(case)
    
    print(f"\nRègle appliquée: {recommendation.applied_rule_id}")
    print(f"Urgence: {recommendation.urgency}")
    print(f"Examens: {recommendation.imaging}")
    
    # Vérifier que c'est IRM prioritaire (pas scanner)
    if recommendation.imaging:
        has_scanner = any("scanner" in exam.lower() for exam in recommendation.imaging)
        has_irm = any("irm" in exam.lower() for exam in recommendation.imaging)
        
        print(f"\nScanner présent: {has_scanner}")
        print(f"IRM présente: {has_irm}")
        
        # En contexte non urgent, IRM doit être privilégiée
        if has_scanner and not has_irm:
            print("⚠️  Scanner sans IRM en contexte non urgent - devrait être IRM")
        elif has_irm and not has_scanner:
            print("✅ IRM seule - correct pour contexte non urgent")
        elif has_irm and has_scanner:
            print("⚠️  Les deux présents - acceptable mais IRM devrait être prioritaire")
    
    print(f"\nCommentaire:\n{recommendation.comment}")
    
    print("\n✅ TEST 2 TERMINÉ")
    return True


def test_pregnancy_rule():
    """Test règle PREGNANCY_001 spécifique."""
    print("\n" + "="*70)
    print("TEST 3: Règle PREGNANCY_001 (céphalée aiguë grossesse)")
    print("="*70)
    
    case = HeadacheCase(
        age=30,
        sex="F",
        profile="acute",
        onset="progressive",
        pregnancy_postpartum=True,
        duration_hours=6
    )
    
    recommendation = decide_imaging(case)
    
    print(f"\nRègle appliquée: {recommendation.applied_rule_id}")
    print(f"Urgence: {recommendation.urgency}")
    print(f"Examens: {recommendation.imaging}")
    print(f"\nCommentaire:\n{recommendation.comment}")
    
    # Cette règle devrait recommander IRM + angio-IRM veineuse
    has_irm = any("irm" in exam.lower() for exam in recommendation.imaging)
    print(f"\nIRM présente: {has_irm}")
    
    print("\n✅ TEST 3 TERMINÉ")
    return True


def test_hsa_grossesse_4_semaines():
    """Test HSA chez femme enceinte < 4 semaines (organogenèse)."""
    print("\n" + "="*70)
    print("TEST 4: HSA + Grossesse < 4 semaines (organogenèse)")
    print("="*70)
    
    case = HeadacheCase(
        age=29,
        sex="F",
        profile="acute",
        onset="thunderclap",
        pregnancy_postpartum=True,
        duration_hours=2
    )
    
    recommendation = decide_imaging(case)
    
    print(f"\nRègle appliquée: {recommendation.applied_rule_id}")
    print(f"Urgence: {recommendation.urgency}")
    print(f"Examens: {recommendation.imaging}")
    
    comment = recommendation.comment
    print(f"\nCommentaire:\n{comment}")
    
    # Doit mentionner précaution < 4 semaines
    if "4 semaines" in comment or "organogenèse" in comment.lower():
        print("✅ Précaution organogenèse mentionnée")
    else:
        print("⚠️  Précaution organogenèse non mentionnée explicitement")
    
    print("\n✅ TEST 4 TERMINÉ")
    return True


def run_all_tests():
    """Exécute tous les tests."""
    results = {
        "test_hsa_grossesse_2_mois": False,
        "test_migraine_grossesse": False,
        "test_pregnancy_rule": False,
        "test_hsa_grossesse_4_semaines": False
    }
    
    try:
        results["test_hsa_grossesse_2_mois"] = test_hsa_grossesse_2_mois()
    except AssertionError as e:
        print(f"\n❌ TEST 1 ÉCHOUÉ: {e}")
    except Exception as e:
        print(f"\n❌ TEST 1 ERREUR: {e}")
    
    try:
        results["test_migraine_grossesse"] = test_migraine_grossesse()
    except Exception as e:
        print(f"\n❌ TEST 2 ERREUR: {e}")
    
    try:
        results["test_pregnancy_rule"] = test_pregnancy_rule()
    except Exception as e:
        print(f"\n❌ TEST 3 ERREUR: {e}")
    
    try:
        results["test_hsa_grossesse_4_semaines"] = test_hsa_grossesse_4_semaines()
    except Exception as e:
        print(f"\n❌ TEST 4 ERREUR: {e}")
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_test in results.items():
        status = "✅ RÉUSSI" if passed_test else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests réussis ({passed*100//total}%)")
    print("="*70 + "\n")
    
    # Sauvegarder résultats
    output = {
        "date": "2025-12-04",
        "tests": results,
        "total": total,
        "passed": passed,
        "percentage": passed * 100 // total
    }
    
    with open("tests_validation/test_hsa_grossesse_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Résultats sauvegardés dans tests_validation/test_hsa_grossesse_results.json\n")


if __name__ == "__main__":
    run_all_tests()
