# import difflib
# from fastapi import FastAPI
# from pydantic import BaseModel
# import json
# from pathlib import Path
# import difflib

# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# from nltk.stem import WordNetLemmatizer
# from nltk import pos_tag
# from nltk.tokenize import RegexpTokenizer
# from nltk.metrics import edit_distance

# app = FastAPI()

# CRAFTING_INTENT_KEYWORDS = ["craft", "make", "recipe", "create", "build", "construct", "generate"]
# INFO_INTENT_KEYWORDS = ["describe", "detail", "info", "information", "how", "what", "show", "give", "tell"]

# BASE_DIR = Path(__file__).resolve().parent
# with open(BASE_DIR /"dataset/items.json", "r") as f:
#     items_data = json.load(f)
# with open(BASE_DIR /"dataset/crafting.json", "r") as f:
#     crafting_data = json.load(f)
# with open(BASE_DIR /"dataset/equipments.json", "r") as f:
#     equipments_data = json.load(f)
# with open(BASE_DIR /"dataset/wood_items.json", "r") as f:
#     wood_items_data = json.load(f)
# with open(BASE_DIR /"dataset/correct_words.json", "r") as f:
#     correct_words = json.load(f)

# VALID_WORDS = correct_words + CRAFTING_INTENT_KEYWORDS + INFO_INTENT_KEYWORDS

# def get_wordnet_pos(tag):
#     if tag.startswith('J'):
#         return 'a'
#     elif tag.startswith('V'):
#         return 'v'
#     elif tag.startswith('N'):
#         return 'n'
#     elif tag.startswith('R'):
#         return 'r'
#     else:
#         return 'n'
    
# # SORT DATA
# sorted_crafting = sorted(crafting_data, key=lambda x: len(x['name']), reverse=True)
# sorted_all_items = sorted(items_data + equipments_data + wood_items_data, key=lambda x: len(x['name']), reverse=True)

# # TOKENIZATION WITH REGEX (REMOVING PUNCTUATION MARKS)
# def tokenize_with_regex(text):
#     tokenizer = RegexpTokenizer(r'\w+')
#     tokens = tokenizer.tokenize(text.lower())
#     tokens = [w.rstrip("s") for w in tokens]
#     return tokens

# # STOP WORD REMOVAL
# def remove_stopwords(tokens):
#     stop_words = set(stopwords.words('english'))
#     filtered_tokens = [word for word in tokens if word not in stop_words]
#     return filtered_tokens

# # SPELL CHECKING
# def spell_check(filtered_tokens):
#     misspelled_words = [
#     word for word in filtered_tokens
#     if word not in VALID_WORDS
#     ]
#     return misspelled_words

# # CORRECTION OF MISPELLED WORDS
# def correct_misspelled_words(misspelled_words):
#     corrections_set = {}
#     for word in misspelled_words:
#         matches = difflib.get_close_matches(word, VALID_WORDS)
#         if matches:
#             corrections_set[word] = matches[0]
    
#     return corrections_set
    
# # LEMMATIZATION
# def lemmatize_tokens(corrected_tokens):
#     lemmatizer = WordNetLemmatizer()

#     tagged_tokens = pos_tag(corrected_tokens)
#     print("Tagged Tokens: ", tagged_tokens)

#     lemmatized_tokens = []
#     for word, tag in tagged_tokens:
#         lemmatized_tokens.append(lemmatizer.lemmatize(word, get_wordnet_pos(tag)))

#     lemmatizer.lemmatize(word, get_wordnet_pos(tag))
#     print("Original token: ", corrected_tokens)
#     print("Lemmatized tokens: ", lemmatized_tokens)

#     return lemmatized_tokens

# # IDENTIFY INTENT
# def identify_intent(lemmatized_tokens):
#     if any(keyword in lemmatized_tokens for keyword in CRAFTING_INTENT_KEYWORDS):
#         print("Intent: CRAFTING RECIPE")
#         intent = "crafting_recipe"
#     else:
#         print("Intent: ITEM INFORMATION")
#         intent = "item_information"

#     return intent

# # GET CRAFTING RECIPE
# def get_crafting_recipe(lemmatized_tokens):
#     for item in sorted_crafting:
#             if all(word in lemmatized_tokens for word in item['name'].lower().split()):
#                 return {
#                     "materials" : item["materials"],
#                     "steps": item["steps"]

#                 }
#     return None

# def get_item(lemmatized_tokens, intent):
#     if intent == "crafting_recipe":
#         for item in sorted_crafting:
#             if all(word in lemmatized_tokens for word in item['name'].lower().split()):
#                 return item
#     else:
#         for item in sorted_all_items:
#                 if all(word in lemmatized_tokens for word in item['name'].lower().split()):
#                     return item
#     return None

# class ChatRequest(BaseModel):
#     message: str

# @app.post("/chat")
# def chat(request: ChatRequest):
    
#     user_message = request.message.lower().strip()


#     # TOKENIZATION WITH REGEX (REMOVING PUNCTUATION MARKS)
#     tokens = tokenize_with_regex(user_message)

#     # STOP WORD REMOVAL
#     filtered_tokens = remove_stopwords(tokens)

#     # CHECK IF ANY WORD IS MISPELLED 
#     misspelled_words = spell_check(filtered_tokens)

#     if misspelled_words:
#         corrections_set = correct_misspelled_words(misspelled_words)
#         corrected_tokens = [corrections_set.get(t, t) for t in filtered_tokens]
#         corrected_sentence = [corrections_set.get(t, t) for t in tokens]
#         print("Did you mean: ", corrected_sentence)
#     else:
#         corrected_tokens = filtered_tokens

#     # LEMMATIZATION
#     lemmatized_tokens = lemmatize_tokens(corrected_tokens)

#     # IDENTIFY INTENT
#     intent = identify_intent(lemmatized_tokens)

#     # DISPLAY DATA BASED ON INTENT
#     item = get_item(lemmatized_tokens, intent)
#     if item:
#         return item

       
#     return {"reply": "I can help with wood, stone, and iron-related crafting in minecraft."}

