#!/usr/bin/env python3
"""
Test de robustesse avec TERMINOLOGIE MÉDICALE FRANÇAISE.

Tests avec synonymes, acronymes et abréviations utilisés par médecins français
pour valider la robustesse du système NLU face au langage médical réel.
"""

import sys
import json
from typing import Dict, Any, List

# Force reload des modules pour éviter le cache
for module in list(sys.modules.keys()):
    if module.startswith('headache_assistants'):
        del sys.modules[module]

from headache_assistants.models import HeadacheCase
from headache_assistants.nlu import parse_free_text_to_case
from headache_assistants.rules_engine import decide_imaging


class MedicalTerminologyTester:
    """Teste le système avec terminologie médicale française réelle."""
    
    def __init__(self):
        self.tests = [
            # === HSA - HÉMORRAGIE SOUS-ARACHNOÏDIENNE ===
            {
                "category": "HSA - Acronymes",
                "text": "F 52a, HSA suspectée, début brutal",
                "expected": {
                    "onset": "thunderclap",
                    "urgency": "immediate"
                }
            },
            {
                "category": "HSA - Coup de tonnerre",
                "text": "Pt 45 ans, céph coup de tonnerre, 10/10",
                "expected": {
                    "onset": "thunderclap",
                    "intensity": 10,
                    "urgency": "immediate"
                }
            },
            {
                "category": "HSA - Ictus",
                "text": "Homme 50a, ictus céphalalgique brutal",
                "expected": {
                    "onset": "thunderclap",
                    "urgency": "immediate"
                }
            },
            {
                "category": "HSA - Installation brutale",
                "text": "Patiente 48 ans, céphalée d'installation brutale",
                "expected": {
                    "onset": "thunderclap",
                    "urgency": "immediate"
                }
            },
            {
                "category": "HSA - Début soudain",
                "text": "H 55a, céph début soudain maximale d'emblée",
                "expected": {
                    "onset": "thunderclap",
                    "urgency": "immediate"
                }
            },
            {
                "category": "HSA - Pire céphalée",
                "text": "F 42 ans, pire céphalée de sa vie",
                "expected": {
                    "intensity": 10,
                    "urgency": "immediate"
                }
            },
            
            # === MÉNINGITE - SIGNES MÉNINGÉS ===
            {
                "category": "Méningite - Sdm méningé",
                "text": "Pt 28a, T° 39°C, sdm méningé +",
                "expected": {
                    "fever": True,
                    "meningeal_signs": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Méningite - Kernig",
                "text": "Homme 25 ans, fébrile, Kernig positif",
                "expected": {
                    "fever": True,
                    "meningeal_signs": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Méningite - Brudzinski",
                "text": "F 30a, fièvre 38.5, Brudzinski +",
                "expected": {
                    "fever": True,
                    "meningeal_signs": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Méningite - RDN",
                "text": "Pt 35 ans, T° 39.2, RDN importante",
                "expected": {
                    "fever": True,
                    "meningeal_signs": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Méningite - Hyperthermie",
                "text": "H 22a, hyperthermie 39.5, raideur nuque",
                "expected": {
                    "fever": True,
                    "meningeal_signs": True,
                    "urgency": "immediate"
                }
            },
            
            # === DÉFICIT NEUROLOGIQUE ===
            {
                "category": "Neuro - Hémiparésie",
                "text": "Patiente 60 ans, céph + hémiparésie D",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Neuro - Déficit sensitivomoteur",
                "text": "H 58a, céph, DSM membre sup G",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Neuro - Aphasie",
                "text": "F 65 ans, céphalée, trouble du langage type aphasie",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Neuro - Paralysie faciale",
                "text": "Pt 52a, céph + PF centrale droite",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Neuro - Diplopie",
                "text": "Homme 45 ans, céphalée, diplopie binoculaire",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Neuro - Trouble vigilance",
                "text": "F 70a, céph, altération conscience, Glasgow 13",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            
            # === CONVULSIONS ===
            {
                "category": "Convulsions - Crise comitiale",
                "text": "Pt 38 ans, céph + crise comitiale généralisée",
                "expected": {
                    "seizure": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Convulsions - Épilepsie",
                "text": "H 42a, céphalée, crise d'épilepsie",
                "expected": {
                    "seizure": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Convulsions - CGT",
                "text": "F 28 ans, céph, CGT ce matin",
                "expected": {
                    "seizure": True,
                    "urgency": "immediate"
                }
            },
            
            # === HTIC - HYPERTENSION INTRACRÂNIENNE ===
            {
                "category": "HTIC - Acronyme",
                "text": "Patiente 55 ans, signes d'HTIC, vomissements",
                "expected": {
                    "htic_pattern": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "HTIC - Syndrome",
                "text": "H 48a, sdm HTIC, céph matinales",
                "expected": {
                    "htic_pattern": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "HTIC - Vomissements en jet",
                "text": "F 32 ans, céphalée, vomissements en jet",
                "expected": {
                    "htic_pattern": True,
                    "urgency": "urgent"
                }
            },
            
            # === TRAUMATISME CRÂNIEN ===
            {
                "category": "Trauma - TCE",
                "text": "Pt 35a, TCE J-2, céph persistante",
                "expected": {
                    "trauma": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Trauma - TCC",
                "text": "H 28 ans, TCC hier, céphalée croissante",
                "expected": {
                    "trauma": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Trauma - AVP",
                "text": "F 40a, AVP ce matin, céph intense",
                "expected": {
                    "trauma": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Trauma - Contusion crânienne",
                "text": "Pt 45 ans, contusion crânienne J-1",
                "expected": {
                    "trauma": True,
                    "urgency": "urgent"
                }
            },
            
            # === GROSSESSE / POST-PARTUM ===
            {
                "category": "Grossesse - G1P0",
                "text": "F 28 ans G1P0, 8 SA, céphalée intense",
                "expected": {
                    "pregnancy_postpartum": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Grossesse - Terme",
                "text": "Patiente 32a, 35 SA, céph + HTA",
                "expected": {
                    "pregnancy_postpartum": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Post-partum - J+5",
                "text": "F 29 ans, J5 post-partum, céph violente",
                "expected": {
                    "pregnancy_postpartum": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Grossesse - Gravidique",
                "text": "Femme 26a, céphalée gravidique, T3",
                "expected": {
                    "pregnancy_postpartum": True,
                    "urgency": "urgent"
                }
            },
            
            # === IMMUNOSUPPRESSION ===
            {
                "category": "Immunosup - VIH+",
                "text": "Pt VIH+, CD4 150, céphalée fébrile",
                "expected": {
                    "immunosuppression": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Immunosup - Chimio",
                "text": "H 58a, chimio en cours (K poumon), céph",
                "expected": {
                    "immunosuppression": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Immunosup - Cortico",
                "text": "F 62 ans, cortico au long cours (PR), céph",
                "expected": {
                    "immunosuppression": True,
                    "urgency": "urgent"
                }
            },
            {
                "category": "Immunosup - Greffe",
                "text": "Pt 45a, greffé rénal, ttt immunosup, céph",
                "expected": {
                    "immunosuppression": True,
                    "urgency": "urgent"
                }
            },
            
            # === PROFIL TEMPORAL ===
            {
                "category": "Temporal - Aigu J0",
                "text": "Patiente 40 ans, céph depuis ce matin",
                "expected": {
                    "profile": "acute"
                }
            },
            {
                "category": "Temporal - Aigu 48h",
                "text": "H 35a, céph évoluant depuis 48h",
                "expected": {
                    "profile": "acute"
                }
            },
            {
                "category": "Temporal - Subaigu 2S",
                "text": "F 50 ans, céphalée depuis 2 semaines",
                "expected": {
                    "profile": "subacute"
                }
            },
            {
                "category": "Temporal - Subaigu 1M",
                "text": "Pt 45a, céph évoluant depuis 1 mois",
                "expected": {
                    "profile": "subacute"
                }
            },
            {
                "category": "Temporal - Chronique",
                "text": "H 55 ans, céphalées chroniques depuis 6 mois",
                "expected": {
                    "profile": "chronic"
                }
            },
            {
                "category": "Temporal - Récurrente",
                "text": "F 38a, céph récurrentes depuis des années",
                "expected": {
                    "profile": "chronic"
                }
            },
            
            # === INTENSITÉ ===
            {
                "category": "Intensité - EVA",
                "text": "Patiente 42 ans, céphalée EVA 9/10",
                "expected": {
                    "intensity": 9
                }
            },
            {
                "category": "Intensité - EN",
                "text": "H 48a, douleur EN 8/10",
                "expected": {
                    "intensity": 8
                }
            },
            {
                "category": "Intensité - Maximale",
                "text": "F 50 ans, céph intensité maximale d'emblée",
                "expected": {
                    "intensity": 10
                }
            },
            {
                "category": "Intensité - Modérée",
                "text": "Pt 35a, douleur modérée 5/10",
                "expected": {
                    "intensity": 5
                }
            },
            
            # === ABRÉVIATIONS MÉDICALES COURANTES ===
            {
                "category": "Abréviations - ATCD",
                "text": "F 55a, céph, ATCD migraines",
                "expected": {
                    "profile": "chronic"
                }
            },
            {
                "category": "Abréviations - SAU",
                "text": "Pt 40 ans, céph brutale, adressé SAU",
                "expected": {
                    "onset": "thunderclap"
                }
            },
            {
                "category": "Abréviations - AEG",
                "text": "H 65a, céph + AEG, amaigrissement",
                "expected": {
                    "urgency": "urgent"
                }
            },
            
            # === CAS COMPLEXES AVEC MULTIPLES ABRÉVIATIONS ===
            {
                "category": "Complexe - HSA suspectée",
                "text": "F 48a, céph coup de tonnerre, EVA 10/10, sdm méningé -, déficit -",
                "expected": {
                    "onset": "thunderclap",
                    "intensity": 10,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Complexe - Méningite",
                "text": "H 25a, céph fébrile, T° 39.5, RDN ++, Kernig +, Glasgow 15",
                "expected": {
                    "fever": True,
                    "meningeal_signs": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Complexe - AVC ischémique",
                "text": "Pt 62a, céph brutale + hémiparésie D + aphasie, TA 180/100",
                "expected": {
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Complexe - Trauma + déficit",
                "text": "F 70a, TCC J-1 sur chute, céph croissante + confusion",
                "expected": {
                    "trauma": True,
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Complexe - Grossesse + signes sévères",
                "text": "Patiente 28a G2P1, 32 SA, céph intense + troubles visuels + OMI",
                "expected": {
                    "pregnancy_postpartum": True,
                    "neuro_deficit": True,
                    "urgency": "immediate"
                }
            },
            {
                "category": "Complexe - Immunosup + fièvre",
                "text": "H 52a VIH+, chimio, T° 38.8, céph + photophobie",
                "expected": {
                    "immunosuppression": True,
                    "fever": True,
                    "urgency": "immediate"
                }
            },
        ]
        
        self.results = {
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    def run_test(self, test: Dict[str, Any]) -> bool:
        """Exécute un test et vérifie les résultats."""
        case, metadata = parse_free_text_to_case(test["text"])
        recommendation = decide_imaging(case)
        
        passed = True
        errors = []
        
        # Vérifier champs attendus
        for field, expected_value in test["expected"].items():
            if field == "urgency":
                actual = recommendation.urgency
            else:
                actual = getattr(case, field, None)
            
            if actual != expected_value:
                passed = False
                errors.append(f"{field}: attendu={expected_value}, obtenu={actual}")
        
        # Stocker résultat
        self.results["details"].append({
            "category": test["category"],
            "text": test["text"],
            "passed": passed,
            "errors": errors,
            "case": {
                "onset": case.onset,
                "profile": case.profile,
                "intensity": case.intensity,
                "fever": case.fever,
                "meningeal_signs": case.meningeal_signs,
                "neuro_deficit": case.neuro_deficit,
                "seizure": case.seizure,
                "htic_pattern": case.htic_pattern,
                "trauma": case.trauma,
                "pregnancy_postpartum": case.pregnancy_postpartum,
                "immunosuppression": case.immunosuppression
            },
            "recommendation": {
                "urgency": recommendation.urgency,
                "imaging": recommendation.imaging
            }
        })
        
        return passed
    
    def run_all_tests(self):
        """Exécute tous les tests."""
        print("=" * 100)
        print("TEST TERMINOLOGIE MÉDICALE FRANÇAISE - ROBUSTESSE NLU")
        print("=" * 100)
        print()
        
        # Grouper par catégorie
        categories = {}
        for test in self.tests:
            cat = test["category"].split(" - ")[0]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(test)
        
        # Exécuter tests par catégorie
        for category, tests in sorted(categories.items()):
            print(f"\n{'='*100}")
            print(f"  {category} ({len(tests)} tests)")
            print(f"{'='*100}")
            
            cat_passed = 0
            for i, test in enumerate(tests, 1):
                passed = self.run_test(test)
                
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"\n[{i}/{len(tests)}] {test['category']}")
                print(f"  Texte: {test['text']}")
                print(f"  {status}")
                
                if not passed:
                    errors = self.results["details"][-1]["errors"]
                    for error in errors:
                        print(f"    ⚠️  {error}")
                else:
                    cat_passed += 1
                
                if passed:
                    self.results["passed"] += 1
                else:
                    self.results["failed"] += 1
            
            cat_pct = (cat_passed / len(tests)) * 100
            print(f"\n  {category}: {cat_passed}/{len(tests)} ({cat_pct:.1f}%)")
        
        self.print_summary()
    
    def print_summary(self):
        """Affiche le résumé."""
        total = self.results["passed"] + self.results["failed"]
        pct = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 100)
        print("RÉSUMÉ TERMINOLOGIE MÉDICALE")
        print("=" * 100)
        print(f"Total tests:     {total}")
        print(f"Réussis:         {self.results['passed']} ({pct:.1f}%)")
        print(f"Échoués:         {self.results['failed']} ({100-pct:.1f}%)")
        print("=" * 100)
        
        # Analyser échecs par catégorie
        if self.results["failed"] > 0:
            print("\nANALYSE DES ÉCHECS:")
            failed_by_cat = {}
            for detail in self.results["details"]:
                if not detail["passed"]:
                    cat = detail["category"].split(" - ")[0]
                    if cat not in failed_by_cat:
                        failed_by_cat[cat] = []
                    failed_by_cat[cat].append(detail)
            
            for cat, failures in sorted(failed_by_cat.items()):
                print(f"\n{cat}: {len(failures)} échec(s)")
                for failure in failures[:3]:  # Max 3 exemples par catégorie
                    print(f"  - {failure['category']}")
                    print(f"    Texte: {failure['text']}")
                    for error in failure['errors']:
                        print(f"    ⚠️  {error}")
    
    def save_results(self, filename: str = "test_medical_terminology_results.json"):
        """Sauvegarde les résultats."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                "total": self.results["passed"] + self.results["failed"],
                "passed": self.results["passed"],
                "failed": self.results["failed"],
                "details": self.results["details"]
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nRésultats sauvegardés dans: {filename}")


if __name__ == "__main__":
    tester = MedicalTerminologyTester()
    tester.run_all_tests()
    tester.save_results()
