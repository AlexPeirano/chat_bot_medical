"""Tests complets du système de dialogue pour valider le workflow end-to-end."""

from headache_assistants.dialogue import handle_user_message, reset_session
from headache_assistants.models import ChatMessage
import json


def print_separator(title):
    """Affiche un séparateur visuel."""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def test_urgence_hsa():
    """Test cas d'urgence vitale - HSA (Hémorragie Sous-Arachnoïdienne)."""
    print_separator("TEST 1: URGENCE VITALE - HSA (Coup de tonnerre)")
    
    session_id = "test_hsa"
    
    msg = ChatMessage(
        role="user",
        content="Femme 45 ans, céphalée brutale coup de tonnerre il y a 2h, EVA 10/10, pire douleur de sa vie"
    )
    
    response = handle_user_message([], msg, session_id=session_id)
    
    print(f"\nMessage: {msg.content}")
    print(f"\nCas extrait:")
    print(f"  - onset: {response.headache_case.onset}")
    print(f"  - intensity: {response.headache_case.intensity}")
    print(f"  - profile: {response.headache_case.profile}")
    
    print(f"\nDialogue terminé: {response.dialogue_complete}")
    
    if response.imaging_recommendation:
        print(f"\nRecommandation:")
        print(f"  - Urgence: {response.imaging_recommendation.urgency}")
        print(f"  - Imageries: {', '.join(response.imaging_recommendation.imaging)}")
        print(f"  - Commentaire: {response.imaging_recommendation.comment[:100]}...")
        
        if response.imaging_recommendation.urgency == "immediate":
            print("\n✅ URGENCE correctement détectée")
        else:
            print(f"\n❌ ERREUR: Urgence devrait être 'immediate', pas '{response.imaging_recommendation.urgency}'")
    else:
        print("\n❌ ERREUR: Aucune recommandation générée pour urgence vitale!")
    
    reset_session(session_id)


def test_meningite():
    """Test cas méningite - fièvre + raideur nuque."""
    print_separator("TEST 2: URGENCE - Méningite (Fièvre + Raideur)")
    
    session_id = "test_meningite"
    messages = []
    
    # Message initial
    msg1 = ChatMessage(role="user", content="Homme 30 ans, céphalée depuis 24h, fièvre 39°C")
    messages.append(msg1)
    response = handle_user_message([], msg1, session_id=session_id)
    
    print(f"\nMessage 1: {msg1.content}")
    print(f"Fever détecté: {response.headache_case.fever}")
    print(f"Question: {response.next_question[:80] if response.next_question else 'Aucune'}...")
    
    # Si question sur raideur nuque, répondre oui
    if response.next_question and "nuque" in response.next_question.lower():
        messages.append(ChatMessage(role="assistant", content=response.message))
        msg2 = ChatMessage(role="user", content="oui, nuque très raide")
        messages.append(msg2)
        response = handle_user_message(messages[:-1], msg2, session_id=session_id)
        
        print(f"\nMessage 2: {msg2.content}")
        print(f"Meningeal_signs détecté: {response.headache_case.meningeal_signs}")
    
    print(f"\nDialogue terminé: {response.dialogue_complete}")
    
    if response.imaging_recommendation:
        print(f"\nRecommandation:")
        print(f"  - Urgence: {response.imaging_recommendation.urgency}")
        print(f"  - Commentaire: {response.imaging_recommendation.comment[:100]}...")
        
        if response.imaging_recommendation.urgency in ["immediate", "urgent"]:
            print("\n✅ URGENCE méningite correctement détectée")
        else:
            print(f"\n❌ ERREUR: Urgence insuffisante pour méningite")
    
    reset_session(session_id)


