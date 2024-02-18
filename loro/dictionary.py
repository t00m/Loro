#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint
from loro.core.env import ENV
from loro.core.log import get_logger
from loro.core.util import json_load, json_save
from loro.core.util import get_project_config_dir
from loro.services.nlp.spacy import get_glossary_keys

class Dictionary:
    def __init__(self):
        self.log = get_logger('Dictionary')
        self.source, self.target = ENV['Projects']['Default']['Languages']
        configdir = get_project_config_dir(self.source)

         # Dictionary in-memory dicts
        self.sentences = {}
        self.topics = {}
        self.subtopics = {}
        self.tokens = {}
        self.lemmas = {}
        self.pos = {}
        self.entities = {}

        # Initialize stats
        self.stats = {}
        self.posset = set()
        for key in get_glossary_keys():
            self.stats[key] = {}

        # Dictionary configuration files
        self.fsents = os.path.join(get_project_config_dir(self.source), 'sentences.json')
        self.ftopics = os.path.join(get_project_config_dir(self.source), 'topics.json')
        self.fsubtopics = os.path.join(get_project_config_dir(self.source), 'subtopics.json')
        self.ftokens = os.path.join(get_project_config_dir(self.source), 'tokens.json')
        self.flemmas = os.path.join(get_project_config_dir(self.source), 'lemmas.json')
        self.fpos = os.path.join(get_project_config_dir(self.source), 'pos.json')
        self.fents = os.path.join(get_project_config_dir(self.source), 'entities.json')

        # ~ self.resources = {}
        # ~ self.resources['sentences'] = {'file': os.path.join(configdir, 'sentences.json'), 'dict': self.sentences }
        # ~ self.resources['topics'] = { 'file': os.path.join(configdir, 'topics.json'), 'dict': self.topics }
        # ~ self.resources['subtopics'] = { 'file': os.path.join(configdir, 'subtopics.json'), 'dict': self.subtopics }
        # ~ pprint.pprint(resources)

        self.__load_dictionary()

    def __load_dictionary(self):
        for thisfile, thisdict in [
                                    (self.fsents, self.sentences),
                                    (self.ftopics, self.topics),
                                    (self.fsubtopics, self.subtopics),
                                    (self.ftokens, self.tokens),
                                    (self.flemmas, self.lemmas),
                                    (self.fpos, self.pos),
                                    (self.fents, self.entities)
                                ]:
            if os.path.exists(thisfile):
                thisdict = json_load(thisfile)
            else:
                json_save(thisfile, thisdict)
        self.log.info("Dictionary loaded")

    def __save_dictionary(self):
        for thisfile, thisdict in [
                                    (self.fsents, self.sentences),
                                    (self.ftopics, self.topics),
                                    (self.fsubtopics, self.subtopics),
                                    (self.ftokens, self.tokens),
                                    (self.flemmas, self.lemmas),
                                    (self.fpos, self.pos),
                                    (self.fents, self.entities)
                                ]:
            json_save(thisfile, thisdict)
        self.log.info("Dictionary saved")
        for key in self.posset:
            print("POS TAG: %s" % key)
            pprint.pprint(sorted(self.stats[key].items(), key=lambda p:p[1], reverse=True))
        # ~ pprint.pprint(self.stats)

    def add_sentence(self, sid: str, sentence:str) -> bool:
        added = False
        if not sid in self.sentences:
            self.sentences[sid] = sentence
            added = True
        return added

    def add_topic(self, topic: str, workbook: {}) -> bool:
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

    def add_subtopic(self, subtopic: str, workbook: {}) -> bool:
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

    def add_token(self, token: str, sid: str, workbook: {}):
        try:
            sids = self.tokens[token.text]['sentences']
            sids.append(sid)
            self.tokens[token.text]['sentences'] = sids
        except:
            self.tokens[token.text] = {}
            self.tokens[token.text]['sentences'] = [sid]
            self.tokens[token.text]['lemma'] = token.lemma_
            self.tokens[token.text]['pos'] = token.pos_
            self.tokens[token.text]['entities'] = workbook[sid]['entities']

        try:
            tokens = self.lemmas[token.lemma_]
            if token.text_ not in tokens:
                tokens.append(token.text)
                self.lemmas[token.lemma_] = tokens
        except:
            self.lemmas[token.lemma_] = [token.text]

        # P-O-S (Part Of Speech) tagging and stats
        ## Stats
        try:
            num = self.stats[token.pos_][token.lemma_]
            self.stats[token.pos_][token.lemma_] = num + 1
        except:
            self.stats[token.pos_][token.lemma_] = 1
        self.posset.add(token.pos_)

        try:
            tokens = self.pos[token.pos_]
            if token.text not in tokens:
                tokens.append(token.text)
            self.pos[token.pos_] = tokens
        except:
            self.pos[token.pos_] = [token.text]

        for entity in workbook[sid]['entities']:
            try:
                tokens = self.entities[entity]
                if token.text not in tokens:
                    tokens.append(token.text)
                self.entities[entity] = tokens
            except:
                self.entities[entity] = [token.text]

# ~ print("%s > Lemma [%s] POS [%s (%s)]" % (token.text, token.lemma_, pos, token.pos_))

    def __del__(self):
        self.log.info("%d sentences, %d topics, %d subtopics, %d tokens", len(self.sentences), len(self.topics), len(self.subtopics), len(self.tokens))
        # ~ print(self.tokens)
        # ~ print(type(self.tokens))
        self.__save_dictionary()
        self.log.info("Dictionary class destroyed")
