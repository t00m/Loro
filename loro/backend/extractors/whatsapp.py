import os
import re
import sys
import pprint
from datetime import datetime

from loro.core.util import clean_text

pattern = '%d/%m/%Y, %H:%M'

def _startswith_date(text: str) -> bool:
    try:
        adate = datetime.strptime(text[:17], pattern)
        is_date = True
    except ValueError as error:
        is_date = False
    return is_date

def get_messages(filepath: str) -> {}:
    lines = open(filepath, 'r').readlines()
    chat = {}
    nc = 0
    for line in lines:
        if _startswith_date(line):
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
    return chat

def save_sentences(filepath: str, chat: {}) -> None:
    sentences = chat.values()
    with open(filepath, 'w') as fout:
        fout.write('\n'.join(sentences))


    # ~ for nc in chat:
        # ~ print("%d > %s" % (nc, chat[nc]))


