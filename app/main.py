import difflib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from pathlib import Path
import difflib

import nltk

import os

nltk_data_path = "/opt/render/nltk_data"
os.makedirs(nltk_data_path, exist_ok=True)

nltk.download("stopwords", download_dir=nltk_data_path)
nltk.download("punkt", download_dir=nltk_data_path)
nltk.download("wordnet", download_dir=nltk_data_path)

nltk.data.path.append(nltk_data_path)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.tokenize import RegexpTokenizer
from nltk.metrics import edit_distance

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vinitahingonekar.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CRAFTING_INTENT_KEYWORDS = ["craft", "make", "recipe", "create", "build", "construct", "generate"]
INFO_INTENT_KEYWORDS = ["describe", "detail", "info", "information", "how", "what", "show", "give", "tell"]
YES_KEYWORDS = ["yes", "yeah", "y", "ya", "yep", "yup"]
NO_KEYWORDS = ["no", "n", "nope", "nah"]
WOOD = ["oak", "spruce", "birch", "jungle", "acacia", "dark oak", "mangrove", "cherry", "crimson", "warped", "bamboo"]
VARIANTS = ["oak", "spruce", "birch", "jungle", "acacia", "dark oak", "mangrove", "cherry", "crimson", "warped", "bamboo", "stone", "cobblestone"]
INGOTS = ["iron", "copper", "gold", "netherite"]
SPECIAL_PLURALS = {
    "boots": "boots",
    "leggings": "leggings",
}

BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR /"dataset/items.json", "r") as f:
    items_data = json.load(f)
with open(BASE_DIR /"dataset/crafting.json", "r") as f:
    crafting_data = json.load(f)
with open(BASE_DIR /"dataset/equipments.json", "r") as f:
    equipments_data = json.load(f)
# with open(BASE_DIR /"dataset/wood_items.json", "r") as f:
#     wood_items_data = json.load(f)
with open(BASE_DIR /"dataset/correct_words.json", "r") as f:
    correct_words = json.load(f)

VALID_WORDS = correct_words + CRAFTING_INTENT_KEYWORDS + INFO_INTENT_KEYWORDS

pending_corrected_input = ""
awaiting_response = False
skip_spell_check = False

last_item = ""
last_intent = ""

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return 'n'
    
# SORT DATA
sorted_crafting = sorted(crafting_data, key=lambda x: len(x['name']), reverse=True)
sorted_all_items = sorted(items_data + equipments_data, key=lambda x: len(x['name']), reverse=True)


def normalize_word(word, item_names):
    if word.endswith("s"):
        singular = word[:-1]
        if singular in item_names:
            return singular
    return word
    
# TOKENIZATION WITH REGEX (REMOVING PUNCTUATION MARKS)
def tokenize_with_regex(text):
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text.lower())
    # tokens = [w.rstrip("s") for w in tokens]
    return tokens

# STOP WORD REMOVAL
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

# SPELL CHECKING
# def spell_check(filtered_tokens):
#     misspelled_words = [
#     word for word in filtered_tokens
#     if word not in VALID_WORDS
#     ]
#     return misspelled_words

def spell_check(filtered_tokens):
    misspelled_words = []
    for word in filtered_tokens:
        matches = difflib.get_close_matches(word, VALID_WORDS, n=1, cutoff=0.8)
        if not matches:
            continue  # unknown word, NOT spelling mistake
        if matches[0] != word:
            misspelled_words.append(word)
    return misspelled_words

# CORRECTION OF MISPELLED WORDS
def correct_misspelled_words(misspelled_words):
    corrections_set = {}
    for word in misspelled_words:
        matches = difflib.get_close_matches(word, VALID_WORDS)
        if matches:
            corrections_set[word] = matches[0]
    
    return corrections_set
    
# LEMMATIZATION
def lemmatize_tokens(corrected_tokens):
    lemmatizer = WordNetLemmatizer()

    tagged_tokens = pos_tag(corrected_tokens)
    print("Tagged Tokens: ", tagged_tokens)

    lemmatized_tokens = []
    for word, tag in tagged_tokens:
        if word in SPECIAL_PLURALS:
            lemmatized_tokens.append(word)
        else:
            lemmatized_tokens.append(lemmatizer.lemmatize(word, get_wordnet_pos(tag)))

    lemmatizer.lemmatize(word, get_wordnet_pos(tag))
    print("Original token: ", corrected_tokens)
    print("Lemmatized tokens: ", lemmatized_tokens)

    return lemmatized_tokens

# IDENTIFY INTENT
def identify_intent(lemmatized_tokens):
    if any(keyword in lemmatized_tokens for keyword in CRAFTING_INTENT_KEYWORDS):
        print("Intent: CRAFTING RECIPE")
        intent = "crafting_recipe"
    else:
        print("Intent: ITEM INFORMATION")
        intent = "item_information"

    return intent

# GET CRAFTING RECIPE
def get_crafting_recipe(lemmatized_tokens):
    for item in sorted_crafting:
            if all(word in lemmatized_tokens for word in item['name'].lower().split()):
                return item
    return None

# GET ITEM INFORMATION
def get_item(lemmatized_tokens, dataset):
    for item in dataset:

            if all(word in lemmatized_tokens for word in item['name'].lower().split()):
                variant = None

                if(item['name'].lower() in VARIANTS):

                    for secondary_item in dataset:
                        if all(word in lemmatized_tokens for word in secondary_item['name'].lower().split()):
                            if secondary_item['name'].lower() != item['name'].lower():
                                return {
                                    "item" : secondary_item,
                                    "variant" : item['name'].lower()
                                }
                            
                    return {
                    "item": item,
                    "variant": None
                    }
                            
                if(item['item_type'] == "generic"):
                    for v in item['variants']:
                        v_words = v.split()
                        if all(word in lemmatized_tokens for word in v_words):
                            print(f"variant found = {v}")
                            variant = v
                            break

                # print(f"VARIANT getitmeinfo = {variant}")
                return {"item" : item, 
                         "variant" : variant
                         }
    return None

