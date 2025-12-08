"""Debug du système de dialogue pour voir les métadonnées d'embedding."""

from headache_assistants.models import ChatMessage
from headache_assistants.dialogue import handle_user_message, get_session_info

def debug_dialogue_metadata():
    """Debug pour voir où sont stockés les special_patterns."""

    print("=" * 80)
    print("DEBUG: Métadonnées du dialogue")
    print("=" * 80)

    session_id = None
    history = []

    # Tour 1: Message initial avec névralgie
    msg1 = ChatMessage(
        role="user",
        content="Patient de 55 ans avec douleur faciale comme une décharge électrique quand il parle"
    )
    print(f"\n[USER 1]: {msg1.content}")
    response1 = handle_user_message(history, msg1, session_id)
    session_id = response1.session_id

    # Récupérer les infos de session
    session_info = get_session_info(session_id)
    print(f"\n📊 Session metadata après message 1:")
    print(f"  - extraction_metadata keys: {session_info['extraction_metadata'].keys()}")

    # Vérifier enhancement_details
    enhancement = session_info['extraction_metadata'].get('enhancement_details', {})
    print(f"  - enhancement_details keys: {enhancement.keys()}")

    # Vérifier special_patterns
    special_patterns = enhancement.get('special_patterns_detected', [])
    print(f"  - special_patterns_detected: {len(special_patterns)} patterns")

    if special_patterns:
        print("\n✅ Patterns détectés après le premier message:")
        for i, pattern in enumerate(special_patterns):
            print(f"\n  Pattern {i+1}:")
            print(f"    - type: {pattern.get('type')}")
            print(f"    - description: {pattern.get('description')}")
            print(f"    - similarity: {pattern.get('similarity', 0):.3f}")
            print(f"    - imaging: {pattern.get('imaging_recommendation')}")
            print(f"    - matched_text: {pattern.get('matched_text')}")
    else:
        print("\n⚠️  Aucun pattern détecté après le premier message")

    # Tour 2: Continuer le dialogue
    history.append(msg1)
    history.append(ChatMessage(role="assistant", content=response1.message))

    msg2 = ChatMessage(role="user", content="C'est chronique")
    print(f"\n\n[USER 2]: {msg2.content}")
    response2 = handle_user_message(history, msg2, session_id)

    # Vérifier metadata après message 2
    session_info = get_session_info(session_id)
    print(f"\n📊 Session metadata après message 2:")
    enhancement2 = session_info['extraction_metadata'].get('enhancement_details', {})
    special_patterns2 = enhancement2.get('special_patterns_detected', [])
    print(f"  - special_patterns_detected (extraction_metadata): {len(special_patterns2)} patterns")

    # Vérifier accumulated_special_patterns
    accumulated = session_info.get('accumulated_special_patterns', [])
    print(f"  - accumulated_special_patterns (session): {len(accumulated)} patterns")

    if len(accumulated) > 0:
        print("  ✅ Les patterns sont PRÉSERVÉS dans accumulated_special_patterns")
    else:
        print("  ⚠️  Les patterns n'ont pas été préservés")

    return special_patterns, accumulated


if __name__ == "__main__":
    patterns1, patterns2 = debug_dialogue_metadata()

    print("\n\n🎯 DIAGNOSTIC:")
    if len(patterns1) > 0 and len(patterns2) > 0:
        print("✅ OK: Les patterns sont détectés et préservés dans accumulated_special_patterns")
        print(f"   → {len(patterns2)} pattern(s) préservé(s) durant toute la session")
    elif len(patterns1) > 0 and len(patterns2) == 0:
        print("❌ PROBLÈME: Les patterns sont détectés mais ne sont pas accumulés")
    else:
        print("⚠️  Les patterns ne sont pas détectés du tout")
