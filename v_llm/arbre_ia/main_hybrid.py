"""Point d'entrée principal pour le système de dialogue médical interactif."""

from headache_assistants.nlu_hybrid import HybridNLU
from headache_assistants.models import HeadacheCase


def print_separator(char="=", length=70):
    """Affiche une ligne de séparation."""
    print(char * length)


def interactive_mode(nlu: HybridNLU):
    """Mode interactif avec dialogue (pose des questions si infos manquantes)."""
    from headache_assistants.dialogue import handle_user_message
    from headache_assistants.models import ChatMessage
    from headache_assistants.prescription import generate_prescription

    print("\n" + "="*70)
    print("ASSISTANT MEDICAL - EVALUATION DES CEPHALEES (NLU HYBRIDE)")
    print("="*70)
    print("\nBonjour Docteur,")
    print("Decrivez le cas clinique de votre patient.")
    print("Le systeme pose des questions pour determiner les examens necessaires.")
    print("\nATTENTION : Outil d'aide a la decision uniquement.")
    print("="*70)
    print("\nCommandes disponibles:")
    print("  /aide        - Afficher cette aide")
    print("  /ordonnance  - Generer une ordonnance (apres evaluation)")
    print("  /reset       - Commencer un nouveau cas")
    print("  /quit        - Quitter le programme")
    print("="*70 + "\n")

    history = []
    session_id = None
    last_case = None
    last_recommendation = None

    while True:
        user_input = input("Vous: ").strip()

        if not user_input:
            continue

        # Gestion des commandes
        if user_input.lower() in ['/quit', '/exit', '/q']:
            print("\nAssistant: Au revoir Docteur.\n")
            break

        if user_input.lower() in ['/aide', '/help', '/h']:
            print("\nCommandes disponibles:")
            print("  /aide        - Afficher cette aide")
            print("  /ordonnance  - Generer une ordonnance (apres evaluation)")
            print("  /reset       - Commencer un nouveau cas")
            print("  /quit        - Quitter le programme\n")
            continue

        if user_input.lower() in ['/ordonnance', '/ord']:
            if last_case and last_recommendation:
                try:
                    doctor_name = input("Nom du prescripteur (ou Entree pour 'Dr. [NOM]'): ").strip()
                    if not doctor_name:
                        doctor_name = "Dr. [NOM]"

                    filepath = generate_prescription(last_case, last_recommendation, doctor_name)
                    print(f"\nOrdonnance generee: {filepath}\n")
                except Exception as e:
                    print(f"\nErreur lors de la generation: {e}\n")
            else:
                print("\nAucune evaluation en cours. Veuillez d'abord evaluer un cas.\n")
            continue

        if user_input.lower() == '/reset':
            print("\nAssistant: Nouveau cas. Decrivez le cas clinique de votre patient.\n")
            history = []
            session_id = None
            last_case = None
            last_recommendation = None
            continue

        # Créer message utilisateur
        user_message = ChatMessage(role="user", content=user_input)
        history.append(user_message)

        # Traiter avec le système de dialogue
        response = handle_user_message(history, user_message, session_id)

        # Sauvegarder session_id
        if not session_id:
            session_id = response.session_id

        # Ajouter réponse à l'historique
        assistant_message = ChatMessage(role="assistant", content=response.message)
        history.append(assistant_message)

        # Afficher réponse
        if response.dialogue_complete:
            print(f"\nAssistant: {response.message}\n")
        elif response.next_question:
            print(f"\nAssistant: {response.next_question}\n")
        else:
            print(f"\nAssistant: {response.message}\n")

        # Sauvegarder résultats pour ordonnance
        if response.imaging_recommendation:
            last_recommendation = response.imaging_recommendation
        if response.headache_case:
            last_case = response.headache_case

        # Afficher résumé final si dialogue terminé
        if response.dialogue_complete and last_recommendation and last_case:
            print_case_summary(last_case)

            urgency_display = {
                "immediate": "IMMEDIATE",
                "urgent": "URGENTE",
                "delayed": "PROGRAMMEE",
                "none": "AUCUNE"
            }

            print("\n" + "-"*70)
            print("RESUME")
            print("-"*70)
            print(f"Urgence: {urgency_display.get(last_recommendation.urgency, 'INCONNUE')}")
            if last_recommendation.imaging:
                print("Examens recommandes:")
                for exam in last_recommendation.imaging:
                    print(f"  - {exam}")
            print("-"*70)
            print("\n")

            # Afficher les options après le résumé
            print("Options: [O]rdonnance, [N]ouveau cas, [Q]uitter")
            choix = input("Vous: ").strip().lower()

            if choix in ['o', 'ordonnance']:
                doctor_name = input("Nom du prescripteur (ou Entree pour 'Dr. [NOM]'): ").strip()
                if not doctor_name:
                    doctor_name = "Dr. [NOM]"
                try:
                    filepath = generate_prescription(last_case, last_recommendation, doctor_name)
                    print(f"\nOrdonnance generee: {filepath}\n")
                except Exception as e:
                    print(f"\nErreur lors de la generation: {e}\n")

            if choix in ['n', 'nouveau', 'nouveau cas']:
                print("\nAssistant: Nouveau cas. Decrivez le cas clinique de votre patient.\n")
                history = []
                session_id = None
                last_case = None
                last_recommendation = None

            if choix in ['quitter', 'q', '/quit']:
                print("\nAssistant: Au revoir Docteur.\n")
                break

        # Note: Progression du cas supprimée pour simplifier l'output


def print_case_summary(case: HeadacheCase):
    """Affiche un résumé du cas sans émojis."""
    print("\nCAS CLINIQUE:")
    print("-"*70)

    # Informations temporelles
    if case.onset and case.onset != "unknown":
        print(f"Debut (Onset): {case.onset}")
    if case.profile and case.profile != "unknown":
        print(f"Profil temporel: {case.profile}")

    # Red Flags détectés
    print(f"\nRED FLAGS DETECTES:")
    red_flags = []

    if case.onset == "thunderclap":
        red_flags.append("Debut brutal (thunderclap)")
    if case.fever is True:
        red_flags.append("Fievre")
    if case.meningeal_signs is True:
        red_flags.append("Syndrome meninge")
    if case.htic_pattern is True:
        red_flags.append("Signes HTIC")
    if case.neuro_deficit is True:
        red_flags.append("Deficit neurologique")
    if case.trauma is True:
        red_flags.append("Traumatisme cranien")
    if case.seizure is True:
        red_flags.append("Crises/Convulsions")
    if case.pregnancy_postpartum is True:
        red_flags.append("Grossesse/Post-partum")
    if case.immunosuppression is True:
        red_flags.append("Immunodepression")
    if case.cancer_history is True:
        red_flags.append("Antecedent oncologique")

    if red_flags:
        for flag in red_flags:
            print(f"  - {flag}")
    else:
        print("  Aucun red flag detecte")

    print("-"*70)


def main():
    """Point d'entrée principal."""
    # Initialisation silencieuse
    nlu = HybridNLU(confidence_threshold=0.7, verbose=False)

    # Lancer le mode interactif
    interactive_mode(nlu)


if __name__ == "__main__":
    main()
