#!/usr/bin/env python3
"""
Demo content generation for Matt
"""

import sys
sys.path.append('src')
from generation.generator import generate_variants
from visuals.compositor import create_quote_graphic

print("🔴 LFC AGENT - DEMO CONTENT")
print("=" * 50)

# 1. Iconic Moment - Gerrard (handled respectfully)
print("\n1️⃣ ICONIC MOMENT - Captain Fantastic")
context = {
    "opponent": "Manchester City",
    "date": "2026-02-08T16:30:00Z",
    "asset_description": "Steven Gerrard celebrating at Anfield",
    "context": "Captain leading Liverpool through epic battles"
}
variants = generate_variants("iconic_moment", context)
print(f"Heroic: {variants['variant_a']['caption']}")
print(f"Cheeky: {variants['variant_c']['caption']}")

# 2. Comedy/Banter - 115 charges
print("\n2️⃣ COMEDY/BANTER - Financial Fair Play")
context2 = {
    "opponent": "Manchester City", 
    "date": "2026-02-08T16:30:00Z",
    "topic": "115 charges vs Liverpool's organic success",
    "angle": "History you can't buy"
}
variants2 = generate_variants("comedy_banter", context2)
print(f"Savage: {variants2['variant_b']['caption']}")

# 3. Quote graphic
print("\n3️⃣ VISUAL - Quote Graphic")
quote_data = {
    "quote": "The difference between City and us? We have Anfield.",
    "author": "Jürgen Klopp",
    "year": 2019
}
path = create_quote_graphic(quote_data)
print(f"Created: {path}")

print("\n🔥 READY TO DOMINATE SOCIAL MEDIA!")