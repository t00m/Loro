#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint

from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_target_dir
from loro.backend.services.nlp.spacy import get_glossary_keys
from loro.backend.services.nlp.spacy import get_glossary_term_explained
from loro.backend.builders.excel import create_excel


class Dictionary:
    def __init__(self, workbook):
        self.log = get_logger('Dictionary')
        self.source, self.target = ENV['Projects']['Default']['Languages']
        TARGET_DIR = get_project_target_dir(self.source, self.target)
        WB_CONFIG_DIR = os.path.join(TARGET_DIR, workbook, '.config')
        if not os.path.exists(WB_CONFIG_DIR):
            os.makedirs(WB_CONFIG_DIR)

         # Dictionary in-memory dicts
        self.sentences = {}
        self.tokens = {}
        self.topics = {}

        # Initialize stats
        self.stats = {}
        self.posset = set()
        for key in get_glossary_keys():
            self.stats[key] = {}

        # Dictionary configuration files
        self.ftokens = os.path.join(WB_CONFIG_DIR, 'tokens_%s_%s.json' % (self.source, self.target))
        self.fsents = os.path.join(WB_CONFIG_DIR, 'sentences.json')
        self.ftopics = os.path.join(WB_CONFIG_DIR, 'topics.json')

        # Load (or create) personal dictionary for current project
        self.__load_dictionary()

    def __load_dictionary(self):
        if os.path.exists(self.ftokens):
            self.tokens = json_load(self.ftokens)
        else:
            json_save(self.ftokens, self.tokens)
            self.log.debug("Created new config file for tokens:")
            self.log.debug(self.ftokens)

        if os.path.exists(self.fsents):
            self.sentences = json_load(self.fsents)
        else:
            json_save(self.fsents, self.sentences)
            self.log.debug("Created new config file for sentences:")
            self.log.debug(self.fsents)

        if os.path.exists(self.ftopics):
            self.topics = json_load(self.ftopics)
        else:
            json_save(self.ftopics, self.topics)
            self.log.debug("Created new config file for topics")
            self.log.debug(self.ftopics)

        self.log.info("Tokens loaded: %d", len(self.tokens))
        self.log.info("Sentences loaded: %d", len(self.sentences))
        self.log.info("Topics loaded: %d", len(self.topics))

    def __save_dictionary(self):
        for thisfile, thisdict in [
                                    (self.ftokens, self.tokens),
                                    (self.fsents, self.sentences),
                                    (self.ftopics, self.topics),
                                ]:
            json_save(thisfile, thisdict)
            self.log.info("Dictionary '%s' saved with %d entries", os.path.basename(thisfile), len(thisdict))

    def save(self):
        self.__save_dictionary()
        self.log.debug("Dictionary saved")

    def add_sentence(self, sid: str, sentence: str, tokens: []) -> bool:
        added = False
        if not sid in self.sentences:
            self.sentences[sid] = {}
            self.sentences[sid][self.source] = sentence
            sid_tokens = []
            self.sentences[sid]['tokens'] = tokens
            added = True
        return added

    def add_token(self, token: Token, sid: str, topic: str, subtopic: str):
        try:
            metadata = self.tokens[token.text]
            if not sid in metadata['sentences']:
                metadata['sentences'].extend([sid])
            if not token.lemma_ in metadata['lemmas']:
                metadata['lemmas'].extend([token.lemma_])
            if not token.pos_ in metadata['postags']:
                metadata['postags'].extend([token.pos_])
            if not topic in metadata['topics']:
                metadata['topics'].extend([topic.upper()])
            if not subtopic in metadata['subtopics']:
                metadata['subtopics'].extend([subtopic.upper()])
            metadata['count'] += 1
        except KeyError:
            metadata = {}
            metadata['sentences']= [sid]
            metadata['lemmas'] = [token.lemma_]
            metadata['postags'] = [token.pos_]
            metadata['topics'] = [topic]
            metadata['subtopics'] = [subtopic]
            metadata['count'] = 1
        finally:
            self.tokens[token.text] = metadata

            if not topic in self.topics:
                self.topics[topic] = {}
                self.topics[topic][subtopic] = [sid]
            else:
                if not subtopic in self.topics[topic]:
                    self.topics[topic][subtopic] = [sid]
                else:
                    sids = self.topics[topic][subtopic]
                    if not sid in sids:
                        sids.append(sid)
                        self.topics[topic][subtopic] = sids

        # ~ self.tokens[token.text]['gender'] = token.morph.get('gender')

    def get_tokens(self):
        return self.tokens

    def get_token(name: str) -> {}:
        try:
            return self.tokens[name]
        except KeyError:
            return {}

    def get_topics(self):
        return self.topics

    def get_sentences(self):
        return self.sentences

