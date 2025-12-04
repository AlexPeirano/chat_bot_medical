"""Test pour vérifier que la question sur ponction lombaire est bien posée."""

from headache_assistants.dialogue import handle_user_message, reset_session
from headache_assistants.models import ChatMessage

def test_pl_question():
    """Test que la question PL est posée quand nécessaire."""
    
    # Cas 1: Patient avec céphalée positionnelle après PL
    print("=" * 80)
    print("TEST 1: Céphalée post-PL mentionnée explicitement")
    print("=" * 80)
    
    msg1 = ChatMessage(
        role="user",
        content="Femme 35 ans, PL il y a 3j, céphalée intense depuis, amélioration en décubitus"
    )
    
    response1 = handle_user_message([], msg1, session_id="test1")
    
    print(f"\nMessage utilisateur: {msg1.content}")
    print(f"\nCas extrait:")
    print(f"  - recent_pl_or_peridural: {response1.headache_case.recent_pl_or_peridural}")
    print(f"  - intensity: {response1.headache_case.intensity}")
    print(f"  - profile: {response1.headache_case.profile}")
    print(f"\nDialogue complet: {response1.dialogue_complete}")
    print(f"Recommandation: {response1.imaging_recommendation.comment if response1.imaging_recommendation else 'Aucune'}")
    
    reset_session("test1")
    
    # Cas 2: Céphalée sans mention de PL - doit poser la question
    print("\n" + "=" * 80)
    print("TEST 2: Céphalée progressive - doit poser question sur PL")
    print("=" * 80)
    
    msg2 = ChatMessage(
        role="user",
        content="Homme 40 ans, céphalée progressive depuis 5j, EVA 6/10"
    )
    
    response2 = handle_user_message([], msg2, session_id="test2")
    
    print(f"\nMessage utilisateur: {msg2.content}")
    print(f"\nCas extrait:")
    print(f"  - recent_pl_or_peridural: {response2.headache_case.recent_pl_or_peridural}")
    print(f"  - onset: {response2.headache_case.onset}")
    print(f"  - profile: {response2.headache_case.profile}")
    print(f"\nDialogue complet: {response2.dialogue_complete}")
    print(f"Prochaine question: {response2.next_question}")
    
    # Vérifier si la question PL est dans la liste des questions possibles
    if response2.next_question and "ponction lombaire" in response2.next_question.lower():
        print("\n✅ Question sur ponction lombaire POSÉE")
    else:
        print("\n❌ Question sur ponction lombaire NON POSÉE")
        print(f"   Question posée: {response2.next_question}")
    
    reset_session("test2")
    
    # Cas 3: Répondre "oui" à la question PL
    print("\n" + "=" * 80)
    print("TEST 3: Réponse 'oui' à la question PL")
    print("=" * 80)
    
    msg3a = ChatMessage(
        role="user",
        content="Homme 40 ans, céphalée progressive depuis 5j, EVA 6/10"
    )
    
    response3a = handle_user_message([], msg3a, session_id="test3")
    print(f"\nPremier message: {msg3a.content}")
    print(f"Réponse système: {response3a.next_question[:100]}...")
    
    # Simuler réponse "oui" à la question PL
    msg3b = ChatMessage(role="user", content="oui")
    history = [msg3a, ChatMessage(role="assistant", content=response3a.message)]
    response3b = handle_user_message(history, msg3b, session_id="test3")
    
    print(f"\nRéponse utilisateur: {msg3b.content}")
    print(f"Cas après réponse:")
    print(f"  - fever: {response3b.headache_case.fever}")
    print(f"  - recent_pl_or_peridural: {response3b.headache_case.recent_pl_or_peridural}")
    
    if response3b.headache_case.fever is True:
        print("\n✅ Réponse 'oui' CORRECTEMENT interprétée pour fever")
    else:
        print(f"\n❌ Réponse 'oui' MAL interprétée pour fever: {response3b.headache_case.fever}")
    
    reset_session("test3")
    
    # Cas 4: Dialogue complet jusqu'à la question PL
    print("\n" + "=" * 80)
    print("TEST 4: Dialogue complet - atteindre question PL et répondre")
    print("=" * 80)
    
    session_id = "test4"
    messages = []
    
    # Message initial
    msg = ChatMessage(role="user", content="Homme 40 ans, céphalée progressive depuis 5j, EVA 6/10")
    messages.append(msg)
    response = handle_user_message(messages[:-1], msg, session_id=session_id)
    print(f"\nMessage 1: {msg.content}")
    print(f"Question: {response.next_question[:80]}...")
    
    # Répondre à chaque question jusqu'à PL
    questions_answers = [
        ("fever", "non"),
        ("meningeal_signs", "non"),
        ("htic_pattern", "non"),
    ]
    
    for field, answer in questions_answers:
        messages.append(ChatMessage(role="assistant", content=response.message))
        msg = ChatMessage(role="user", content=answer)
        messages.append(msg)
        response = handle_user_message(messages[:-1], msg, session_id=session_id)
        print(f"\nRéponse '{answer}' → {field}: {getattr(response.headache_case, field)}")
        if response.next_question:
            print(f"Question: {response.next_question[:80]}...")
    
    # Vérifier si on arrive à la question PL
    if response.next_question and "ponction lombaire" in response.next_question.lower():
        print("\n✅ Question sur ponction lombaire ATTEINTE après les red flags")
        
        # Répondre "oui" à la question PL
        messages.append(ChatMessage(role="assistant", content=response.message))
        msg = ChatMessage(role="user", content="oui")
        messages.append(msg)
        response = handle_user_message(messages[:-1], msg, session_id=session_id)
        
        print(f"\nRéponse 'oui' → recent_pl_or_peridural: {response.headache_case.recent_pl_or_peridural}")
        
        if response.headache_case.recent_pl_or_peridural is True:
            print("✅ Réponse 'oui' à PL CORRECTEMENT interprétée")
        else:
            print(f"❌ Réponse 'oui' à PL MAL interprétée: {response.headache_case.recent_pl_or_peridural}")
    else:
        print(f"\n❌ Question PL NON ATTEINTE. Question actuelle: {response.next_question}")
    
    reset_session(session_id)
    
    print("\n" + "=" * 80)
    print("TESTS TERMINÉS")
    print("=" * 80)


if __name__ == "__main__":
    test_pl_question()
