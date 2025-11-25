#!/usr/bin/env python3
"""Démonstration de la détection automatique de population."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source'))

from main import analyse_texte_medical, _load_system_entries, _match_best_entry, _normalize_key, _normalize_text

def demo_population_detection():
    """Démonstration de comment la population aide au diagnostic."""
    
    print("=" * 80)
    print("DÉMONSTRATION : DÉTECTION AUTOMATIQUE DE POPULATION")
    print("=" * 80)
    print()
    
    # Cas 1 : Appendicite enfant vs adulte
    print("CAS 1 : DOULEUR ABDOMINALE - DISCRIMINATION ENFANT/ADULTE")
    print("-" * 80)
    
    scenarios = [
        ("enfant 10 ans douleur fosse iliaque droite", "enfant"),
        ("patient 35 ans douleur FID", "adulte"),
        ("femme 28 ans enceinte grossesse douleur FID", "grossesse"),
    ]
    
    entries = _load_system_entries("digestif")
    
    for texte, expected_category in scenarios:
        print(f"\nTexte: \"{texte}\"")
        f = analyse_texte_medical(texte)
        
        print(f"  → Âge détecté: {f.get('age') or 'non détecté'}")
        if f.get('age'):
            print(f"  → Population: {f.get('population')}")
        if f.get('grossesse'):
            print(f"  → Grossesse: Oui")
        
        # Simuler les réponses
        t_norm = _normalize_text(texte)
        positives = set()
        
        # Ajouter les symptômes de base pour appendicite
        base_symptoms = ["douleur fid", "douleur abdominale", "suspicion appendicite"]
        for symptom in base_symptoms:
            positives.add(_normalize_key(symptom))
        
        # Matcher
        best, score = _match_best_entry(entries, positives, f)
        
        if best:
            print(f"  ✓ Recommandation: {best['modalite']}")
            print(f"    (ID: {best['id']}, Score: {score})")
            populations = best.get('populations', [])
            if populations:
                print(f"    Populations cibles: {', '.join(populations)}")
        print()
    
    # Cas 2 : Impact sur le score
    print("\n" + "=" * 80)
    print("CAS 2 : IMPACT DE LA POPULATION SUR LE SCORE")
    print("-" * 80)
    
    # Test avec enfant
    texte_enfant = "enfant 8 ans douleur abdominale FID"
    f_enfant = analyse_texte_medical(texte_enfant)
    
    positives = set()
    for symptom in ["douleur fid", "douleur abdominale"]:
        positives.add(_normalize_key(symptom))
    
    print(f"\nTexte: \"{texte_enfant}\"")
    print(f"Population détectée: {f_enfant.get('population')}")
    print(f"\nScores des différentes recommandations:")
    
    candidates = []
    for e in entries:
        if "appendicite" in e.get('id', '').lower():
            items = set()
            for fld in ("symptomes", "indications_positives"):
                for v in (e.get(fld) or []):
                    items.add(_normalize_key(v))
            base_score = len(items & positives)
            
            # Calcul du bonus de population
            populations = e.get("populations") or []
            population_bonus = 0
            if f_enfant.get("population") and f_enfant["population"] in populations:
                population_bonus = 1.0
            
            total_score = base_score + population_bonus
            candidates.append({
                'id': e['id'],
                'modalite': e['modalite'],
                'populations': populations,
                'base_score': base_score,
                'population_bonus': population_bonus,
                'total_score': total_score
            })
    
    # Trier par score décroissant
    candidates.sort(key=lambda x: x['total_score'], reverse=True)
    
    for i, cand in enumerate(candidates[:5], 1):
        marker = "★" if i == 1 else " "
        print(f"\n{marker} {cand['id']}")
        print(f"  Modalité: {cand['modalite']}")
        print(f"  Populations: {', '.join(cand['populations'])}")
        print(f"  Score base: {cand['base_score']}")
        print(f"  Bonus population: +{cand['population_bonus']}")
        print(f"  Score total: {cand['total_score']}")
    
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    print("""
La détection automatique de population permet de :
  
  ✓ Détecter l'âge (ex: "12 ans" → enfant)
  ✓ Détecter les mots-clés (ex: "enfant", "adulte", "pédiatrique")  
  ✓ Ajuster automatiquement les recommandations
  ✓ Prioriser les examens adaptés à chaque population
  ✓ Améliorer la précision du diagnostic

Le système applique un bonus de +1.0 points quand la population
correspond aux populations cibles de l'entrée JSON, ce qui permet
de discriminer entre plusieurs recommandations similaires.
""")
    print("=" * 80)

if __name__ == "__main__":
    demo_population_detection()
