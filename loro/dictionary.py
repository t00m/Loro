#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint

from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_config_dir
from loro.backend.services.nlp.spacy import get_glossary_keys
from loro.backend.services.nlp.spacy import get_glossary_term_explained
from loro.backend.builders.excel import create_excel


class Dictionary:
    def __init__(self):
        self.log = get_logger('Dictionary')
        self.source, self.target = ENV['Projects']['Default']['Languages']
        configdir = get_project_config_dir(self.source, self.target)

         # Dictionary in-memory dicts
        self.sentences = {}
        self.topics = {}
        self.subtopics = {}
        self.tokens = {}
        self.lemmas = {}
        self.pos = {}
        self.entities = {}

        self.user_tokens = {}
        self.__load_user_tokens()

        # Initialize stats
        self.stats = {}
        self.posset = set()
        for key in get_glossary_keys():
            self.stats[key] = {}

        # Dictionary configuration files
        self.fsents = os.path.join(get_project_config_dir(self.source, self.target), 'sentences.json')
        self.ftopics = os.path.join(get_project_config_dir(self.source, self.target), 'topics.json')
        self.fsubtopics = os.path.join(get_project_config_dir(self.source, self.target), 'subtopics.json')
        self.ftokens = os.path.join(get_project_config_dir(self.source, self.target), 'tokens.json')
        self.flemmas = os.path.join(get_project_config_dir(self.source, self.target), 'lemmas.json')
        self.fpos = os.path.join(get_project_config_dir(self.source, self.target), 'pos.json')
        self.fents = os.path.join(get_project_config_dir(self.source, self.target), 'entities.json')

        # ~ self.resources = {}
        # ~ self.resources['sentences'] = {'file': os.path.join(configdir, 'sentences.json'), 'dict': self.sentences }
        # ~ self.resources['topics'] = { 'file': os.path.join(configdir, 'topics.json'), 'dict': self.topics }
        # ~ self.resources['subtopics'] = { 'file': os.path.join(configdir, 'subtopics.json'), 'dict': self.subtopics }
        # ~ pprint.pprint(resources)

        # Load (or create) personal dictionary for current project
        self.__load_dictionary()

    def get_topics_file(self):
        return self.ftopics

    def get_subtopics_file(self):
        return self.fsubtopics

    def __load_user_tokens(self):
        fusertokens = os.path.join(get_project_config_dir(self.source, self.target), 'user_tokens_%s_%s.json' % (self.source, self.target))
        try:
            self.user_tokens = json_load(fusertokens)
            self.log.info("Project user tokens loaded")
        except FileNotFoundError:
            self.user_tokens = {}
            json_save(fusertokens, self.user_tokens)
            self.log.info("Project user tokens loaded (new)")

    def __save_user_tokens(self):
        fusertokens = os.path.join(get_project_config_dir(self.source, self.target), 'user_tokens_%s_%s.json' % (self.source, self.target))
        json_save(fusertokens, self.user_tokens)
        self.log.info("Project user tokens saved")

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
        # ~ self.log.info("Dictionary loaded")

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
        # ~ self.log.info("Dictionary saved")
        for key in self.posset:
            postag = get_glossary_term_explained(key).title()
            self.log.info("%s: %d", postag, len(self.stats[key]))
            # ~ if key == 'PROPN':
                # ~ self.log.info(self.stats[key])
        # ~ create_excel(self.stats, self.posset)
        # ~ for key in self.posset:
            # ~ print("POS TAG: %s" % key)
            # ~ pprint.pprint(sorted(self.stats[key].items(), key=lambda p:p[1], reverse=True))
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

    def get_topics(self):
        return sorted(list(self.topics.keys()))

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

    def get_subtopics(self):
        return sorted(list(self.subtopics.keys()))

    def get_token(self, token) -> bool:
        if token.text in self.user_tokens:
            return self.user_tokens[token.text]
        else:
            return None
        # ~ self.tokens[token.text] = self.user_tokens[token.text]

    def get_token(name: str) -> {}:
        return self.user_tokens[name]

    def add_token(self, token: Token, sid: str):
        try:
            sids = self.user_tokens[token.text]['sentences']
            sids.append(sid)
            self.user_tokens[token.text]['sentences'] = sids
        except:
            self.user_tokens[token.text] = {}
            self.user_tokens[token.text]['sentences'] = [sid]
            self.user_tokens[token.text]['lemma'] = token.lemma_
            self.user_tokens[token.text]['pos'] = token.pos_
            self.user_tokens[token.text]['gender'] = token.morph.get('gender')

        try:
            tokens = self.lemmas[token.lemma_]
            if token.text not in tokens:
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

    def __del__(self):
        self.log.info("%d sentences, %d topics, %d subtopics, %d tokens", len(self.sentences), len(self.topics), len(self.subtopics), len(self.tokens))
        # ~ print(self.tokens)
        # ~ print(type(self.tokens))
        self.__save_dictionary()
        self.__save_user_tokens()
        # ~ self.log.info("Dictionary class destroyed")
