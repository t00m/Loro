#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from loro.core.env import ENV
from loro.core.util import json_load, json_save
from loro.core.util import get_project_config_dir

def save_sentence(sid: str, sentence:str) -> bool:
    saved = False
    source, target = ENV['Projects']['Default']['Languages']
    fsents = os.path.join(get_project_config_dir(source), 'sentences.json')
    if os.path.exists(fsents):
        sentences = json_load(fsents)
        if not sid in sentences:
            sentences[sid] = sentence
            saved = True
    else:
        sentences = {}
        sentences[sid] = sentence
        saved = True
    if saved:
        json_save(fsents, sentences)
    return saved

# ~ def save_topic(topoic: str, workbook {}) -> None:
    # ~ source, target = ENV['Projects']['Default']['Languages']
    # ~ ftopics = os.path.join(get_project_config_dir(source), 'topics.json')
    # ~ if os.path.exists(ftopics):
        # ~ topics = json_load(ftopics)
        # ~ if not topic in topics:
            # ~ topics[topic] = list(workbook.keys())
        # ~ else:
