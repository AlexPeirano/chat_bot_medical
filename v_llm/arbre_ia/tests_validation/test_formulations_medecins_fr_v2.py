"""
Test de robustesse syntaxique étendu - Version 2
Cas cliniques variés avec formulations médicales françaises authentiques
Teste les acronymes, abréviations, synonymes et variations syntaxiques
"""

import json
from headache_assistants.nlu import parse_free_text_to_case
from headache_assistants.models import HeadacheCase

# Cas de test étendus avec formulations médicales françaises
CAS_MEDECINS_FRANCAIS_V2 = [
    # ========== MIGRAINES ==========
    {
        "nom": "Migraine 1 - Notation médicale condensée",
        "input": "F 28a, hémicrânie G battante depuis ce matin, EVA 8/10, N++, V++, photo+++, phono++. Couché dans le noir.",
        "attendu": {
            "headache_profile": "migraine_like",
            "intensity": 8,
            "profile": "acute"
        }
    },
    {
        "nom": "Migraine 2 - Avec aura typique",
        "input": "Homme 35a, scotome scintillant 20min puis CCH D pulsatile, EVA 9, N+V+, majoration effort. Durée 12h.",
        "attendu": {
            "headache_profile": "migraine_like",
            "intensity": 9,
            "duration_current_episode_hours": 12
        }
    },
    {
        "nom": "Migraine 3 - Crise sévère langage courant médecin",
        "input": "Patiente 42a, mal de tête atroce côté droit qui bat, supporte pas lumière ni bruit, vomit tout. EVA 10/10. Depuis hier soir.",
        "attendu": {
            "headache_profile": "migraine_like",
            "intensity": 10,
            "profile": "acute"
        }
    },
    {
        "nom": "Migraine 4 - Migraine compliquée déficit neuro",
        "input": "F 31a, CCH G avec hémiparésie D régressive, aphasie transitoire 30min, puis céphalée pulsatile intense EVA 8. Durée totale 4h.",
        "attendu": {
            "headache_profile": "migraine_like",
            "neuro_deficit": True,
            "intensity": 8,
            "duration_current_episode_hours": 4
        }
    },
    {
        "nom": "Migraine 5 - Abréviations multiples",
        "input": "M 29a, CCH unilatérale pulsatile, EVA 7, N+, intol lumière et bruit, aggrav mvt. ATCD migraineux fam+.",
        "attendu": {
            "headache_profile": "migraine_like",
            "intensity": 7
        }
    },
    
    # ========== CÉPHALÉES DE TENSION ==========
    {
        "nom": "CTT 1 - Notation avec Ø",
        "input": "Patiente 55a, céphalées bilat diffuses type serrement, EVA 3/10, Ø N, Ø V, Ø photo, Ø phono. Stress++.",
        "attendu": {
            "headache_profile": "tension_like",
            "intensity": 3
        }
    },
    {
        "nom": "CTT 2 - Description classique",
        "input": "H 48a, douleur en casque bilatérale non pulsatile, EVA 4/10, sans N/V ni photo/phono. Contractures cervicales importantes.",
        "attendu": {
            "headache_profile": "tension_like",
            "intensity": 4
        }
    },
    {
        "nom": "CTT 3 - Chronique quotidienne",
        "input": "Mme 52a, CCH quotidiennes depuis 6 mois, bilat en étau, EVA 3-4/10, aucun S associé. Anxiété chronique.",
        "attendu": {
            "headache_profile": "tension_like",
            "profile": "chronic",
            "intensity": 3
        }
    },
    {
        "nom": "CTT 4 - Abréviations multiples",
        "input": "F 45a, céph bilat diffuses occipito-front, non puls, EVA 5/10, Ø N/V/photo/phono. Contract trapèzes++.",
        "attendu": {
            "headache_profile": "tension_like",
            "intensity": 5
        }
    },
    {
        "nom": "CTT 5 - Avec déclencheurs",
        "input": "Patient 38a, céphalées bilatérales en étau depuis 2j, EVA 4/10, pas de signes associés. Contexte surmenage professionnel.",
        "attendu": {
            "headache_profile": "tension_like",
            "intensity": 4,
            "duration_current_episode_hours": 48
        }
    },
    
    # ========== ALGIES VASCULAIRES ==========
    {
        "nom": "AVF 1 - Crise typique",
        "input": "H 33a, douleur péri-orbitaire D atroce EVA 10/10, 45min, larmoie++, rhinorrhée D, injection conj. Agitation extrême.",
        "attendu": {
            "intensity": 10,
            "duration_current_episode_hours": 0.75
        }
    },
    {
        "nom": "AVF 2 - Période active",
        "input": "M 40a, crises quotid x3/j depuis 10j. Douleur orbitaire G insupportable 30-60min. Larmoiement, rhinorrhée homolatérale. Ptosis discret.",
        "attendu": {
            "intensity": 10,
            "profile": "subacute"
        }
    },
    {
        "nom": "AVF 3 - Notation condensée",
        "input": "Patient 36a, douleur rétro-orb D EVA max, 1h, larmes D, nez coule D, rougeur œil D, agité+++. Rythme circadien (nuit).",
        "attendu": {
            "intensity": 10,
            "duration_current_episode_hours": 1
        }
    },
    {
        "nom": "AVF 4 - Style urgences",
        "input": "H 29a, douleur orbitaire + temporo-frontale G strictement, début brutal, EVA 10, durée 50min. Larmoiement massif, rhinorrhée. Ne tient pas en place.",
        "attendu": {
            "intensity": 10,
            "duration_current_episode_hours": 0.83
        }
    },
    
    # ========== RED FLAGS / URGENCES ==========
    {
        "nom": "Red Flag 1 - Début thunderclap",
        "input": "Patiente 58a, céphalée brutale d'emblée maximale il y a 2h, pire douleur de sa vie, EVA 10/10, N+V+. Suspicion HSA.",
        "attendu": {
            "onset": "thunderclap",
            "intensity": 10,
            "profile": "acute"
        }
    },
    {
        "nom": "Red Flag 2 - Fièvre + signes méningés",
        "input": "H 25a, CCH intense depuis 6h, T°39.2, RDN+++, Kernig+, photophobie+++, vomissements. Tableau méningite.",
        "attendu": {
            "fever": True,
            "meningeal_signs": True,
            "profile": "acute"
        }
    },
    {
        "nom": "Red Flag 3 - Déficit neuro aigu",
        "input": "F 62a, céphalée depuis ce matin avec hémiparésie G, aphasie, EVA 6/10. Déficit persistant.",
        "attendu": {
            "neuro_deficit": True,
            "profile": "acute"
        }
    },
    {
        "nom": "Red Flag 4 - HTIC",
        "input": "Patient 45a, céphalées matutinales progressives depuis 3 sem, vomissements en jet, aggravation toux. Œdème papillaire au FO.",
        "attendu": {
            "htic_pattern": True,
            "profile": "subacute"
        }
    },
    {
        "nom": "Red Flag 5 - Post-traumatique",
        "input": "H 35a, céphalées persistantes depuis chute il y a 5j (TCC). Céphalée diffuse EVA 6/10, fluctuante.",
        "attendu": {
            "trauma": True,
            "profile": "acute",
            "intensity": 6
        }
    },
    {
        "nom": "Red Flag 6 - Nouveau >50ans",
        "input": "Mme 68a, première céphalée de sa vie depuis 2j, bilatérale EVA 7/10, sans S associés. Pas d'ATCD céphalées.",
        "attendu": {
            "profile": "acute",
            "intensity": 7
        }
    },
    
    # ========== CAS COMPLEXES / MIXTES ==========
    {
        "nom": "Complexe 1 - Migraine chronique transformée",
        "input": "F 40a, CCH chroniques quotid >1an. Fond douloureux permanent EVA 3 + crises 2x/sem unilatérales pulsatiles EVA 8 N+V+photo+phono+.",
        "attendu": {
            "profile": "chronic",
            "headache_profile": "migraine_like",
            "intensity": 8
        }
    },
    {
        "nom": "Complexe 2 - Céphalée post-PL",
        "input": "Patient 28a, PL il y a 3j pour bilan neuro. Depuis: céphalée intense position debout, amélioration décubitus. EVA 8/10.",
        "attendu": {
            "recent_pl_or_peridural": True,
            "intensity": 8,
            "profile": "acute"
        }
    },
    {
        "nom": "Complexe 3 - Grossesse",
        "input": "Patiente 32a enceinte (28 SA), céphalées depuis hier, bilat EVA 5/10, photo+. TA 165/95. Œdèmes MI.",
        "attendu": {
            "pregnancy_postpartum": True,
            "intensity": 5,
            "profile": "acute"
        }
    },
    {
        "nom": "Complexe 4 - Immunodépression",
        "input": "H 52a VIH+, CD4 <200. CCH progressive depuis 10j, EVA 6/10, fièvre 38.5°. Bilan infectieux en cours.",
        "attendu": {
            "immunosuppression": True,
            "fever": True,
            "profile": "subacute"
        }
    },
    {
        "nom": "Complexe 5 - Multiple red flags",
        "input": "F 58a, nouvelle céphalée brutale J-1, EVA 9/10, fièvre 38.8°, raideur nuque +, photophobie +++. Tableau suspect.",
        "attendu": {
            "onset": "thunderclap",
            "fever": True,
            "meningeal_signs": True,
            "intensity": 9
        }
    },
    
    # ========== VARIATIONS LINGUISTIQUES ==========
    {
        "nom": "Variation 1 - Style observation médicale",
        "input": "Observation: Patiente âgée de 37 ans consultant pour hémicrânie gauche pulsatile évoluant depuis 8 heures, intensité EVA 7/10, accompagnée de nausées, photophobie et phonophobie.",
        "attendu": {
            "headache_profile": "migraine_like",
            "intensity": 7,
            "duration_current_episode_hours": 8
        }
    },
    {
        "nom": "Variation 2 - Langage familier patient",
        "input": "Monsieur 45a dit avoir mal à la tête des deux côtés comme dans un étau, ça serre, pas trop fort (5/10), pas de nausées ni vomissements.",
        "attendu": {
            "headache_profile": "tension_like",
            "intensity": 5
        }
    },
    {
        "nom": "Variation 3 - Notes rapides urgences",
        "input": "H 40a, CCH brutale max d'emblée J0, 10/10, N+++V+++, suspicion HSA, scanner cérébral urgent.",
        "attendu": {
            "onset": "thunderclap",
            "intensity": 10,
            "profile": "acute"
        }
    },
    {
        "nom": "Variation 4 - Consultation classique",
        "input": "Femme de 50 ans se plaignant de céphalées quotidiennes depuis plusieurs mois, de type pression bilatérale, intensité modérée (4-5/10), sans signe d'accompagnement.",
        "attendu": {
            "headache_profile": "tension_like",
            "profile": "chronic",
            "intensity": 4
        }
    },
    {
        "nom": "Variation 5 - Abréviations extrêmes",
        "input": "M 33a, CCH unilatD puls EVA9 N+V+ photo+ phono+ dep 6h ATCD migr fam++",
        "attendu": {
            "headache_profile": "migraine_like",
            "intensity": 9,
            "duration_current_episode_hours": 6
        }
    }
]


