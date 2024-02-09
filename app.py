# pip3 install google-cloud-translate
# https://cloud.google.com/docs/authentication/external/set-up-adc
# export GOOGLE_APPLICATION_CREDENTIALS="/home/user/Downloads/service-account-file.json"

import os
import json
import pprint
import hashlib

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

def translate_text(text: str, project_id: str =GOOGLE_APPLICATION_ID):
    """Translate text by using Google Cloud Translate service"""
    text_hash = get_hash(text)
    print("%s -> %s" % (text, text_hash))
    try:
        print("Using cache...")
        translations[text_hash]
        return text_hash
    except:
        print("Using Google translate")
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

if not os.path.exists('translations.json'):
    translations = {}
    json_save('translations.json', translations)
else:
    translations = json_load('translations.json')

text_hash = translate_text(text='Hallo')
pprint.pprint(translations[text_hash])
