#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint

from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_target_dir
from loro.backend.core.util import get_project_config_dir


class Dictionary:
    def __init__(self, app):
        self.log = get_logger('Dictionary')
        self.app = app
        self.tk_cache = self.__init_tokens_cache()
        self.wb_cache = {}

    def __del__(self):
        self.log.debug("Read from File[%d] / Read from Memory[%d]", self.stats['rff'], self.stats['rfm'])

    def __get_tokens_cache_path(self):
        source, target = ENV['Projects']['Default']['Languages']
        cache_dir = get_project_config_dir(source)
        cache_file = 'tokens_%s.json' % source
        cache_path = os.path.join(cache_dir, cache_file)
        return cache_path

    def __init_tokens_cache(self):
        cache_path = self.__get_tokens_cache_path()
        self.log.debug("Tokens main cache: '%s'", cache_path)
        if not os.path.exists(cache_path):
            json_save(cache_path, {})
            tcache = {}
        else:
            tcache = json_load(cache_path)
        return tcache

    def get_topics(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['topics']['data']

    def get_subtopics(self, workbook: str):
        subtopics = set()
        cache = self.get_cache(workbook)
        for topic in self.get_topics(workbook):
            for subtopic in cache['topics']['data'][topic]:
                subtopics.add(subtopic)
        return subtopics

    def get_tokens(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['tokens']['data']

    def get_sentences(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['sentences']['data']

    def set_cache(self, workbook:str, data = {}):
        key = self.get_cache_key(workbook)
        self.wb_cache[key] = data
        self._save_cache(workbook)

    def _save_cache(self, workbook: str):
        key = self.get_cache_key(workbook)
        for item in self.wb_cache[key]:
            filepath = self.wb_cache[key][item]['file']
            data = self.wb_cache[key][item]['data']
            json_save(filepath, data)

    def get_cache(self, workbook:str) -> {}:
        source, target = ENV['Projects']['Default']['Languages']
        WB_CONFIG_DIR = self.get_cache_dir(workbook)
        key = self.get_cache_key(workbook)
        try:
            self.wb_cache[key]
            return self.wb_cache[key]
        except KeyError:
            self.log.debug("Creating new cache for workbook '%s'", workbook)
            self.wb_cache[key] = {}

            ftokens = os.path.join(WB_CONFIG_DIR, '%s_tokens_%s_%s.json' % (workbook, source, target))
            self.wb_cache[key]['tokens'] = {}
            self.wb_cache[key]['tokens']['file'] = ftokens
            if os.path.exists(ftokens):
                self.wb_cache[key]['tokens']['data'] = json_load(ftokens)
            else:
                self.wb_cache[key]['tokens']['data'] = {}
            # ~ source, target = ENV['Projects']['Default']['Languages']
            fsents = os.path.join(WB_CONFIG_DIR, '%s_sentences_%s_%s.json' % (workbook, source, target))
            self.wb_cache[key]['sentences'] = {}
            self.wb_cache[key]['sentences']['file'] = fsents
            if os.path.exists(fsents):
                self.wb_cache[key]['sentences']['data'] = json_load(fsents)
            else:
                self.wb_cache[key]['sentences']['data'] = {}

            ftopics = os.path.join(WB_CONFIG_DIR, '%s_topics_%s_%s.json' % (workbook, source, target))
            self.wb_cache[key]['topics'] = {}
            self.wb_cache[key]['topics']['file'] = ftopics
            if os.path.exists(ftopics):
                self.wb_cache[key]['topics']['data'] = json_load(ftopics)
            else:
                self.wb_cache[key]['topics']['data'] = {}

            self.save(workbook)

            return self.wb_cache[key]

    def get_cache_dir(self, workbook: str) -> str:
        source, target = ENV['Projects']['Default']['Languages']
        TARGET_DIR = get_project_target_dir(source, target)
        WB_CONFIG_DIR = os.path.join(TARGET_DIR, workbook, '.config')
        return WB_CONFIG_DIR

    def get_cache_files(self, workbook:str) -> []:
        key = self.get_cache_key(workbook)
        files = []
        self.get_cache(workbook)
        for item in self.wb_cache[key]:
            files.append(self.wb_cache[key][item]['file'])
        return files

    def initialize(self, workbook):
        self.log.debug("Initializing workbook '%s'", workbook)
        cache_files = self.get_cache_files(workbook)
        for filepath in cache_files:
            if os.path.exists(filepath):
                os.unlink(filepath)
                self.log.debug("\tDeleting file '%s'", os.path.basename(filepath))

        for filepath in cache_files:
            dirpath = os.path.dirname(filepath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
                self.log.debug("\tCreating directory '%s'", dirpath)

        key = self.get_cache_key(workbook)
        del(self.wb_cache[key])
        self.get_cache(workbook)
        self._save_cache(workbook)

    def get_cache_key(self, workbook):
        source, target = ENV['Projects']['Default']['Languages']
        return "%s-%s-%s" % (workbook, source, target)

    def save(self, workbook):
        self._save_cache(workbook)
        # ~ self.log.debug("Workbook '%s' dictionary saved", workbook)

    def add_sentence(self, workbook:str, sid: str, sentence: str, tokens: []) -> bool:
        source, target = ENV['Projects']['Default']['Languages']
        cache = self.get_cache(workbook)
        sentences = cache['sentences']['data']
        added = False
        if sid not in sentences:
            sentences[sid] = {}
            sentences[sid][source] = sentence
            sid_tokens = []
            sentences[sid]['tokens'] = tokens
            added = True
            cache['sentences']['data'] = sentences
            self.set_cache(workbook, cache)
        return added

    def add_token(self, workbook:str, token: Token, sid: str, topic: str, subtopic: str):
        this_token = self.__get_token_from_main_cache(token.text)
        cache = self.get_cache(workbook)
        if this_token is None:
            # Get token metadata and add it to the tokens main cache

            # Tokens dictionary
            try:
                token_data = cache['tokens']['data'][token.text]
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
                token_data['topics'] = [topic]
                token_data['subtopics'] = [subtopic]
                token_data['count'] = 1
            self.__add_token_to_main_cache(token.text, token_data)
        else:
            # Retrieve metdata from tokens main cache
            token_data = this_token

        # Topics dictionary
        topic_data = cache['topics']['data']
        if not topic in topic_data:
            topic_data[topic] = {}
            topic_data[topic][subtopic] = [sid]
        else:
            if not subtopic in topic_data[topic]:
                topic_data[subtopic] = [sid]
            else:
                sids = topic_data[topic][subtopic]
                if not sid in sids:
                    sids.append(sid)
                    topic_data[topic][subtopic] = sids

        # Save data
        cache['topics']['data'] = topic_data
        cache['tokens']['data'][token.text] = token_data
        self.set_cache(workbook, cache)

        # ~ self.tokens[token.text]['gender'] = token.morph.get('gender')
        # ~ self.log.debug("Added token '%s'", token.text)

    def get_token(name: str) -> {}:
        try:
            return self.tokens[name]
        except KeyError:
            return {}

    def __get_token_from_main_cache(self, token: str) -> {}:
        try:
            this_token = self.tk_cache[token]
            return this_token
        except KeyError:
            return None

    def __add_token_to_main_cache(self, token: str, data: {}):
        cache_path = self.__get_tokens_cache_path()
        self.tk_cache[token] = data
        json_save(cache_path, self.tk_cache)
