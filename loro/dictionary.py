#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint
from loro.core.env import ENV
from loro.core.log import get_logger
from loro.core.util import json_load, json_save
from loro.core.util import get_project_config_dir

class Dictionary:
    def __init__(self):
        self.log = get_logger('Dictionary')
        self.source, self.target = ENV['Projects']['Default']['Languages']
        configdir = get_project_config_dir(self.source)

         # Dictionary in-memory dicts
        self.sentences = {}
        self.topics = {}
        self.subtopics = {}

        # Dictionary configuration files
        self.fsents = os.path.join(get_project_config_dir(self.source), 'sentences.json')
        self.ftopics = os.path.join(get_project_config_dir(self.source), 'topics.json')
        self.fsubtopics = os.path.join(get_project_config_dir(self.source), 'subtopics.json')

        # ~ self.resources = {}
        # ~ self.resources['sentences'] = {'file': os.path.join(configdir, 'sentences.json'), 'dict': self.sentences }
        # ~ self.resources['topics'] = { 'file': os.path.join(configdir, 'topics.json'), 'dict': self.topics }
        # ~ self.resources['subtopics'] = { 'file': os.path.join(configdir, 'subtopics.json'), 'dict': self.subtopics }
        # ~ pprint.pprint(resources)

        self.load_dictionary()

    def load_dictionary(self):
        for thisfile, thisdict in [
                                    (self.fsents, self.sentences),
                                    (self.ftopics, self.topics),
                                    (self.fsubtopics, self.subtopics)
                                ]:
            if os.path.exists(thisfile):
                thisdict = json_load(thisfile)
            else:
                json_save(thisfile, thisdict)
        self.log.info("Dictionary loaded")

    def add_sentence(self, sid: str, sentence:str) -> bool:
        added = False
        if not sid in self.sentences:
            self.sentences[sid] = sentence
            added = True
        return added

    def add_topic(self, topic: str, workbook: {}) -> None:
        added = False
        if not topic in self.topics:
            self.topics[topic] = list(workbook.keys())
            added = True
        else:
            newsids = []
            for sid in workbook.keys():
                sids = self.topics[topic]
                if not sid in sids:
                    newsids.append(sid)
                    added = True
            sids.extend(newsids)
            self.topics[topic] = sids
        return added

    def add_subtopic(self, subtopic: str, workbook: {}) -> None:
        added = False
        if not subtopic in self.subtopics:
            self.subtopics[subtopic] = list(workbook.keys())
            added = True
        else:
            newsids = []
            for sid in workbook.keys():
                sids = self.subtopics[subtopic]
                if not sid in sids:
                    newsids.append(sid)
                    added = True
            sids.extend(newsids)
            self.subtopics[subtopic] = sids
        return added

    def save_dictionary(self):
        for thisfile, thisdict in [
                                    (self.fsents, self.sentences),
                                    (self.ftopics, self.topics),
                                    (self.fsubtopics, self.subtopics)
                                ]:
            json_save(thisfile, thisdict)
        self.log.info("Dictionary saved")

    def __del__(self):
        self.log.info("%d sentences, %d topics, %d subtopics", len(self.sentences), len(self.topics), len(self.subtopics))
        self.save_dictionary()
        self.log.info("Dictionary class destroyed")
