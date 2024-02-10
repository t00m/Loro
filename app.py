# pip3 install google-cloud-translate
# https://cloud.google.com/docs/authentication/external/set-up-adc
# export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"

import os
import re
import json
import pprint
import hashlib

import nltk
# https://data-dive.com/german-nlp-binary-text-classification-of-reviews-part1/
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
#nltk.download('german_tagset')
#nltk.download('stts')
nltk.download('stopwords')

stemmer = SnowballStemmer("german")
stop_words = set(stopwords.words("german"))

from google.cloud import translate

GO = True

try:
    GOOGLE_APPLICATION_ID = os.environ['GOOGLE_APPLICATION_ID']
except KeyError as error:
    print("GOOGLE_APPLICATION_ID envvar not set")
    GO = False

try:
    GOOGLE_APPLICATION_CREDENTIALS = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
except KeyError as error:
    print("GOOGLE_APPLICATION_CREDENTIALS envvar not set")
    GO = False

if not GO:
    exit(-1)

def json_load(filepath: str) -> {}:
    """Load into a dictionary a file in json format"""
    with open(filepath, 'r') as fin:
        adict = json.load(fin)
    return adict

def json_save(filepath: str, adict: {}) -> {}:
    """Save dictionary into a file in json format"""
    with open(filepath, 'w') as fout:
        json.dump(adict, fout, sort_keys=True, indent=4)

def get_hash(text: str) -> str:
    """Get the SHA256 hash for a given text"""
    m = hashlib.sha256()
    m.update(text.encode())
    return m.hexdigest()

if not os.path.exists('translations.json'):
    translations = {}
    json_save('translations.json', translations)
else:
    translations = json_load('translations.json')

def translate_text(text: str, project_id: str =GOOGLE_APPLICATION_ID):
    """Translate text by using Google Cloud Translate service"""
    text_hash = get_hash(text)
    print("%s -> %s" % (text, text_hash))
    try:
        print("Using cache for %s..." % text)
        translations[text_hash]
        return text_hash
    except:
        print("Using Google translate for %s..." % text)
        client = translate.TranslationServiceClient()
        location = "global"
        parent = f"projects/{project_id}/locations/{location}"

        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": "de-DE",
                "target_language_code": "en",
            }
        )
        results = []
        for result in response.translations:
            results.append(result.translated_text)
        translations[text_hash] = results
        json_save('translations.json', translations)
        return text_hash

def tokenize_sentence(sentence: str) -> []:
    return []

def process_sentence(sentence: str) -> None:
    clean_sentence = clean_text(sentence)
    print("Clean sentence: %s" % clean_sentence)
    tokens = tokenize_sentence(clean_sentence)
    print("Tokens: %s" % tokens)
    for token in tokens:
        translate_text(text=token)
    translate_text(text=sentence)

def tokenize_sentence(text: str) -> []:
    text_lowercase = text.lower()
    tokens = nltk.word_tokenize(text_lowercase)
    return tokens

def pos_tagging(tokens: []) -> []:
    tagged_tokens = nltk.pos_tag(tokens)
    return tagged_tokens

def named_entity_recognition(tokens: []) -> []:
    from nltk.chunk import conll2002_io
    text_tagged = nltk.tag.perceptron.PerceptronTagger().tag(tokens)
    entities = conll2002_io.parse(text_tagged)
    return entities
    # ~ for chunk in entities.tagged_sents:
        # ~ for t in chunk:
            # ~ if t[1] not in ['B-ORG', 'I-ORG', 'B-PER', 'I-PER', 'B-LOC', 'I-LOC']:
                # ~ print(t[0] + "/" + t[1])

def clean_text(text, for_embedding=False):
    """
        - remove any html tags (< /br> often found)
        - Keep only ASCII + European Chars and whitespace, no digits
        - remove single letter chars
        - convert all whitespaces (tabs etc.) to single wspace
        if not for embedding (but e.g. tdf-idf):
        - all lowercase
        - remove stopwords, punctuation and stemm
    """
    RE_WSPACE = re.compile(r"\s+", re.IGNORECASE)
    RE_TAGS = re.compile(r"<[^>]+>")
    RE_ASCII = re.compile(r"[^A-Za-zÀ-ž ]", re.IGNORECASE)
    RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž]\b", re.IGNORECASE)
    if for_embedding:
        # Keep punctuation
        RE_ASCII = re.compile(r"[^A-Za-zÀ-ž,.!? ]", re.IGNORECASE)
        RE_SINGLECHAR = re.compile(r"\b[A-Za-zÀ-ž,.!?]\b", re.IGNORECASE)

    text = re.sub(RE_TAGS, " ", text)
    text = re.sub(RE_ASCII, " ", text)
    text = re.sub(RE_SINGLECHAR, " ", text)
    text = re.sub(RE_WSPACE, " ", text)

    word_tokens = word_tokenize(text)
    words_tokens_lower = [word.lower() for word in word_tokens]

    if for_embedding:
        # no stemming, lowering and punctuation / stop words removal
        words_filtered = word_tokens
    else:
        words_filtered = [
            stemmer.stem(word) for word in words_tokens_lower if word not in stop_words
        ]

    text_clean = " ".join(words_filtered)
    return text_clean

text = 'Nach dem Spiel ist vor dem Spiel. Am Samstag geht es schon weiter. Die E3 spielt zu Hause gegen die jsg riol. Hier würden wir gerne auch Kuchen/ Muffins und vielleicht 2 Portionen laugengebäck anbieten. Außerdem bräuchten wir 2 Verkäufer die es an den Mann bringen.'
print("Original sentence: %s" % text)
process_sentence(sentence=text)

