import os
import re
import json
import hashlib

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
    return text.strip()

    # ~ word_tokens = word_tokenize(text)
    # ~ words_tokens_lower = [word.lower() for word in word_tokens]

    # ~ if for_embedding:
        # ~ # no stemming, lowering and punctuation / stop words removal
        # ~ words_filtered = word_tokens
    # ~ else:
        # ~ words_filtered = [
            # ~ stemmer.stem(word) for word in words_tokens_lower if word not in stop_words
        # ~ ]

    # ~ text_clean = " ".join(words_filtered)
    # ~ return text_clean

def contains_numbers(word: str) -> bool:
    pattern = r"\d+"  # Match one or more digits
    return bool(re.search(pattern, word))

def validate_word(word: str) -> bool:
    text = clean_text(word)

    if len(text) > 1 and not contains_numbers(text):
        return True
