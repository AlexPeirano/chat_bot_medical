"""Test du système de dialogue avec support embedding.

Vérifie que le dialogue utilise HybridNLU et détecte les patterns spéciaux
comme les névralgies du trijumeau via l'embedding.
"""

from headache_assistants.models import ChatMessage
from headache_assistants.dialogue import handle_user_message

def test_dialogue_with_nevralgie():
    """Test dialogue avec détection de névralgie du trijumeau via embedding."""

    print("=" * 80)
    print("TEST: Dialogue avec névralgie du trijumeau (détection via embedding)")
    print("=" * 80)

    # Message utilisateur avec névralgie du trijumeau
    user_message = ChatMessage(
        role="user",
        content="Patient de 55 ans avec douleur faciale comme une décharge électrique quand il parle"
    )

    print(f"\nMessage utilisateur: {user_message.content}")
    print("\n" + "-" * 80)

    # Traiter le message
    response = handle_user_message(
        history=[],
        new_message=user_message
    )

    print(f"\nRéponse du système:\n{response.message}")
    print("\n" + "-" * 80)

    # Vérifier les métadonnées
    print("\n📊 Métadonnées d'extraction:")
    print(f"  - Dialogue complet: {response.dialogue_complete}")
    print(f"  - Plus d'infos requises: {response.requires_more_info}")
    print(f"  - Score de confiance: {response.confidence_score:.2f}")

    if response.headache_case:
        print(f"\n📋 Cas extrait:")
        print(f"  - Âge: {response.headache_case.age}")
        print(f"  - Profil: {response.headache_case.profile}")
        print(f"  - Onset: {response.headache_case.onset}")

    if response.imaging_recommendation:
        print(f"\n🏥 Recommandation:")
        print(f"  - Imagerie: {response.imaging_recommendation.imaging}")
        print(f"  - Urgence: {response.imaging_recommendation.urgency}")
        print(f"  - Commentaire: {response.imaging_recommendation.comment[:100]}...")

    # Vérifier si patterns spéciaux détectés dans le message
    if "Diagnostic différentiel suggéré" in response.message:
        print("\n✅ SUCCESS: Patterns spéciaux détectés par embedding dans le message final!")
    else:
        print("\n⚠️  WARNING: Aucun pattern spécial détecté dans le message final")

    print("\n" + "=" * 80)
    return response


def test_dialogue_with_htic():
    """Test dialogue avec HTIC (règle classique, pas d'embedding nécessaire)."""

    print("\n\n" + "=" * 80)
    print("TEST: Dialogue avec HTIC (règle classique)")
    print("=" * 80)

    # Message utilisateur avec HTIC
    user_message = ChatMessage(
        role="user",
        content="Femme 45 ans, céphalées chroniques depuis 2 ans, vomissements en jet depuis 1 semaine"
    )

    print(f"\nMessage utilisateur: {user_message.content}")
    print("\n" + "-" * 80)

    # Traiter le message
    response = handle_user_message(
        history=[],
        new_message=user_message
    )

    print(f"\nRéponse du système:\n{response.message}")
    print("\n" + "-" * 80)

    print("\n📊 Métadonnées:")
    print(f"  - Dialogue complet: {response.dialogue_complete}")
    print(f"  - Plus d'infos requises: {response.requires_more_info}")

    if response.headache_case:
        print(f"\n📋 Cas extrait:")
        print(f"  - HTIC pattern: {response.headache_case.htic_pattern}")
        print(f"  - Recent pattern change: {response.headache_case.recent_pattern_change}")

    print("\n" + "=" * 80)
    return response


if __name__ == "__main__":
    # Test 1: Névralgie (embedding)
    response1 = test_dialogue_with_nevralgie()

    # Test 2: HTIC (règles)
    response2 = test_dialogue_with_htic()

    print("\n\n🎯 RÉSUMÉ DES TESTS:")
    print(f"  - Test névralgie (embedding): {'✅ PASS' if 'Diagnostic différentiel' in response1.message else '❌ FAIL'}")
    print(f"  - Test HTIC (règles): {'✅ PASS' if response2.headache_case and response2.headache_case.htic_pattern else '❌ FAIL'}")
