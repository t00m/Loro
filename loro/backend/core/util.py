#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: utils.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: utils
"""

import os
import re
import glob
import json
import math
import shutil
import hashlib
import subprocess
import multiprocessing

from loro.backend.core.config import Config
from loro.backend.core.constants import LORO_USER_DIR
from loro.backend.core.constants import LORO_USER_PROJECTS_DIR
from loro.backend.core.constants import LORO_USER_CONFIG_DIR
from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger

log = get_logger('Util')
config = Config()

def exec_cmd(cmd):
    """Execute an operating system command.
    Return:
    - document
    - True if success, False if not
    """
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
    return process.communicate()

def get_default_languages() -> ():
    return config.get_default_languages()

def get_project_dir() -> str:
    source, target = get_default_languages()
    return os.path.join(os.path.join(LORO_USER_PROJECTS_DIR, source))

def get_project_config_dir() -> str:
    return os.path.join(get_project_dir(), '.config')

def get_project_input_dir() -> str:
    return os.path.join(get_project_dir(), 'input')

def get_project_output_dir() -> str:
    return os.path.join(get_project_dir(), 'output')

def get_project_target_dir() -> str:
    source, target = get_default_languages()
    return os.path.join(get_project_output_dir(), target)

def get_project_target_workbook_dir(workbook: str):
    return os.path.join(get_project_target_dir(), workbook)

def get_project_target_workbook_html_dir(workbook: str) -> str:
    return os.path.join(get_project_target_workbook_dir(workbook), 'html')

def get_project_target_workbook_build_dir(workbook: str):
    return os.path.join(get_project_target_workbook_dir(workbook), '.build')

def setup_project_dirs(source: str, target: str) -> None:
    dir_project_source = get_project_dir()
    dir_project_config = get_project_config_dir()
    dir_project_source_input = get_project_input_dir()
    dir_project_source_output = get_project_output_dir()
    dir_project_target = get_project_target_dir()

    for directory in [
                        LORO_USER_DIR,
                        LORO_USER_PROJECTS_DIR,
                        LORO_USER_CONFIG_DIR,
                        dir_project_source,
                        dir_project_config,
                        dir_project_source_input,
                        dir_project_source_output,
                        dir_project_target,
                     ]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def get_inputs() -> []:
    return glob.glob(os.path.join(get_project_input_dir(), '*.txt'))

def delete_project_target_dirs(source: str, target: str):
    target_dir = get_project_target_dir()
    try:
        shutil.rmtree(target_dir)
    except FileNotFoundError:
        pass
    # ~ log.debug("All directories under '%s' have been deleted", target_dir)
    # ~ target_files = glob.glob(os.path.join(config_dir, '*.json'))
    # ~ for config_file in config_files:
    # ~ os.remove(config_file)
    # ~ return config_files

def create_directory(directory: str):
    os.makedirs(directory, exist_ok=True)
    log.debug("Directory %s created", directory)

def delete_directory(directory: str):
    try:
        shutil.rmtree(directory)
        log.debug("Directory %s deleted", directory)
    except FileNotFoundError:
        log.debug("Directory %s doesn't exist. Nothing deleted", directory)

def get_metadata_from_filepath(filepath:str) -> ():
    basename = os.path.basename(filepath)
    return get_metadata_from_filename(basename)

def get_metadata_from_filename(basename:str) -> ():
    dot = basename.rfind('.')
    if dot > 1:
        basename = basename[:dot]
    sep = basename.rfind('_')
    if sep > 1:
        suffix = basename[sep+1:]
        basename = basename[:sep]
    else:
        suffix = ''

    try:
        topic, subtopic = basename.split('-')
    except:
        topic = 'Unknown'
        subtopic = 'Unknown'
    return topic, subtopic, suffix

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

def valid_key(key: str) -> str:
    key = str(key).strip().replace('-', '_')
    key = str(key).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', key)

def find_item(filter_model, item):
    sorted_model = filter_model.get_model()
    list_store = sorted_model.get_model()
    pos = 0
    for key in list_store:
        if key.id == item.id:
            return pos
        pos += 1
    return -1

def get_default_workers():
    """Calculate default number or workers.
    Workers = Number of CPU / 2
    Minimum workers = 1
    """
    ncpu = multiprocessing.cpu_count()
    workers = ncpu/2
    return math.ceil(workers)