def tester_formulations_v2():
    """
    Teste le système NLU avec un ensemble étendu de formulations médicales françaises.
    """
    print("=" * 80)
    print("TEST DE ROBUSTESSE ÉTENDU - FORMULATIONS MÉDICALES FRANÇAISES V2")
    print("=" * 80)
    print(f"Nombre de cas: {len(CAS_MEDECINS_FRANCAIS_V2)}")
    print()
    
    resultats = []
    reussites = 0
    echecs = 0
    
    # Statistiques par catégorie
    stats_categories = {
        "Migraine": {"total": 0, "reussite": 0},
        "CTT": {"total": 0, "reussite": 0},
        "AVF": {"total": 0, "reussite": 0},
        "Red Flag": {"total": 0, "reussite": 0},
        "Complexe": {"total": 0, "reussite": 0},
        "Variation": {"total": 0, "reussite": 0}
    }
    
    for i, cas in enumerate(CAS_MEDECINS_FRANCAIS_V2, 1):
        print(f"\n{'=' * 80}")
        print(f"CAS {i}/{len(CAS_MEDECINS_FRANCAIS_V2)}: {cas['nom']}")
        print(f"{'=' * 80}")
        print(f"\nINPUT MÉDICAL:")
        print(f"  {cas['input']}")
        print()
        
        # Déterminer la catégorie
        categorie = cas['nom'].split()[0]
        if categorie in stats_categories:
            stats_categories[categorie]["total"] += 1
        
        try:
            # Analyse NLU
            headache_case, metadata = parse_free_text_to_case(cas['input'])
            
            print(f"RÉSULTAT NLU:")
            print(f"  Profil temporel: {headache_case.profile}")
            print(f"  Type de début: {headache_case.onset}")
            print(f"  Profil céphalée: {headache_case.headache_profile}")
            print(f"  Intensité: {headache_case.intensity}")
            print(f"  Durée (heures): {headache_case.duration_current_episode_hours}")
            
            # Afficher les red flags détectés
            red_flags = []
            if headache_case.fever: red_flags.append("Fièvre")
            if headache_case.meningeal_signs: red_flags.append("Signes méningés")
            if headache_case.neuro_deficit: red_flags.append("Déficit neuro")
            if headache_case.htic_pattern: red_flags.append("HTIC")
            if headache_case.trauma: red_flags.append("Trauma")
            if headache_case.pregnancy_postpartum: red_flags.append("Grossesse/PP")
            if headache_case.recent_pl_or_peridural: red_flags.append("Post-PL")
            if headache_case.immunosuppression: red_flags.append("Immunodép")
            
            if red_flags:
                print(f"  Red flags: {', '.join(red_flags)}")
            
            # Vérifications basées sur les attributs disponibles
            validations = {}
            
            for cle, valeur_attendue in cas['attendu'].items():
                valeur_obtenue = getattr(headache_case, cle, None)
                
                if isinstance(valeur_attendue, bool):
                    validations[cle] = valeur_obtenue == valeur_attendue
                elif isinstance(valeur_attendue, (int, float)):
                    if valeur_obtenue is None:
                        validations[cle] = False
                    else:
                        # Tolérance pour les durées
                        if 'duration' in cle:
                            validations[cle] = abs(valeur_obtenue - valeur_attendue) < 1.5
                        else:
                            validations[cle] = abs(valeur_obtenue - valeur_attendue) <= 1
                else:
                    validations[cle] = valeur_obtenue == valeur_attendue
            
            # Statut global
            succes = all(validations.values()) if validations else False
            
            print(f"\n{'✓' if succes else '✗'} VALIDATION:")
            for cle, ok in validations.items():
                valeur_attendue = cas['attendu'][cle]
                valeur_obtenue = getattr(headache_case, cle, None)
                symbole = '✓' if ok else '✗'
                print(f"  {symbole} {cle}: attendu={valeur_attendue}, obtenu={valeur_obtenue}")
            
            if succes:
                reussites += 1
                if categorie in stats_categories:
                    stats_categories[categorie]["reussite"] += 1
            else:
                echecs += 1
            
            # Sauvegarde résultat
            resultats.append({
                "cas": cas['nom'],
                "input": cas['input'],
                "attendu": cas['attendu'],
                "resultat": {
                    "profile": headache_case.profile,
                    "onset": headache_case.onset,
                    "headache_profile": headache_case.headache_profile,
                    "intensity": headache_case.intensity,
                    "duration_current_episode_hours": headache_case.duration_current_episode_hours,
                    "fever": headache_case.fever,
                    "meningeal_signs": headache_case.meningeal_signs,
                    "neuro_deficit": headache_case.neuro_deficit,
                    "htic_pattern": headache_case.htic_pattern,
                    "trauma": headache_case.trauma,
                    "pregnancy_postpartum": headache_case.pregnancy_postpartum,
                    "immunosuppression": headache_case.immunosuppression
                },
                "succes": succes,
                "details_validation": validations
            })
            
        except Exception as e:
            print(f"\n✗ ERREUR: {str(e)}")
            import traceback
            traceback.print_exc()
            echecs += 1
            resultats.append({
                "cas": cas['nom'],
                "input": cas['input'],
                "attendu": cas['attendu'],
                "erreur": str(e),
                "succes": False
            })
    
    # Résumé final
    print(f"\n\n{'=' * 80}")
    print("RÉSUMÉ FINAL")
    print(f"{'=' * 80}")
    print(f"Total de cas testés: {len(CAS_MEDECINS_FRANCAIS_V2)}")
    print(f"✓ Réussites: {reussites} ({reussites/len(CAS_MEDECINS_FRANCAIS_V2)*100:.1f}%)")
    print(f"✗ Échecs: {echecs} ({echecs/len(CAS_MEDECINS_FRANCAIS_V2)*100:.1f}%)")
    
    print(f"\n{'=' * 80}")
    print("STATISTIQUES PAR CATÉGORIE")
    print(f"{'=' * 80}")
    for categorie, stats in stats_categories.items():
        if stats["total"] > 0:
            taux = (stats["reussite"] / stats["total"]) * 100
            print(f"{categorie:15} : {stats['reussite']:2}/{stats['total']:2} ({taux:5.1f}%)")
    
    # Sauvegarde JSON
    with open('test_formulations_medecins_v2_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "date_test": "2025-12-04",
            "version": "2.0",
            "description": "Test étendu de robustesse syntaxique avec formulations médicales françaises",
            "total_cas": len(CAS_MEDECINS_FRANCAIS_V2),
            "reussites": reussites,
            "echecs": echecs,
            "taux_reussite": round(reussites/len(CAS_MEDECINS_FRANCAIS_V2)*100, 2),
            "statistiques_categories": stats_categories,
            "resultats_detailles": resultats
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nRésultats détaillés sauvegardés dans: test_formulations_medecins_v2_results.json")
    
    return resultats


if __name__ == "__main__":
    tester_formulations_v2()
