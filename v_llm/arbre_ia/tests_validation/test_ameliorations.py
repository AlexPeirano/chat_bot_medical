"""Implémentation des améliorations critiques et haute priorité.

PHASE 1 - Critique (Sécurité patient)
PHASE 2 - Haute (Robustesse)
"""

from headache_assistants.nlu import parse_free_text_to_case
from headache_assistants.models import HeadacheCase


def test_ameliorations_phase1():
    """Test des améliorations critiques de sécurité patient."""
    
    print("=" * 80)
    print("PHASE 1 - AMÉLIORATIONS CRITIQUES (Sécurité Patient)")
    print("=" * 80)
    
    # Test 1: Validation température (fièvre si ≥38°C)
    print("\n1. VALIDATION TEMPÉRATURE STRICTE")
    print("-" * 80)
    
    test_cases_temp = [
        ("Céphalée avec T° 37.8", False, "37.8°C < 38°C → pas de fièvre"),
        ("Céphalée avec fièvre 38.2°C", True, "38.2°C ≥ 38°C → fièvre"),
        ("T=39°C depuis hier", True, "39°C ≥ 38°C → fièvre"),
        ("Température 37.5", False, "37.5°C < 38°C → pas de fièvre"),
    ]
    
    for text, expected_fever, description in test_cases_temp:
        case, _ = parse_free_text_to_case(text)
        status = "✅" if case.fever == expected_fever else "❌"
        print(f"{status} {description}")
        print(f"   Texte: '{text}'")
        print(f"   Fever: {case.fever} (attendu: {expected_fever})")
    
    # Test 2: Détection contradictions
    print("\n2. DÉTECTION CONTRADICTIONS")
    print("-" * 80)
    
    test_cases_contradictions = [
        ("Céphalée brutale progressive", "onset contradictoire: thunderclap vs progressive"),
        ("Fièvre mais apyrétique", "fever contradictoire: True vs False"),
        ("Depuis 2j chronique", "durée vs profile: 48h incompatible avec chronic"),
    ]
    
    for text, expected_contradiction in test_cases_contradictions:
        case, metadata = parse_free_text_to_case(text)
        print(f"📝 {expected_contradiction}")
        print(f"   Texte: '{text}'")
        print(f"   Onset: {case.onset}, Profile: {case.profile}, Durée: {case.duration_current_episode_hours}h")
        print(f"   ⚠️ À IMPLÉMENTER: Détection automatique de cette contradiction")
    
    # Test 3: Cross-validation durée vs profile
    print("\n3. CROSS-VALIDATION DURÉE VS PROFILE")
    print("-" * 80)
    
    test_cases_cross = [
        ("Depuis 3 mois, céphalées", 2160.0, "chronic", True),
        ("Depuis 48h chronique", 48.0, "chronic", False),  # Incohérent
        ("Céphalée aiguë depuis 6 mois", 4320.0, "acute", False),  # Incohérent
    ]
    
    for text, expected_duration, expected_profile, should_be_coherent in test_cases_cross:
        case, _ = parse_free_text_to_case(text)
        
        # Vérifier cohérence
        coherent = True
        if case.duration_current_episode_hours and case.profile != "unknown":
            if case.duration_current_episode_hours < 168 and case.profile != "acute":
                coherent = False
            elif 168 <= case.duration_current_episode_hours < 2160 and case.profile != "subacute":
                coherent = False
            elif case.duration_current_episode_hours >= 2160 and case.profile != "chronic":
                coherent = False
        
        status = "✅" if coherent == should_be_coherent else "⚠️"
        print(f"{status} Texte: '{text}'")
        print(f"   Durée: {case.duration_current_episode_hours}h, Profile: {case.profile}")
        print(f"   Cohérence: {coherent} (attendu: {should_be_coherent})")


