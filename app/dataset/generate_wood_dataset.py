import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

wood_types = ["oak", "spruce", "birch", "jungle", "acacia", "dark oak", "mangrove", "cherry",]

item_types = ["door", "fence", "stairs", "planks", "slab", "button", "pressure plate", "trapdoor", "sign", "boat"]

wood_items = []

for item in item_types:
    for wood in wood_types:
        wood_items.append(
            {
                "name": f"{wood} {item}",
                "category": "block",
                "material": "wood",
                "wood_type": wood,
                "description": f"A {item.lower()} crafted from {wood.lower()} wood.",
                "obtained by": "Crafting"
            }
        )
with open(BASE_DIR / "wood_items.json", "w", encoding="utf-8") as file:
    json.dump(wood_items, file, indent=2)

print("wood_items.json created")