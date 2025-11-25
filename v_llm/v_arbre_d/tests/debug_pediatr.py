#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'source'))

from main import _normalize_text
import re

texte = "patient pediatrique avec fievre"
t_norm = _normalize_text(texte)
print(f"Texte original: '{texte}'")
print(f"Texte normalisé: '{t_norm}'")
print()

# Tester le pattern
pattern = r"\b(?:enfant|pediatr|nourrisson|bebe|nouveau[- ]?ne|adolescent)\b"
match = re.search(pattern, t_norm)
print(f"Pattern: {pattern}")
print(f"Match trouvé: {match}")
if match:
    print(f"Groupe trouvé: '{match.group()}'")
