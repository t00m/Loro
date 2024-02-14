import os
import re
import pprint
from datetime import datetime

import spacy
from spacy.lang.de.examples import sentences
# ~ pip3 install -U $(spacy info de_core_news_sm --url) --user --break-system-packages
# ~ https://github.com/explosion/spacy-models/releases?q=german&expanded=true
nlp = spacy.load("de_core_news_sm")

pattern = '%d/%m/%Y, %H:%M'


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
    # ~ text = text.replace('\n', '.')
    return text.strip()

def startswith_date(text: str) -> bool:
    try:
        adate = datetime.strptime(text[:17], pattern)
        is_date = True
    except ValueError as error:
        is_date = False
    return is_date

lines = open('wchat.txt', 'r').readlines()
chat = {}
nc = 0
for line in lines:
    if startswith_date(line):
        nc += 1
        sep = line.find(':', 17) + 2
        if sep > 1:
            msg = line[sep:]
            if len(clean_text(msg)) > 0:
                chat[nc] = clean_text(msg)
    else:
        try:
            conversation = chat[nc]
            conversation += line
            chat[nc] = conversation
        except:
            pass

# ~ for nc in chat:
    # ~ print("%d > %s" % (nc, chat[nc]))

univ = {}
for nc in chat:
    doc = nlp(chat[nc])
    for token in doc:
        try:
            elems = univ[token.pos_]
            if not token.text in elems:
                elems.append(token.text)
        except:
            elems = []
            elems.append(token.text)
            univ[token.pos_] = elems
        # ~ print(token.text, token.pos_, token.dep_)

pprint.pprint(univ)
