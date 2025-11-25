#!/usr/bin/env python3
"""Tests de la gestion des acronymes médicaux."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source'))

from main import _expand_acronyms, analyse_texte_medical, MEDICAL_ACRONYMS

def test_acronym_expansion():
    """Teste l'expansion des acronymes."""
    
    print("=" * 80)
    print("TESTS DE GESTION DES ACRONYMES MÉDICAUX")
    print("=" * 80)
    print()
    
    # Test 1 : Expansion simple
    print("TEST 1 : EXPANSION D'ACRONYMES")
    print("-" * 80)
    
    test_cases = [
        ("douleur FID", "fosse iliaque droite"),
        ("patient avec EP", "embolie pulmonaire"),
        ("suspicion OAP", "œdème aigu pulmonaire"),
        ("douleur HCD", "hypocondre droit"),
        ("RGO chronique", "reflux gastro-œsophagien"),
        ("BPCO décompensée", "bronchopneumopathie chronique obstructive"),
        ("AVC ischémique", "accident vasculaire cérébral"),
    ]
    
    successes = 0
    for texte_original, expected_expansion in test_cases:
        expanded = _expand_acronyms(texte_original)
        
        # Vérifier que l'expansion contient le terme attendu
        has_expansion = expected_expansion.lower() in expanded.lower()
        has_original = texte_original.split()[1].lower() in expanded.lower()  # L'acronyme original
        
        success = has_expansion and has_original
        successes += success
        
        status = "✓" if success else "✗"
        print(f"{status} {texte_original:25} → {expanded}")
        if not success:
            print(f"   Attendu: contient '{expected_expansion}'")
        print()
    
    rate1 = (successes / len(test_cases) * 100) if test_cases else 0
    print(f"Expansion: {successes}/{len(test_cases)} ({rate1:.1f}%)")
    
    # Test 2 : Détection dans contexte médical
    print("\n" + "=" * 80)
    print("TEST 2 : DÉTECTION DANS CONTEXTE CLINIQUE")
    print("-" * 80)
    print()
    
    clinical_cases = [
        {
            "texte": "patient 35 ans douleur FID suspicion appendicite",
            "should_detect": ["fosse iliaque droite", "douleur", "appendicite"],
            "acronym": "FID"
        },
        {
            "texte": "femme 60 ans dyspnée suspicion EP",
            "should_detect": ["embolie pulmonaire", "dyspnée"],
            "acronym": "EP"
        },
        {
            "texte": "homme 45 ans douleur HCD cholécystite",
            "should_detect": ["hypocondre droit", "douleur"],
            "acronym": "HCD"
        },
        {
            "texte": "enfant 8 ans douleur FIG",
            "should_detect": ["fosse iliaque gauche"],
            "acronym": "FIG"
        },
    ]
    
    successes_clinical = 0
    for case in clinical_cases:
        texte = case["texte"]
        acronym = case["acronym"]
        
        # Analyser avec expansion d'acronymes
        f = analyse_texte_medical(texte)
        expanded = _expand_acronyms(texte)
        
        # Vérifier que l'expansion a eu lieu
        all_detected = all(term.lower() in expanded.lower() for term in case["should_detect"])
        
        success = all_detected
        successes_clinical += success
        
        status = "✓" if success else "✗"
        print(f"{status} Acronyme: {acronym}")
        print(f"   Texte original : {texte}")
        print(f"   Texte expansé  : {expanded}")
        
        if f.get("age"):
            print(f"   → Âge: {f['age']} ans")
        if f.get("population"):
            print(f"   → Population: {f['population']}")
        
        for term in case["should_detect"]:
            found = term.lower() in expanded.lower()
            check_status = "✓" if found else "✗"
            print(f"   {check_status} Contient: '{term}'")
        print()
    
    rate2 = (successes_clinical / len(clinical_cases) * 100) if clinical_cases else 0
    print(f"Détection clinique: {successes_clinical}/{len(clinical_cases)} ({rate2:.1f}%)")
    
    # Test 3 : Acronymes multiples
    print("\n" + "=" * 80)
    print("TEST 3 : GESTION D'ACRONYMES MULTIPLES")
    print("-" * 80)
    print()
    
    multi_acronym_cases = [
        {
            "texte": "douleur FID et HCD",
            "acronyms": ["FID", "HCD"],
            "expansions": ["fosse iliaque droite", "hypocondre droit"]
        },
        {
            "texte": "RX thorax puis CT si EP",
            "acronyms": ["RX", "CT", "EP"],
            "expansions": ["radiographie", "scanner", "embolie pulmonaire"]
        },
    ]
    
    successes_multi = 0
    for case in multi_acronym_cases:
        texte = case["texte"]
        expanded = _expand_acronyms(texte)
        
        all_expanded = all(exp.lower() in expanded.lower() for exp in case["expansions"])
        
        success = all_expanded
        successes_multi += success
        
        status = "✓" if success else "✗"
        print(f"{status} Acronymes: {', '.join(case['acronyms'])}")
        print(f"   Original : {texte}")
        print(f"   Expansé  : {expanded}")
        
        for acronym, expansion in zip(case["acronyms"], case["expansions"]):
            found = expansion.lower() in expanded.lower()
            check_status = "✓" if found else "✗"
            print(f"   {check_status} {acronym} → {expansion}")
        print()
    
    rate3 = (successes_multi / len(multi_acronym_cases) * 100) if multi_acronym_cases else 0
    print(f"Acronymes multiples: {successes_multi}/{len(multi_acronym_cases)} ({rate3:.1f}%)")
    
    # Test 4 : Liste des acronymes disponibles
    print("\n" + "=" * 80)
    print("TEST 4 : DICTIONNAIRE D'ACRONYMES DISPONIBLES")
    print("-" * 80)
    print()
    
    print(f"Total d'acronymes définis : {len(MEDICAL_ACRONYMS)}\n")
    
    # Grouper par catégorie
    categories = {
        "Anatomie": ["fid", "fig", "hcd", "hcg", "epigastre", "hypogastre"],
        "Examens": ["irm", "tdm", "ct", "rx", "echo", "us"],
        "Pathologies thorax": ["ep", "oap", "bpco", "htap"],
        "Pathologies digestif": ["rgo", "mici", "ulh"],
        "Symptômes": ["sad", "sca", "avc", "ait"],
    }
    
    for category, acronym_list in categories.items():
        print(f"\n{category}:")
        for acronym in acronym_list:
            if acronym in MEDICAL_ACRONYMS:
                print(f"  • {acronym.upper():8} → {MEDICAL_ACRONYMS[acronym]}")
    
    # Résumé global
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    
    total_tests = len(test_cases) + len(clinical_cases) + len(multi_acronym_cases)
    total_successes = successes + successes_clinical + successes_multi
    total_rate = (total_successes / total_tests * 100) if total_tests else 0
    
    print(f"\nTotal: {total_tests} tests")
    print(f"✓ Succès: {total_successes} ({total_rate:.1f}%)")
    print(f"✗ Échecs: {total_tests - total_successes}")
    
    print(f"\nDétail par catégorie:")
    print(f"  • Expansion simple    : {successes}/{len(test_cases)} ({rate1:.1f}%)")
    print(f"  • Contexte clinique   : {successes_clinical}/{len(clinical_cases)} ({rate2:.1f}%)")
    print(f"  • Acronymes multiples : {successes_multi}/{len(multi_acronym_cases)} ({rate3:.1f}%)")
    
    print("\n💡 Avantages:")
    print("  ✓ Comprend les acronymes médicaux courants")
    print("  ✓ Garde l'acronyme original pour traçabilité")
    print("  ✓ Améliore la détection de symptômes")
    print("  ✓ Extensible facilement (ajouter au dictionnaire)")
    
    print("\n" + "=" * 80)
    
    return total_rate >= 85

if __name__ == "__main__":
    success = test_acronym_expansion()
    sys.exit(0 if success else 1)
