#!/usr/bin/env python3
"""Suite de tests complète après ajout de la détection de population."""

import subprocess
import sys

def run_test(script_name, args=None):
    """Exécute un script de test et retourne le résultat."""
    cmd = ["python3", script_name]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    print("=" * 80)
    print("SUITE DE TESTS COMPLÈTE - DÉTECTION DE POPULATION")
    print("=" * 80)
    print()
    
    tests = [
        ("Tests détection population", "tests/test_population_detection.py", None),
        ("Tests scénarios cliniques", "tests/test_scenarios.py", None),
        ("Tests unitaires thorax", "tests/test_thorax.py", ["thorax"]),
        ("Tests unitaires digestif", "tests/test_thorax.py", ["digestif"]),
    ]
    
    results = []
    
    for test_name, script, args in tests:
        print(f"\n{'=' * 80}")
        print(f"EXÉCUTION : {test_name}")
        print(f"{'=' * 80}\n")
        
        success, stdout, stderr = run_test(script, args)
        results.append((test_name, success))
        
        # Afficher uniquement le résumé
        lines = stdout.split('\n')
        in_results = False
        for line in lines:
            if 'RÉSULTATS' in line or 'RÉSUMÉ' in line:
                in_results = True
            if in_results:
                print(line)
        
        if not success:
            print(f"\n⚠️  Certains tests ont échoué")
    
    # Résumé global
    print("\n" + "=" * 80)
    print("RÉSUMÉ GLOBAL DE TOUS LES TESTS")
    print("=" * 80)
    
    total_tests = len(results)
    total_success = sum(1 for _, success in results if success)
    
    for test_name, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {test_name}")
    
    print()
    print(f"Total: {total_tests} suites de tests")
    print(f"✓ Succès: {total_success}")
    print(f"✗ Échecs: {total_tests - total_success}")
    
    success_rate = (total_success / total_tests * 100) if total_tests else 0
    print(f"\nTaux de réussite global: {success_rate:.1f}%")
    
    if total_success == total_tests:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS ! 🎉")
        print("\nLa détection automatique de population fonctionne parfaitement.")
        print("Le système peut maintenant :")
        print("  • Détecter l'âge du patient (ex: '12 ans' → enfant)")
        print("  • Reconnaître les mots-clés (enfant, adulte, pédiatrique, etc.)")
        print("  • Adapter automatiquement les recommandations")
        print("  • Discriminer entre protocoles enfant/adulte")
    else:
        print("\n⚠️  Certains tests nécessitent attention")
    
    print("=" * 80)
    
    return total_success == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
