import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR /"items.json", "r") as f:
    items_data = json.load(f)
with open(BASE_DIR /"crafting.json", "r") as f:
    crafting_data = json.load(f)
with open(BASE_DIR /"equipments.json", "r") as f:
    equipments_data = json.load(f)
with open(BASE_DIR /"wood_items.json", "r") as f:
    wood_items_data = json.load(f)


correct_words = set()

ALL_DATA = items_data + equipments_data + wood_items_data + crafting_data

for item in ALL_DATA:
    words = item["name"].lower().split()  # 👈 THIS LINE FIXES IT
    for w in words:
        correct_words.add(w)


with open(BASE_DIR / "correct_words.json", "w", encoding="utf-8") as file:
    json.dump(list(correct_words), file, indent=2)

print("correct_words.json created")
# print(f"Total correct words: {len(correct_words)}")
# print(correct_words)