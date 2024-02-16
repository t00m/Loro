import os
import re
import glob
import json
import hashlib
import subprocess

def get_user_documents_dir():
    return subprocess.check_output(["xdg-user-dir", "DOCUMENTS"], universal_newlines=True).strip()

def setup_project_dirs(workspace: str, source: str, target: str) -> None:
    dir_project_source = os.path.join(workspace, source)
    dir_project_source_config = os.path.join(workspace, source, '.config')
    dir_project_source_inputs = os.path.join(workspace, source, 'inputs')
    dir_project_target = os.path.join(workspace, source, target)
    for directory in [  dir_project_source,
                        dir_project_source_config,
                        dir_project_source_inputs,
                        dir_project_target
                     ]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_project_input_dir(workspace: str, source: str):
    return os.path.join(workspace, source, 'inputs')

def get_inputs(workspace: str, source: str):
    input_dir = get_project_input_dir(workspace, source)
    return glob.glob(os.path.join(input_dir, '*'))

def get_metadata_from_filepath(filepath:str) -> ():
    basename = os.path.basename(filepath)
    dot = basename.rfind('.')
    if dot > 1:
        basename = basename[:dot]
    seq = basename.rfind('_')
    if seq > 1:
        basename = basename[:seq]
    try:
        topic, subtopic = basename.split('-')
    except:
        topic = 'unknown'
        subtopic = 'unknown'
    return topic, subtopic

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

def is_number(word: str) -> bool:
    RE_NUMBERS = r"\d+"  # Match one or more digits
    return  bool(re.search(RE_NUMBERS, word))

def is_url(word: str) -> bool:
    RE_URL = re.compile(r"http\S+", re.IGNORECASE)
    return bool(re.search(RE_URL, word))

def is_tag(word: str) -> bool:
    RE_TAGS = re.compile(r"<[^>]+>", re.IGNORECASE)
    return bool(re.search(RE_TAGS, word))

def is_alpha(word: str) -> bool:
    RE_ASCII = re.compile(r"[^A-Za-zÀ-ž]", re.IGNORECASE)
    alpha = not bool(re.search(RE_ASCII, word))
    return alpha

def is_valid_word(word: str) -> bool:
    alpha = is_alpha(word)
    lenghty = len(word.strip()) > 1
    nums = is_number(word)
    tags = is_tag(word)
    urls = is_url(word)
    valid = alpha and lenghty and not nums and not tags and not urls
    # ~ print ("Word: %s [%s] > lengthy? %s, alpha? %s, not numbers? %s, not tag? %s, not url? %s" % (word, valid, lenghty, alpha, not nums, not tags, not urls))
    return valid
