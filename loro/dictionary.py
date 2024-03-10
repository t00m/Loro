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
    def __init__(self, app):
        self.log = get_logger('Dictionary')
        self.app = app
        self.cache = {}

    def get_topics(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['topics']['data']

    def get_tokens(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['tokens']['data']

    def get_sentences(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['sentences']['data']

    def set_cache(self, workbook:str, data = {}):
        key = self.get_cache_key(workbook)
        self.cache[key] = data
        self.save_cache(workbook)

    def save_cache(self, workbook: str):
        key = self.get_cache_key(workbook)
        for item in self.cache[key]:
            filepath = self.cache[key][item]['file']
            data = self.cache[key][item]['data']
            json_save(filepath, data)
        self.log.debug("Workbook '%s' cache saved", workbook)

    def get_cache(self, workbook:str) -> {}:
        source, target = ENV['Projects']['Default']['Languages']
        TARGET_DIR = get_project_target_dir(source, target)
        WB_CONFIG_DIR = os.path.join(TARGET_DIR, workbook, '.config')
        key = "%s-%s-%s" % (workbook, source, target) # Cache name
        try:
            return self.cache[key]
        except KeyError:
            self.log.debug("Creating new cache for workbook '%s'", workbook)
            self.cache[key] = {}

            ftokens = os.path.join(WB_CONFIG_DIR, '%s_tokens_%s_%s.json' % (workbook, source, target))
            self.cache[key]['tokens'] = {}
            self.cache[key]['tokens']['file'] = ftokens
            if os.path.exists(ftokens):
                self.cache[key]['tokens']['data'] = json_load(ftokens)
            else:
                self.cache[key]['tokens']['data'] = {}

            fsents = os.path.join(WB_CONFIG_DIR, '%s_sentences_%s_%s.json' % (workbook, source, target))
            self.cache[key]['sentences'] = {}
            self.cache[key]['sentences']['file'] = fsents
            if os.path.exists(fsents):
                self.cache[key]['sentences']['data'] = json_load(fsents)
            else:
                self.cache[key]['sentences']['data'] = {}

            ftopics = os.path.join(WB_CONFIG_DIR, '%s_topics_%s_%s.json' % (workbook, source, target))
            self.cache[key]['topics'] = {}
            self.cache[key]['topics']['file'] = ftopics
            if os.path.exists(ftopics):
                self.cache[key]['topics']['data'] = json_load(ftopics)
            else:
                self.cache[key]['topics']['data'] = {}

            return self.cache[key]

    def get_cache_files(self, workbook:str) -> []:
        source, target = ENV['Projects']['Default']['Languages']
        TARGET_DIR = get_project_target_dir(source, target)
        WB_CONFIG_DIR = os.path.join(TARGET_DIR, workbook, '.config')
        key = "%s-%s-%s" % (workbook, source, target) # Cache name
        files = []
        self.get_cache(workbook)
        for item in self.cache[key]:
            files.append(self.cache[key][item]['file'])
        return files

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
        self.log.info("Loaded %d tokens, %d sentences and %d topics", len(self.tokens), len(self.sentences), len(self.topics))

    def initialize(self, workbook):
        self.log.debug("Initializing workbook '%s'", workbook)
        for filepath in self.get_cache_files(workbook):
            if os.path.exists(filepath):
                os.unlink(filepath)

        self.get_cache(workbook)
        self.save_cache(workbook)

    def get_cache_key(self, workbook):
        source, target = ENV['Projects']['Default']['Languages']
        return "%s-%s-%s" % (workbook, source, target)

    def __save_dictionary(self):
        self.log.debug("Dictionary config dir: '%s'", os.path.dirname(self.ftokens))
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

    def add_sentence(self, workbook:str, sid: str, sentence: str, tokens: []) -> bool:
        added = False
        if not sid in self.sentences:
            self.sentences[sid] = {}
            self.sentences[sid][self.source] = sentence
            sid_tokens = []
            self.sentences[sid]['tokens'] = tokens
            added = True
        return added

    def add_token(self, workbook:str, token: Token, sid: str, topic: str, subtopic: str):
        key = self.get_cache_key(workbook)
        self.log.debug("Token[%s] Workbook Key[%s]", token.text, key)
        cache = self.get_cache(key)
        self.log.debug("Token[%s] Cache[%s]", token.text, cache)
        try:
            token_data = cache[key]['tokens']['data'][token.text]
            if not sid in token_data['sentences']:
                token_data['sentences'].extend([sid])
            if not token.lemma_ in token_data['lemmas']:
                token_data['lemmas'].extend([token.lemma_])
            if not token.pos_ in token_data['postags']:
                token_data['postags'].extend([token.pos_])
            if not topic in token_data['topics']:
                token_data['topics'].extend([topic.upper()])
            if not subtopic in token_data['subtopics']:
                token_data['subtopics'].extend([subtopic.upper()])
            token_data['count'] += 1
        except KeyError:
            token_data = {}
            token_data['sentences']= [sid]
            token_data['lemmas'] = [token.lemma_]
            token_data['postags'] = [token.pos_]
            token_data['topics'] = {}
            token_data['topics'][topic] = {}
            token_data['topics'][topic][subtopic] = [sid]
            token_data['subtopics'] = [subtopic]
            token_data['count'] = 1
        finally:
            if not topic in token_data['topics']:
                self.log.debug("IF- Token[%s] > Topic[%s] in Token[%s]? %s", token.text, topic, token_data['topics'], topic in token_data['topics'])
                token_data['topics'][topic] = {}
                token_data['topics'][topic][subtopic] = [sid]
            else:
                self.log.debug("ELSE- Token[%s] > Topic[%s] in Token[%s]? %s", token.text, topic, token_data['topics'], topic in token_data['topics'])
                if not subtopic in token_data['topics'][topic]:
                    token_data['topics'][topic][subtopic] = [sid]
                else:
                    sids = token_data['topics'][topic][subtopic]
                    if not sid in sids:
                        sids.append(sid)
                        token_data['topics'][topic][subtopic] = sids
            cache[key]['tokens']['data'][token.text] = token_data
            self.set_cache(workbook, cache[key])

        # ~ self.tokens[token.text]['gender'] = token.morph.get('gender')
        # ~ self.log.debug("Added token '%s'", token.text)

    def get_token(name: str) -> {}:
        try:
            return self.tokens[name]
        except KeyError:
            return {}

