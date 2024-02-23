import os
import re
import glob
import json
import hashlib
import subprocess

from loro.core.constants import LORO_USER_DIR
from loro.core.constants import LORO_USER_PROJECTS_DIR
from loro.core.constants import LORO_USER_CONFIG_DIR

def setup_project_dirs(source: str, target: str) -> None:
    dir_project_source = os.path.join(LORO_USER_PROJECTS_DIR, source)
    dir_project_target = os.path.join(LORO_USER_PROJECTS_DIR, source, target)
    dir_project_config = os.path.join(dir_project_target, '.config')
    dir_project_input = os.path.join(dir_project_target, 'input')
    dir_project_output = os.path.join(dir_project_target, 'output')
    for directory in [
                        LORO_USER_DIR,
                        LORO_USER_PROJECTS_DIR,
                        LORO_USER_CONFIG_DIR,
                        dir_project_source,
                        dir_project_target,
                        dir_project_config,
                        dir_project_input,
                        dir_project_output
                     ]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_project_input_dir(source: str, target: str) -> str:
    return os.path.join(LORO_USER_PROJECTS_DIR, source, target, 'input')

def get_project_config_dir(source: str, target: str) -> str:
    return os.path.join(LORO_USER_PROJECTS_DIR, source, target, '.config')

def get_inputs(source: str, target: str) -> []:
    input_dir = get_project_input_dir(source, target)
    return glob.glob(os.path.join(input_dir, '*'))

def delete_project_config_files(source: str, target: str):
    config_dir = get_project_config_dir(source, target)
    config_files = glob.glob(os.path.join(config_dir, '*.json'))
    for config_file in config_files:
        os.remove(config_file)
    return config_files

# ~ def get_project_output_dir(source: str):
    # ~ return os.path.join(LORO_USER_PROJECTS_DIR, source, target'input')

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
        json.dump(adict, fout, sort_keys=True, indent=4, ensure_ascii=False)

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