# GET CRAFTING SENTENCE
def get_crafting_sentence(item_data):
    item = item_data['item']
    variant = item_data['variant']

    materials_list = []

    for mat, qty in item['materials'].items():
        if mat == "{material}" and variant:

            if variant in WOOD:
                mat_name = f"{variant} planks"
            if variant in INGOTS:
                mat_name = f"{variant} ingots"
            else:
                mat_name = variant

        elif mat == "{material}":
            mat_name = "material"
        else:
            mat_name = mat

        materials_list.append(f"{qty} {mat_name}")

    materials_str = ", ".join(materials_list)

    steps_str = "\n".join(
        f"{i+1}. {step.replace('{material}', mat_name if mat_name else '')}"
        for i, step in enumerate(item['steps'])
    )

    crafting_sentence = (
        f"To craft a {variant + ' ' if variant else ''}{item['name']}, "
        f"you need {materials_str}.\n"
        f"The steps are:\n{steps_str}"
    )

    if not variant and item['item_type'] == "generic":
        variants = ", ".join(item['variants'])
        crafting_sentence += f"\nAvailable variants of {item['name']}s: {variants}"

    print(crafting_sentence)
    return crafting_sentence

# GET INFORMATION DATA
def get_information_data(item_data):
    item = item_data['item']
    variant = item_data.get('variant') 

    if variant:
        information_reply = f"{variant.title()} {item['description']}"
    else:
        information_reply = item['description']

    # information_reply = item['description']
    information_reply += f"\nIt is obtained by {item['obtained_by']}."

    if item['item_type'] == "generic":
        if variant:
            if(variant in WOOD):
                information_reply += f"\nIt can be made from {variant} planks."
            else:
                information_reply += f"\nIt can be made from {variant}."
        else:
            variants = ", ".join(item['variants'])
            information_reply += f"\nVariants are {variants}"


    elif item['item_type'] == "equipment":
        information_reply += f"\nDurability is {item['durability']}\nDefense is {item['defense']}"
    
    elif item['item_type'] == "weapon":
        information_reply += f"\nDurability is {item['durability']}\nDamage is {item['damage']}"

    if not variant:
        if(type(item['material']) == list):
            materials = ", ".join(item['material'])
        else:
            materials = item['material']
        information_reply += f"\nIt can be made from {materials}."
    
    print(information_reply)
    return information_reply


class UserInput(BaseModel):
    message: str

@app.post("/submit_data/")    
async def submit_data(user_input: UserInput):
    global awaiting_response, pending_corrected_input, skip_spell_check
    user_message = user_input.message.lower().strip()

    print("User Message: ", user_message)

    if awaiting_response:
        if(user_message in YES_KEYWORDS):
            user_message = pending_corrected_input
            pending_corrected_input = ""
            awaiting_response = False
            skip_spell_check = True
        else:
            awaiting_response = False
            item_reply = ({
                "intent": "clarification",
                "reply": "Please Rephrase your Question"
            })
            return item_reply

    # TOKENIZATION WITH REGEX (REMOVING PUNCTUATION MARKS)
    tokens = tokenize_with_regex(user_message)
    print(f"TOEKNS REGEX : {tokens}")

    # STOP WORD REMOVAL
    filtered_tokens = remove_stopwords(tokens)

    # CHECK IF ANY WORD IS MISPELLED 
    # misspelled_words = spell_check(filtered_tokens)
    misspelled_words = [] if skip_spell_check else spell_check(filtered_tokens)

    if misspelled_words:
        corrections_set = correct_misspelled_words(misspelled_words)
        corrected_tokens = [corrections_set.get(t, t) for t in filtered_tokens]
        corrected_sentence = [corrections_set.get(t, t) for t in tokens]
        corrected_sentence = " " .join(corrected_sentence)
        print("Did you mean: ", corrected_sentence)
        pending_corrected_input = corrected_sentence
        awaiting_response = True
        item_reply = ({
                "intent": "clarification",
                "reply": f'Did you mean "{corrected_sentence}" ?'
            })
        return item_reply
    else:
        corrected_tokens = filtered_tokens

    # LEMMATIZATION
    lemmatized_tokens = lemmatize_tokens(corrected_tokens)

    # IDENTIFY INTENT
    intent = identify_intent(lemmatized_tokens)

    # DISPLAY DATA BASED ON INTENT
    if intent == "crafting_recipe":
        item = get_item(lemmatized_tokens,sorted_crafting)
        if item:
            crafting_sentence = get_crafting_sentence(item)
            item_reply = ({
                "intent": "crafting_recipe",
                "reply": crafting_sentence
            })
            awaiting_response = False
            return item_reply
        else:
            return {"intent": "crafting_recipe", "reply": "Sorry, I couldn't find a crafting recipe for that item."}
        
    elif intent == "item_information":
        item = get_item(lemmatized_tokens, sorted_all_items)
        if item:
            information_reply = get_information_data(item)
            item_reply = {
                "intent": "item_information",
                "reply": information_reply
            }
            awaiting_response = False
            return item_reply

    awaiting_response = False
    return {"reply": "I can help with wood, stone, and iron-related crafting in minecraft."}


# TO DO
# suggessions
# ML ?
# 
# UI
# bot is typing
# put the suggessions on buttons easy to send data ?