def test_cephalee_post_pl():
    """Test céphalée post-ponction lombaire."""
    print_separator("TEST 3: Céphalée Post-Ponction Lombaire")
    
    session_id = "test_post_pl"
    
    msg = ChatMessage(
        role="user",
        content="Femme 35 ans, PL il y a 3j, depuis céphalée intense, amélioration complète en décubitus, EVA debout 8/10"
    )
    
    response = handle_user_message([], msg, session_id=session_id)
    
    print(f"\nMessage: {msg.content}")
    print(f"\nCas extrait:")
    print(f"  - recent_pl_or_peridural: {response.headache_case.recent_pl_or_peridural}")
    print(f"  - intensity: {response.headache_case.intensity}")
    print(f"  - profile: {response.headache_case.profile}")
    
    # Le dialogue peut continuer pour vérifier red flags
    dialogue_count = 1
    while not response.dialogue_complete and dialogue_count < 10:
        print(f"\nQuestion {dialogue_count}: {response.next_question[:60]}...")
        
        # Répondre "non" aux red flags
        messages = [msg, ChatMessage(role="assistant", content=response.message)]
        msg_reply = ChatMessage(role="user", content="non")
        messages.append(msg_reply)
        response = handle_user_message(messages[:-1], msg_reply, session_id=session_id)
        dialogue_count += 1
    
    print(f"\nDialogue terminé après {dialogue_count} échanges")
    
    if response.imaging_recommendation:
        print(f"\nRecommandation:")
        print(f"  - Urgence: {response.imaging_recommendation.urgency}")
        print(f"  - Imageries: {', '.join(response.imaging_recommendation.imaging)}")
        print(f"  - Commentaire: {response.imaging_recommendation.comment[:150]}...")
        
        if response.headache_case.recent_pl_or_peridural is True:
            print("\n✅ Post-PL correctement détecté")
        else:
            print("\n❌ ERREUR: Post-PL non détecté")
    
    reset_session(session_id)


def test_migraine_simple():
    """Test migraine simple sans red flags - ne devrait pas nécessiter d'imagerie."""
    print_separator("TEST 4: Migraine Simple Sans Red Flags")
    
    session_id = "test_migraine"
    messages = []
    
    msg1 = ChatMessage(
        role="user",
        content="Femme 28 ans, céphalée unilatérale gauche pulsatile depuis ce matin, nausées, photophobie, EVA 7/10"
    )
    messages.append(msg1)
    response = handle_user_message([], msg1, session_id=session_id)
    
    print(f"\nMessage initial: {msg1.content}")
    print(f"\nCas extrait:")
    print(f"  - headache_profile: {response.headache_case.headache_profile}")
    print(f"  - intensity: {response.headache_case.intensity}")
    print(f"  - profile: {response.headache_case.profile}")
    
    # Répondre "non" à toutes les questions de red flags
    dialogue_count = 1
    while not response.dialogue_complete and dialogue_count < 15:
        if response.next_question:
            print(f"\nQ{dialogue_count}: {response.next_question[:60]}...")
            messages.append(ChatMessage(role="assistant", content=response.message))
            
            # Répondre "non" aux red flags
            msg_reply = ChatMessage(role="user", content="non")
            messages.append(msg_reply)
            response = handle_user_message(messages[:-1], msg_reply, session_id=session_id)
            dialogue_count += 1
        else:
            break
    
    print(f"\nDialogue terminé après {dialogue_count} échanges")
    
    if response.imaging_recommendation:
        print(f"\nRecommandation:")
        print(f"  - Urgence: {response.imaging_recommendation.urgency}")
        print(f"  - Imageries: {', '.join(response.imaging_recommendation.imaging)}")
        
        if "aucun" in response.imaging_recommendation.imaging or len(response.imaging_recommendation.imaging) == 0:
            print("\n✅ Aucune imagerie recommandée (correct pour migraine simple)")
        else:
            print(f"\n⚠️ Imagerie recommandée pour migraine simple: {response.imaging_recommendation.imaging}")
    
    reset_session(session_id)


