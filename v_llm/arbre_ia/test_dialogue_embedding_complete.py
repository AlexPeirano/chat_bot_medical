"""Test du système de dialogue COMPLET avec support embedding.

Simule une conversation complète pour voir les patterns spéciaux détectés
dans le message final.
"""

from headache_assistants.models import ChatMessage
from headache_assistants.dialogue import handle_user_message

def simulate_complete_dialogue_nevralgie():
    """Simule un dialogue complet avec névralgie du trijumeau."""

    print("=" * 80)
    print("TEST: Dialogue COMPLET avec névralgie du trijumeau")
    print("=" * 80)

    session_id = None
    history = []

    # Tour 1: Message initial
    msg1 = ChatMessage(
        role="user",
        content="Patient de 55 ans avec douleur faciale comme une décharge électrique quand il parle"
    )
    print(f"\n[USER 1]: {msg1.content}")
    response1 = handle_user_message(history, msg1, session_id)
    session_id = response1.session_id
    history.append(msg1)
    history.append(ChatMessage(role="assistant", content=response1.message))
    print(f"[ASSISTANT 1]: {response1.message[:150]}...")
    print(f"  → Dialogue complet: {response1.dialogue_complete}")

    # Tour 2: Répondre à la question sur le début
    msg2 = ChatMessage(
        role="user",
        content="C'est chronique, il a cette douleur depuis plusieurs mois"
    )
    print(f"\n[USER 2]: {msg2.content}")
    response2 = handle_user_message(history, msg2, session_id)
    history.append(msg2)
    history.append(ChatMessage(role="assistant", content=response2.message))
    print(f"[ASSISTANT 2]: {response2.message[:150]}...")
    print(f"  → Dialogue complet: {response2.dialogue_complete}")

    # Tour 3: Répondre à la question sur l'intensité
    if not response2.dialogue_complete and response2.next_question:
        msg3 = ChatMessage(
            role="user",
            content="L'intensité est de 8/10"
        )
        print(f"\n[USER 3]: {msg3.content}")
        response3 = handle_user_message(history, msg3, session_id)
        history.append(msg3)
        history.append(ChatMessage(role="assistant", content=response3.message))
        print(f"[ASSISTANT 3]: {response3.message[:150]}...")
        print(f"  → Dialogue complet: {response3.dialogue_complete}")

        # Tour 4: Répondre à la question sur la fièvre
        if not response3.dialogue_complete and response3.next_question:
            msg4 = ChatMessage(
                role="user",
                content="Non, pas de fièvre"
            )
            print(f"\n[USER 4]: {msg4.content}")
            response4 = handle_user_message(history, msg4, session_id)
            history.append(msg4)
            history.append(ChatMessage(role="assistant", content=response4.message))
            print(f"[ASSISTANT 4]: {response4.message[:150]}...")
            print(f"  → Dialogue complet: {response4.dialogue_complete}")

            # Tour 5: Continuer jusqu'à ce que le dialogue soit complet
            current_response = response4
            turn = 5
            while not current_response.dialogue_complete and turn <= 10:
                # Répondre "non" à toutes les questions oui/non
                msg = ChatMessage(role="user", content="Non")
                print(f"\n[USER {turn}]: {msg.content}")
                current_response = handle_user_message(history, msg, session_id)
                history.append(msg)
                history.append(ChatMessage(role="assistant", content=current_response.message))
                print(f"[ASSISTANT {turn}]: {current_response.message[:150]}...")
                print(f"  → Dialogue complet: {current_response.dialogue_complete}")
                turn += 1

            # Message final
            if current_response.dialogue_complete:
                print("\n" + "=" * 80)
                print("MESSAGE FINAL DU SYSTÈME:")
                print("=" * 80)
                print(current_response.message)
                print("=" * 80)

                # Vérifier si patterns spéciaux détectés
                if "Diagnostic différentiel suggéré" in current_response.message:
                    print("\n✅ SUCCESS: Patterns spéciaux détectés par embedding!")
                    print("   → La névralgie du trijumeau a été détectée via l'embedding")
                    return True
                else:
                    print("\n⚠️  WARNING: Aucun pattern spécial dans le message final")
                    print("   → L'embedding n'a pas détecté de pattern spécial")
                    return False
            else:
                print("\n⚠️  Dialogue non terminé après 10 tours")
                return False


if __name__ == "__main__":
    success = simulate_complete_dialogue_nevralgie()

    print("\n\n🎯 RÉSULTAT:")
    if success:
        print("✅ L'embedding est correctement utilisé dans le dialogue")
    else:
        print("❌ L'embedding ne semble pas être utilisé ou les patterns ne sont pas détectés")
