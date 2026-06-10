"""Test the donjon generator"""

from donjon_generator import DonjonTextGenerator

print("Loading donjon generator...")
gen = DonjonTextGenerator()

# Load some data files
print("Loading text.js data...")
# text.js uses a different format - it's JS not JSON
# We need to check what format the data is in

import os
import json

# Check what files we have
print("\nFiles in donjon directory:")
for f in os.listdir(os.path.dirname(__file__)):
    if f.endswith('.js'):
        print(f"  - {f}")

# Let's try to parse the JS files or find JSON equivalents
print("\nTrying to load data...")

# For now, let's create a simple test with inline data
test_data = {
    "tavern_name": [
        "The {adjective} {noun}",
        "The {adjective} {animal}",
        "{noun}'s Rest",
        "The {color} {object}"
    ],
    "adjective": ["Broken", "Golden", "Silent", "Mystic", "Ancient", "Crimson"],
    "noun": ["Knight", "Dragon", "Crown", "Phoenix", "Chalice"],
    "animal": ["Badger", "Raven", "Wolf", "Owl", "Serpent"],
    "color": ["Red", "Blue", "Green", "Silver", "Black"],
    "object": ["Lantern", "Shield", "Rose", "Star", "Moon"]
}

gen.gen_data = test_data

print("\n=== Tavern Name Generator Test ===")
for i in range(5):
    name = gen.generate_text("tavern_name")
    print(f"  {i+1}. {name}")

print("\n=== Random Elements ===")
print(f"Adjectives: {gen.generate_list('adjective', 3)}")
print(f"Animals: {gen.generate_list('animal', 3)}")