def test_cephalee_chronique_htic():
    """Test céphalée chronique avec signes HTIC - nécessite imagerie."""
    print_separator("TEST 5: Céphalée Chronique avec Signes HTIC")
    
    session_id = "test_htic"
    messages = []
    
    msg1 = ChatMessage(
        role="user",
        content="Homme 50 ans, céphalées quotidiennes depuis 3 mois, pires le matin au réveil, vomissements en jet"
    )
    messages.append(msg1)
    response = handle_user_message([], msg1, session_id=session_id)
    
    print(f"\nMessage initial: {msg1.content}")
    print(f"\nCas extrait:")
    print(f"  - profile: {response.headache_case.profile}")
    print(f"  - htic_pattern: {response.headache_case.htic_pattern}")
    
    # Répondre aux questions
    dialogue_count = 1
    while not response.dialogue_complete and dialogue_count < 15:
        if response.next_question:
            print(f"\nQ{dialogue_count}: {response.next_question[:70]}...")
            messages.append(ChatMessage(role="assistant", content=response.message))
            
            # Répondre "non" sauf pour HTIC qui est déjà détecté
            msg_reply = ChatMessage(role="user", content="non")
            messages.append(msg_reply)
            response = handle_user_message(messages[:-1], msg_reply, session_id=session_id)
            dialogue_count += 1
        else:
            break
    
    print(f"\nDialogue terminé après {dialogue_count} échanges")
    
    if response.imaging_recommendation:
        print(f"\nRecommandation:")
        print(f"  - Urgence: {response.imaging_recommendation.urgency}")
        print(f"  - Imageries: {', '.join(response.imaging_recommendation.imaging)}")
        
        if any(img in ['irm_cerebrale', 'scanner_cerebral'] for img in response.imaging_recommendation.imaging):
            print("\n✅ Imagerie cérébrale recommandée (correct pour HTIC)")
        else:
            print(f"\n❌ ERREUR: Pas d'imagerie cérébrale pour signes HTIC")
    
    reset_session(session_id)


def test_extraction_durées():
    """Test extraction des durées en différents formats."""
    print_separator("TEST 6: Extraction Durées (Formats Français Médicaux)")
    
    test_cases = [
        ("depuis 2h", "acute", 2.0),
        ("depuis 48h", "acute", 48.0),
        ("depuis 5j", "acute", 120.0),  # 5*24 = 120h
        ("depuis 3 semaines", "subacute", 504.0),  # 3*7*24 = 504h
        ("depuis 4 mois", "chronic", None),  # > 3 mois
        ("crises de 45min", None, 0.75),  # 45/60 = 0.75h
        ("durée totale 8h", None, 8.0),
        ("céphalée 30-60min", None, 0.75),  # moyenne (30+60)/2/60
    ]
    
    results = []
    for text, expected_profile, expected_duration in test_cases:
        session_id = f"test_duree_{len(results)}"
        msg = ChatMessage(role="user", content=f"Patient avec céphalée {text}")
        response = handle_user_message([], msg, session_id=session_id)
        
        case = response.headache_case
        duration = case.duration_current_episode_hours
        profile = case.profile
        
        profile_ok = (expected_profile is None or profile == expected_profile)
        duration_ok = (expected_duration is None or 
                      (duration is not None and abs(duration - expected_duration) < 1.5))
        
        status = "✅" if (profile_ok and duration_ok) else "❌"
        
        results.append({
            "text": text,
            "expected_profile": expected_profile,
            "got_profile": profile,
            "expected_duration": expected_duration,
            "got_duration": duration,
            "status": status
        })
        
        print(f"\n{status} '{text}'")
        print(f"   Profile: {profile} (attendu: {expected_profile})")
        print(f"   Durée: {duration}h (attendu: {expected_duration}h)")
        
        reset_session(session_id)
    
    success_count = sum(1 for r in results if r["status"] == "✅")
    print(f"\n{'='*80}")
    print(f"Résultat: {success_count}/{len(results)} extractions correctes ({success_count*100//len(results)}%)")


