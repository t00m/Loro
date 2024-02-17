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

def save_topic(topic: str, workbook: {}) -> None:
    changes = False
    source, target = ENV['Projects']['Default']['Languages']
    ftopics = os.path.join(get_project_config_dir(source), 'topics.json')
    if os.path.exists(ftopics):
        topics = json_load(ftopics)
        if not topic in topics:
            topics[topic] = list(workbook.keys())
            changes = True
        else:
            newsids = []
            for sid in workbook.keys():
                sids = topics[topic]
                if not sid in sids:
                    newsids.append(sid)
                    changes = True
            sids.extend(newsids)
            topics[topic] = sids
    else:
        topics = {}
        topics[topic] = list(workbook.keys())
        changes = True

    if changes:
        json_save(ftopics, topics)


def save_subtopic(subtopic: str, workbook: {}) -> None:
    changes = False
    source, target = ENV['Projects']['Default']['Languages']
    fsubtopics = os.path.join(get_project_config_dir(source), 'subtopics.json')
    if os.path.exists(fsubtopics):
        subtopics = json_load(fsubtopics)
        if not subtopic in subtopics:
            subtopics[subtopic] = list(workbook.keys())
            changes = True
        else:
            newsids = []
            for sid in workbook.keys():
                sids = subtopics[subtopic]
                if not sid in sids:
                    newsids.append(sid)
                    changes = True
            sids.extend(newsids)
            subtopics[subtopic] = sids
    else:
        subtopics = {}
        subtopics[subtopic] = list(workbook.keys())
        changes = True

    if changes:
        json_save(fsubtopics, subtopics)