def test_ameliorations_phase2():
    """Test des améliorations haute priorité (robustesse)."""
    
    print("\n" + "=" * 80)
    print("PHASE 2 - AMÉLIORATIONS HAUTE PRIORITÉ (Robustesse)")
    print("=" * 80)
    
    # Test 1: Pattern "il y a X j/h/sem"
    print("\n1. PATTERN 'IL Y A X TEMPS'")
    print("-" * 80)
    
    test_cases_il_y_a = [
        ("Céphalée commencée il y a 3 jours", 72.0, "acute"),
        ("Mal de tête il y a 2h", 2.0, "acute"),
        ("Il y a 3 semaines, début douleur", 504.0, "subacute"),
        ("Il y a 1 mois, céphalées", 720.0, "subacute"),
    ]
    
    for text, expected_duration, expected_profile in test_cases_il_y_a:
        case, _ = parse_free_text_to_case(text)
        
        duration_ok = (case.duration_current_episode_hours is not None and
                      abs(case.duration_current_episode_hours - expected_duration) < 1)
        profile_ok = case.profile == expected_profile
        
        status = "✅" if (duration_ok and profile_ok) else "❌"
        print(f"{status} '{text}'")
        print(f"   Durée: {case.duration_current_episode_hours}h (attendu: {expected_duration}h)")
        print(f"   Profile: {case.profile} (attendu: {expected_profile})")
        
        if not duration_ok:
            print(f"   ⚠️ À IMPLÉMENTER: Pattern 'il y a X temps'")
    
    # Test 2: Pattern "ça fait X que"
    print("\n2. PATTERN 'ÇA FAIT X QUE'")
    print("-" * 80)
    
    test_cases_ca_fait = [
        ("Ça fait 3 jours que j'ai mal", 72.0, "acute"),
        ("Cela fait 2 semaines que ça dure", 336.0, "subacute"),
    ]
    
    for text, expected_duration, expected_profile in test_cases_ca_fait:
        case, _ = parse_free_text_to_case(text)
        
        duration_ok = (case.duration_current_episode_hours is not None and
                      abs(case.duration_current_episode_hours - expected_duration) < 1)
        
        status = "✅" if duration_ok else "❌"
        print(f"{status} '{text}'")
        print(f"   Durée: {case.duration_current_episode_hours}h (attendu: {expected_duration}h)")
        
        if not duration_ok:
            print(f"   ⚠️ À IMPLÉMENTER: Pattern 'ça fait X que'")
    
    # Test 3: Multiple EVA → max
    print("\n3. MULTIPLE EVA VALUES → MAXIMUM")
    print("-" * 80)
    
    test_cases_multi_eva = [
        ("Fond douloureux EVA 3/10, crises EVA 8/10", 8, "Devrait prendre max (8)"),
        ("EVA habituelle 2, mais aujourd'hui 9/10", 9, "Devrait prendre max (9)"),
    ]
    
    for text, expected_max, description in test_cases_multi_eva:
        case, _ = parse_free_text_to_case(text)
        
        status = "✅" if case.intensity == expected_max else "❌"
        print(f"{status} {description}")
        print(f"   Texte: '{text}'")
        print(f"   Intensité: {case.intensity} (attendu: {expected_max})")
        
        if case.intensity != expected_max:
            print(f"   ⚠️ À IMPLÉMENTER: Extraction multiple EVA + max()")
    
    # Test 4: Validation âges aberrants
    print("\n4. VALIDATION ÂGES ABERRANTS")
    print("-" * 80)
    
    test_cases_age = [
        ("Femme 500 ans céphalée", None, "Âge aberrant devrait être rejeté"),
        ("Homme -5 ans", None, "Âge négatif invalide"),
        ("Patient 0 ans", None, "Âge 0 invalide pour adulte"),
        ("Femme 45 ans", 45, "Âge valide"),
    ]
    
    for text, expected_valid_age, description in test_cases_age:
        case, _ = parse_free_text_to_case(text)
        
        # Vérifier si âge est dans range valide
        age_valid = case.age is not None and 1 <= case.age <= 120
        
        if expected_valid_age is None:
            status = "⚠️" if not age_valid else "❌"
        else:
            status = "✅" if case.age == expected_valid_age else "❌"
        
        print(f"{status} {description}")
        print(f"   Texte: '{text}'")
        print(f"   Âge extrait: {case.age}")
        
        if expected_valid_age is None and age_valid:
            print(f"   ⚠️ À IMPLÉMENTER: Validation range âge (1-120)")


def generate_implementation_guide():
    """Génère un guide d'implémentation priorisé."""
    
    print("\n" + "=" * 80)
    print("GUIDE D'IMPLÉMENTATION PRIORISÉ")
    print("=" * 80)
    
    implementations = [
        {
            "priority": "1-CRITICAL",
            "item": "Validation température ≥38°C",
            "file": "headache_assistants/nlu.py",
            "location": "FEVER_PATTERNS",
            "code": """
# Ajouter validation numérique après détection pattern
if 't°' in text_lower or 'température' in text_lower:
    match = re.search(r'(\\d+(?:\\.\\d+)?)\\s*°', text_lower)
    if match:
        temp = float(match.group(1))
        fever = temp >= 38.0  # Seuil strict 38°C
""",
            "impact": "Évite faux positifs fièvre (37.5-37.9°C)"
        },
        {
            "priority": "1-CRITICAL",
            "item": "Détection contradictions",
            "file": "headache_assistants/nlu.py",
            "location": "parse_free_text_to_case() - fin",
            "code": """
# Ajouter validation contradictions
contradictions = []
if case.onset in ['thunderclap', 'progressive'] and 'progressive' in text and 'brutal' in text:
    contradictions.append('onset_conflicting')
if case.fever is True and 'apyrétique' in text.lower():
    contradictions.append('fever_conflicting')
metadata['contradictions'] = contradictions
""",
            "impact": "Signale textes ambigus nécessitant clarification"
        },
        {
            "priority": "2-HIGH",
            "item": "Pattern 'il y a X temps'",
            "file": "headache_assistants/nlu.py",
            "location": "extract_duration_hours() - nouvelle priorité 12",
            "code": """
# PRIORITÉ 12: "il y a X j/h/sem/mois"
match = re.search(r'il y a (\\d+)\\s*(h(?:eures?)?|j(?:ours?)?|sem(?:aines?)?|mois)', text_lower)
if match:
    value = int(match.group(1))
    unit = match.group(2)
    if 'h' in unit:
        return float(value)
    elif 'j' in unit:
        return float(value) * 24
    elif 'sem' in unit:
        return float(value) * 7 * 24
    elif 'mois' in unit:
        return float(value) * 30 * 24
""",
            "impact": "Support tournure temporelle courante"
        },
        {
            "priority": "2-HIGH",
            "item": "Pattern 'ça fait X que'",
            "file": "headache_assistants/nlu.py",
            "location": "extract_duration_hours() - nouvelle priorité 13",
            "code": """
# PRIORITÉ 13: "ça/cela fait X temps que"
match = re.search(r'(?:ça|cela) fait (\\d+)\\s*(h(?:eures?)?|j(?:ours?)?|sem(?:aines?)?|mois)', text_lower)
if match:
    value = int(match.group(1))
    unit = match.group(2)
    # Même conversion que "il y a"
""",
            "impact": "Support langage familier"
        },
        {
            "priority": "2-HIGH",
            "item": "Multiple EVA → maximum",
            "file": "headache_assistants/nlu.py",
            "location": "extract_intensity_score()",
            "code": """
# Au lieu de retourner premier match, chercher tous
all_evas = []
for match in re.finditer(r'(\\d{1,2})(?:-(\\d{1,2}))?\\s*/\\s*10', text):
    score = int(match.group(1))
    if match.group(2):  # Range
        score2 = int(match.group(2))
        score = max(score, score2)  # Max du range
    all_evas.append(score)

if all_evas:
    return max(all_evas)  # Retourner maximum de tous les EVA
""",
            "impact": "Capture intensité maximale (cliniquement pertinent)"
        },
        {
            "priority": "2-HIGH",
            "item": "Validation âge 1-120",
            "file": "headache_assistants/nlu.py",
            "location": "extract_age()",
            "code": """
# Après extraction âge
if age is not None:
    if not (1 <= age <= 120):
        return None  # Rejeter âges aberrants
    return age
""",
            "impact": "Évite données aberrantes"
        }
    ]
    
    print("\nIMPLÉMENTATIONS RECOMMANDÉES (ordre de priorité):\n")
    
    for i, impl in enumerate(implementations, 1):
        print(f"\n{i}. [{impl['priority']}] {impl['item']}")
        print(f"   Fichier: {impl['file']}")
        print(f"   Localisation: {impl['location']}")
        print(f"   Impact: {impl['impact']}")
        print(f"   Code:{impl['code']}")


if __name__ == "__main__":
    test_ameliorations_phase1()
    test_ameliorations_phase2()
    generate_implementation_guide()
    
    print("\n" + "=" * 80)
    print("FIN DES TESTS D'AMÉLIORATION")
    print("=" * 80)
    print("\n✅ Améliorations identifiées et priorisées")
    print("⚠️  Certaines nécessitent implémentation (voir guide ci-dessus)")