def test_extraction_intensites():
    """Test extraction des intensités EVA."""
    print_separator("TEST 7: Extraction Intensités EVA")
    
    test_cases = [
        ("EVA 7/10", 7),
        ("EVA max 10", 10),
        ("douleur 3/10", 3),
        ("douleur maximale", 10),
        ("douleur insupportable", 10),
        ("douleur modérée", 5),
        ("douleur légère", 3),
        ("EVA 4-6/10", 5),  # moyenne
    ]
    
    results = []
    for text, expected_intensity in test_cases:
        session_id = f"test_intensity_{len(results)}"
        msg = ChatMessage(role="user", content=f"Patient avec céphalée, {text}")
        response = handle_user_message([], msg, session_id=session_id)
        
        intensity = response.headache_case.intensity
        
        # Tolérance ±1 pour les approximations
        intensity_ok = (intensity is not None and abs(intensity - expected_intensity) <= 1)
        
        status = "✅" if intensity_ok else "❌"
        
        results.append({
            "text": text,
            "expected": expected_intensity,
            "got": intensity,
            "status": status
        })
        
        print(f"{status} '{text}' → {intensity} (attendu: {expected_intensity})")
        
        reset_session(session_id)
    
    success_count = sum(1 for r in results if r["status"] == "✅")
    print(f"\n{'='*80}")
    print(f"Résultat: {success_count}/{len(results)} extractions correctes ({success_count*100//len(results)}%)")


def test_abreviations_medicales():
    """Test reconnaissance des abréviations médicales françaises."""
    print_separator("TEST 8: Abréviations Médicales Françaises")
    
    test_cases = [
        ("N+ V+ photo+ phono+", "migraine_like"),  # Signes migraineux
        ("bilat, diffuses, Ø signes associés", "tension_like"),  # CTT
        ("CCH chroniques quotidiennes", "chronic"),  # Profile chronique
        ("AVF crises 30min", None),  # AVF pattern
        ("PL il y a 2j", True),  # recent_pl_or_peridural
    ]
    
    results = []
    for text, expected_value in test_cases:
        session_id = f"test_abbrev_{len(results)}"
        msg = ChatMessage(role="user", content=f"Patient avec {text}")
        response = handle_user_message([], msg, session_id=session_id)
        
        case = response.headache_case
        
        # Vérifier différents champs selon le test
        if expected_value in ["migraine_like", "tension_like"]:
            got_value = case.headache_profile
            match = (got_value == expected_value)
        elif expected_value == "chronic":
            got_value = case.profile
            match = (got_value == expected_value)
        elif isinstance(expected_value, bool):
            got_value = case.recent_pl_or_peridural
            match = (got_value == expected_value)
        else:
            got_value = "N/A"
            match = True
        
        status = "✅" if match else "❌"
        
        results.append({
            "text": text,
            "expected": expected_value,
            "got": got_value,
            "status": status
        })
        
        print(f"{status} '{text}' → {got_value} (attendu: {expected_value})")
        
        reset_session(session_id)
    
    success_count = sum(1 for r in results if r["status"] == "✅")
    print(f"\n{'='*80}")
    print(f"Résultat: {success_count}/{len(results)} reconnaissances correctes ({success_count*100//len(results)}%)")


def generate_summary():
    """Génère un résumé des résultats de tous les tests."""
    print_separator("RÉSUMÉ DES TESTS")
    
    print("\n✅ Tests de scénarios cliniques:")
    print("  1. Urgence vitale HSA (coup de tonnerre)")
    print("  2. Urgence méningite (fièvre + raideur)")
    print("  3. Céphalée post-ponction lombaire")
    print("  4. Migraine simple sans red flags")
    print("  5. Céphalée chronique avec signes HTIC")
    
    print("\n✅ Tests d'extraction NLU:")
    print("  6. Extraction durées (formats français)")
    print("  7. Extraction intensités EVA")
    print("  8. Reconnaissance abréviations médicales")
    
    print("\n" + "="*80)
    print("Tous les tests sont terminés.")
    print("Vérifiez les résultats ci-dessus pour identifier d'éventuels problèmes.")
    print("="*80)


if __name__ == "__main__":
    # Tests de scénarios cliniques
    test_urgence_hsa()
    test_meningite()
    test_cephalee_post_pl()
    test_migraine_simple()
    test_cephalee_chronique_htic()
    
    # Tests d'extraction NLU
    test_extraction_durées()
    test_extraction_intensites()
    test_abreviations_medicales()
    
    # Résumé
    generate_summary()
