"""Script pour réorganiser les règles par ordre de priorité médicale.

Ordre de priorité:
1. acute_emergency (HSA, méningite, etc.) - urgence = immediate
2. urgent_conditions (HTIC, déficit neuro) - urgence = urgent  
3. benign_primary (migraine, algie vasculaire) - urgence = delayed/none
"""

import json
from pathlib import Path

def reorganize_rules():
    """Réorganise les règles par priorité décroissante."""
    
    rules_path = Path("rules/headache_rules.json")
    
    # Charger le fichier
    with open(rules_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rules = data.get("rules", [])
    
    # Définir l'ordre de priorité des catégories
    category_priority = {
        "acute_emergency": 1,      # Urgences vitales (HSA, méningite)
        "urgent_conditions": 2,    # Conditions urgentes (HTIC, AVC)
        "delayed_evaluation": 3,   # Évaluation différée
        "benign_primary": 4,       # Céphalées primaires bénignes
        "chronic_evaluation": 5    # Évaluations chroniques
    }
    
    # Définir l'ordre de priorité des urgences
    urgency_priority = {
        "immediate": 1,
        "urgent": 2,
        "delayed": 3,
        "none": 4
    }
    
    # Trier les règles
    def sort_key(rule):
        category = rule.get("category", "")
        urgency = rule.get("recommendation", {}).get("urgency", "none")
        
        cat_priority = category_priority.get(category, 99)
        urg_priority = urgency_priority.get(urgency, 99)
        
        # Trier par catégorie, puis par urgence
        return (cat_priority, urg_priority, rule.get("id", ""))
    
    sorted_rules = sorted(rules, key=sort_key)
    
    # Afficher le nouvel ordre
    print("Nouvel ordre des règles:")
    print("=" * 80)
    for i, rule in enumerate(sorted_rules, 1):
        category = rule.get("category", "unknown")
        urgency = rule.get("recommendation", {}).get("urgency", "none")
        rule_id = rule.get("id", "")
        name = rule.get("name", "")
        
        print(f"{i:2d}. [{urgency:10s}] [{category:20s}] {rule_id:30s} - {name}")
    
    # Mettre à jour les données
    data["rules"] = sorted_rules
    
    # Sauvegarder
    with open(rules_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Fichier {rules_path} réorganisé avec succès!")
    print(f"   Total: {len(sorted_rules)} règles")
    
    # Statistiques
    by_category = {}
    for rule in sorted_rules:
        cat = rule.get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nStatistiques par catégorie:")
    for cat, count in sorted(by_category.items(), key=lambda x: category_priority.get(x[0], 99)):
        print(f"  - {cat:25s}: {count:2d} règles")


if __name__ == "__main__":
    reorganize_rules()
