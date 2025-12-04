"""
Test avec cas patients réalistes - Formulations et acronymes médicaux français
================================================================================

Ce fichier teste le système avec des formulations réelles utilisées par les 
médecins français, incluant tous les acronymes et abréviations courantes.
"""

from headache_assistants.models import ChatMessage
from headache_assistants.dialogue import handle_user_message
import json


# =============================================================================
# CAS PATIENTS AVEC FORMULATIONS MÉDICALES RÉELLES
# =============================================================================

CAS_PATIENTS = [
    {
        "id": "P001_HSA_suspicion",
        "description": "HSA suspectée - Coup de tonnerre",
        "messages": [
            "H 52a, céph brutale type coup de tonnerre dep 2h, EVA 10/10, vom +, photophobie",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["scanner_cerebral_sans_injection"],  # PL en complément acceptable
    },
    {
        "id": "P002_meningite",
        "description": "Méningite bactérienne",
        "messages": [
            "F 28a, céph intense + T 39.5 + RDN ++, Kernig +, Brudzinski pos, confusion",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["ponction_lombaire"],
    },
    {
        "id": "P003_htic_aigue",
        "description": "HTIC aiguë sur processus expansif",
        "messages": [
            "Pt 65a, céph progressive dep 3 sem, pire le matin, vom en jet, OP ++, hémipar D",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["scanner_cerebral_sans_injection", "irm_cerebrale"],
    },
    {
        "id": "P004_tvc_postpartum",
        "description": "TVC post-partum",
        "messages": [
            "F 32a, J8 post-partum, céph intense progressive dep 2j, déficit MSD, CGT ce matin",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["irm_cerebrale"],  # angio-IRM veineuse en complément acceptable
    },
    {
        "id": "P005_tcc_recent",
        "description": "TCC avec hématome sous-dural",
        "messages": [
            "H 78a, AVP J-3, TCC avec PDC, céph croissante, confusion, GCS 14",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["scanner_cerebral_sans_injection"],
    },
    {
        "id": "P006_abces_cerebral",
        "description": "Abcès cérébral sur immunodépression",
        "messages": [
            "H 45a, VIH+ CD4 80, céph + T 38.8, confusion, déficit MSG, sd méningé",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["scanner_cerebral_avec_injection", "irm_cerebrale"],
    },
    {
        "id": "P007_migraine_aura",
        "description": "Migraine avec aura typique",
        "messages": [
            "F 35a, céph unilatérale G pulsatile dep ce matin, scotomes 20min avant, nausées, photophobie, EVA 7, ATCD migraine",
        ],
        "urgence_attendue": "none",
        "examens_attendus": [],
    },
    {
        "id": "P008_tension_stress",
        "description": "Céphalée de tension",
        "messages": [
            "Pt 42a, céph en étau frontale bilat dep 3j, intensité modérée 4/10, pas de vom, pas de photophobie",
        ],
        "urgence_attendue": "none",
        "examens_attendus": [],
    },
    {
        "id": "P009_chronique_sans_alarme",
        "description": "Céphalée chronique quotidienne sans signe d'alarme",
        "messages": [
            "F 50a, céph chronique dep 2 ans, tous les jours, intensité variable 3-6/10, apyr, RDN -, sans déficit, examen neuro normal",
        ],
        "urgence_attendue": "none",
        "examens_attendus": [],
    },
    {
        "id": "P010_sinusite_aigue",
        "description": "Céphalée sur sinusite maxillaire",
        "messages": [
            "H 38a, céph frontale + douleur sinusienne, rhinorrhée purulente, T 38.2, aggravée tête penchée",
        ],
        "urgence_attendue": "none",
        "examens_attendus": [],
    },
    {
        "id": "P011_hsa_atypique",
        "description": "HSA avec présentation atypique",
        "messages": [
            "F 60a, céph brutale hier soir, actuellement EVA 6, raideur nuque discrète, sans déficit",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["scanner_cerebral_sans_injection"],
    },
    {
        "id": "P012_tvc_grossesse",
        "description": "TVC sur grossesse T3",
        "messages": [
            "F 29a, G1P0 36SA, céph progressive dep 5j, EVA 8, vom, vision floue, sans sg méningés",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["irm_cerebrale"],  # angio-IRM veineuse en complément acceptable
    },
    {
        "id": "P013_dissection_vertebrale",
        "description": "Dissection vertébrale post-traumatique",
        "messages": [
            "H 45a, choc cervical pendant sport J-2, céph occipitale + cervicalgie, acouphène pulsatile, vertiges",
        ],
        "urgence_attendue": "urgent",
        "examens_attendus": ["angio_irm"],
    },
    {
        "id": "P014_tumor_cerebral",
        "description": "Tumeur cérébrale évolutive",
        "messages": [
            "Pt 58a, K poumon traité chimio, céph progressive dep 6 sem, pire matin, vom, troubles mnésiques",
        ],
        "urgence_attendue": "urgent",
        "examens_attendus": ["irm_cerebrale"],
    },
    {
        "id": "P015_algie_vasculaire",
        "description": "Algie vasculaire de la face",
        "messages": [
            "H 40a, douleur périorbitaire G sévère 10/10, larmoiement, rhinorrhée, durée 45min, crises nocturnes répétées",
        ],
        "urgence_attendue": "delayed",
        "examens_attendus": [],
    },
    {
        "id": "P016_hypertension_maligne",
        "description": "Céphalée sur HTA maligne",
        "messages": [
            "F 55a, céph intense + TA 220/120, flou visuel, nausées, pas ATCD HTA",
        ],
        "urgence_attendue": "immediate",
        "examens_attendus": ["scanner_cerebral_sans_injection"],
    },
    {
        "id": "P017_meningite_virale",
        "description": "Méningite virale probable",
        "messages": [
            "H 25a, céph + T 38.3 + RDN +, photophobie, contexte épidémique entérovirus, pas de confusion",
        ],
        "urgence_attendue": "urgent",
        "examens_attendus": ["ponction_lombaire"],
    },
    {
        "id": "P018_migraine_compliquee",
        "description": "Migraine compliquée avec aura prolongée",
        "messages": [
            "F 32a, céph hémicrânienne D, aura visuelle persistante > 1h, hémipar G transitoire, ATCD migraine",
        ],
        "urgence_attendue": "urgent",
        "examens_attendus": ["irm_cerebrale"],
    },
    {
        "id": "P019_post_pl",
        "description": "Céphalée post-ponction lombaire",
        "messages": [
            "Pt 40a, PL il y a 2j pour bilan sclérose en plaques, céph intense orthostatique, pire debout, amélioration décubitus",
        ],
        "urgence_attendue": "delayed",
        "examens_attendus": [],
    },
    {
        "id": "P020_hematome_sous_arachno",
        "description": "Hématome sous-arachnoïdien chronique",
        "messages": [
            "H 82a, sous AVK, chute J-15, céph progressive, confusion fluctuante, marche instable",
        ],
        "urgence_attendue": "urgent",
        "examens_attendus": ["scanner_cerebral_sans_injection"],
    },
]


def executer_test_patient(cas_patient: dict, verbose: bool = True) -> dict:
    """
    Exécute un test complet pour un cas patient.
    
    Args:
        cas_patient: Dictionnaire avec description du cas
        verbose: Afficher les détails
        
    Returns:
        Résultats du test
    """
    messages = []
    session_id = None
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"TEST: {cas_patient['id']}")
        print(f"Description: {cas_patient['description']}")
        print(f"{'='*80}")
    
    # Envoyer tous les messages du cas
    for i, texte in enumerate(cas_patient['messages']):
        if verbose:
            print(f"\nMédecin: {texte}")
        
        msg = ChatMessage(role="user", content=texte)
        messages.append(msg)
        response = handle_user_message(messages[:-1], msg, session_id=session_id)
        session_id = response.session_id
        
        if verbose and not response.dialogue_complete:
            print(f"Assistant: {response.next_question}")
    
    # Répondre automatiquement aux questions manquantes avec des valeurs par défaut
    max_tours = 15
    tour = len(cas_patient['messages'])
    
    while not response.dialogue_complete and tour < max_tours:
        # Réponses automatiques selon le champ demandé
        auto_response = "non"  # Par défaut: non pour tous les red flags
        
        # Identifier la question posée
        question = response.next_question.lower() if response.next_question else ""
        
        if "intensité" in question or "échelle" in question:
            auto_response = "5"
        elif "début" in question or "commencé" in question:
            if "brutal" in question:
                auto_response = "non, progressivement"
        
        if verbose:
            print(f"\nAuto-réponse: {auto_response}")
        
        msg = ChatMessage(role="user", content=auto_response)
        messages.append(msg)
        response = handle_user_message(messages[:-1], msg, session_id=session_id)
        
        if verbose and not response.dialogue_complete:
            print(f"Assistant: {response.next_question}")
        
        tour += 1
    
    # Analyser les résultats
    if response.dialogue_complete and response.imaging_recommendation:
        rec = response.imaging_recommendation
        
        # Vérifier l'urgence
        urgence_ok = rec.urgency == cas_patient['urgence_attendue']
        
        # Vérifier les examens - LOGIQUE ASSOUPLIE:
        # ✅ Accepter si tous les examens attendus sont présents
        # ✅ Accepter examens supplémentaires médicalement justifiés
        # Exemples:
        # - HSA: scanner seul OK, scanner+PL OK (protocole complet)
        # - TVC: IRM seule OK, IRM+angio-IRM veineuse OK (bilan complet)
        examens_attendus_set = set(cas_patient['examens_attendus'])
        examens_obtenus_set = set(rec.imaging)
        
        if len(examens_attendus_set) == 0:
            # Pas d'examen attendu
            examens_ok = len(examens_obtenus_set) == 0
        else:
            # Tous les examens attendus doivent être présents
            # (peut y avoir des examens supplémentaires)
            examens_ok = examens_attendus_set.issubset(examens_obtenus_set)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"RÉSULTATS:")
            print(f"  Urgence obtenue: {rec.urgency} {'✅' if urgence_ok else '❌ (attendu: ' + cas_patient['urgence_attendue'] + ')'}")
            print(f"  Examens obtenus: {rec.imaging}")
            print(f"  Examens attendus: {cas_patient['examens_attendus']}")
            
            # Afficher examens supplémentaires si présents
            examens_supplementaires = examens_obtenus_set - examens_attendus_set
            if examens_supplementaires and len(cas_patient['examens_attendus']) > 0:
                print(f"  Examens supplémentaires (justifiés): {list(examens_supplementaires)}")
            
            print(f"  Examens OK: {'✅' if examens_ok else '❌'}")
            print(f"  Commentaire: {rec.comment[:150]}...")
            print(f"{'='*80}")
        
        return {
            "id": cas_patient['id'],
            "succes": urgence_ok and examens_ok,
            "urgence_ok": urgence_ok,
            "examens_ok": examens_ok,
            "urgence_obtenue": rec.urgency,
            "urgence_attendue": cas_patient['urgence_attendue'],
            "examens_obtenus": rec.imaging,
            "examens_attendus": cas_patient['examens_attendus'],
            "tours": tour,
        }
    else:
        if verbose:
            print(f"\n❌ ÉCHEC: Dialogue non terminé après {tour} tours")
        
        return {
            "id": cas_patient['id'],
            "succes": False,
            "erreur": "Dialogue non terminé",
            "tours": tour,
        }


def executer_tous_les_tests(verbose: bool = True, sauvegarder: bool = True):
    """
    Exécute tous les tests de cas patients.
    
    Args:
        verbose: Afficher les détails
        sauvegarder: Sauvegarder les résultats en JSON
        
    Returns:
        Liste des résultats
    """
    resultats = []
    
    print("\n" + "="*80)
    print("TESTS CAS PATIENTS RÉELS - FORMULATIONS MÉDICALES FRANÇAISES")
    print("="*80)
    
    for cas in CAS_PATIENTS:
        resultat = executer_test_patient(cas, verbose=verbose)
        resultats.append(resultat)
    
    # Statistiques globales
    total = len(resultats)
    succes = sum(1 for r in resultats if r.get('succes', False))
    urgence_ok = sum(1 for r in resultats if r.get('urgence_ok', False))
    examens_ok = sum(1 for r in resultats if r.get('examens_ok', False))
    
    print("\n" + "="*80)
    print("STATISTIQUES GLOBALES")
    print("="*80)
    print(f"Total de cas testés: {total}")
    print(f"Succès complets: {succes}/{total} ({100*succes/total:.1f}%)")
    print(f"Urgence correcte: {urgence_ok}/{total} ({100*urgence_ok/total:.1f}%)")
    print(f"Examens corrects: {examens_ok}/{total} ({100*examens_ok/total:.1f}%)")
    print("="*80)
    
    # Détail des échecs
    echecs = [r for r in resultats if not r.get('succes', False)]
    if echecs:
        print("\nDÉTAIL DES ÉCHECS:")
        for echec in echecs:
            print(f"\n  {echec['id']}:")
            if 'erreur' in echec:
                print(f"    Erreur: {echec['erreur']}")
            else:
                if not echec.get('urgence_ok', False):
                    print(f"    ❌ Urgence: {echec['urgence_obtenue']} au lieu de {echec['urgence_attendue']}")
                if not echec.get('examens_ok', False):
                    print(f"    ❌ Examens: {echec['examens_obtenus']} au lieu de {echec['examens_attendus']}")
    
    # Sauvegarder les résultats
    if sauvegarder:
        with open('test_cas_patients_resultats.json', 'w', encoding='utf-8') as f:
            json.dump(resultats, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Résultats sauvegardés dans: test_cas_patients_resultats.json")
    
    return resultats


if __name__ == "__main__":
    import sys
    
    # Si argument: tester un seul cas
    if len(sys.argv) > 1:
        cas_id = sys.argv[1]
        cas = next((c for c in CAS_PATIENTS if c['id'] == cas_id), None)
        if cas:
            executer_test_patient(cas, verbose=True)
        else:
            print(f"❌ Cas '{cas_id}' introuvable")
            print("\nCas disponibles:")
            for c in CAS_PATIENTS:
                print(f"  - {c['id']}: {c['description']}")
    else:
        # Tester tous les cas
        executer_tous_les_tests(verbose=True, sauvegarder=True)
