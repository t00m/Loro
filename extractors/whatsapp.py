import os
import re
import sys
import pprint
from datetime import datetime

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

lines = open(sys.argv[1], 'r').readlines()
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

for nc in chat:
    print("%d > %s" % (nc, chat[nc]))


