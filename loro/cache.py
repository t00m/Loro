#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint

from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_target_dir

class Cache:
    def __init__(self, app):
        self.log = get_logger('Cache')
        self.app = app
        self.cache = {}

    def __del__(self):
        pass
        # ~ self.log.debug("Read from File[%d] / Read from Memory[%d]", self.stats['rff'], self.stats['rfm'])

    def get_topics(self, workbook: str):
        cache = self.get_cache(workbook)
        return cache['topics']['data']

    def get_subtopics(self, workbook: str):
        subtopics = set()
        cache = self.get_cache(workbook)
        for topic in self.get_topics(workbook):
            # ~ self.log.debug("Topic['%s']", topic)
            for subtopic in cache['topics']['data'][topic]:
                # ~ self.log.debug("\tSubtopic['%s']", subtopic)
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
        self.cache[key] = data
        self._save_cache(workbook)

    def _save_cache(self, workbook: str):
        key = self.get_cache_key(workbook)
        for item in self.cache[key]:
            filepath = self.cache[key][item]['file']
            data = self.cache[key][item]['data']
            json_save(filepath, data)

    def get_cache(self, workbook:str) -> {}:
        source, target = ENV['Projects']['Default']['Languages']
        WB_CONFIG_DIR = self.get_cache_dir(workbook)
        key = self.get_cache_key(workbook)
        try:
            self.cache[key]
            return self.cache[key]
        except KeyError:
            self.log.debug("Creating new cache for workbook '%s'", workbook)
            self.cache[key] = {}

            # Tokens section
            ftokens = os.path.join(WB_CONFIG_DIR, '%s_tokens_%s_%s.json' % (workbook, source, target))
            self.cache[key]['tokens'] = {}
            self.cache[key]['tokens']['file'] = ftokens
            if os.path.exists(ftokens):
                self.cache[key]['tokens']['data'] = json_load(ftokens)
            else:
                self.cache[key]['tokens']['data'] = {}

            # Lemmas section
            flemmas = os.path.join(WB_CONFIG_DIR, '%s_lemmas_%s_%s.json' % (workbook, source, target))
            self.cache[key]['lemmas'] = {}
            self.cache[key]['lemmas']['file'] = flemmas
            if os.path.exists(flemmas):
                self.cache[key]['lemmas']['data'] = json_load(flemmas)
            else:
                self.cache[key]['lemmas']['data'] = {}

            # Sentences section
            fsents = os.path.join(WB_CONFIG_DIR, '%s_sentences_%s_%s.json' % (workbook, source, target))
            self.cache[key]['sentences'] = {}
            self.cache[key]['sentences']['file'] = fsents
            if os.path.exists(fsents):
                self.cache[key]['sentences']['data'] = json_load(fsents)
            else:
                self.cache[key]['sentences']['data'] = {}

            # Topics section
            ftopics = os.path.join(WB_CONFIG_DIR, '%s_topics_%s_%s.json' % (workbook, source, target))
            self.cache[key]['topics'] = {}
            self.cache[key]['topics']['file'] = ftopics
            if os.path.exists(ftopics):
                self.cache[key]['topics']['data'] = json_load(ftopics)
            else:
                self.cache[key]['topics']['data'] = {}

            # Workbook files section
            ffnames = os.path.join(WB_CONFIG_DIR, '%s_filenames_%s_%s.json' % (workbook, source, target))
            self.cache[key]['filenames'] = {}
            self.cache[key]['filenames']['file'] = ffnames
            if os.path.exists(ftopics):
                self.cache[key]['filenames']['data'] = json_load(ffnames)
            else:
                self.cache[key]['filenames']['data'] = {}

            self.save(workbook)

            return self.cache[key]

    def get_cache_dir(self, workbook: str) -> str:
        source, target = ENV['Projects']['Default']['Languages']
        TARGET_DIR = get_project_target_dir(source, target)
        WB_CONFIG_DIR = os.path.join(TARGET_DIR, workbook, '.config')
        return WB_CONFIG_DIR

    def get_cache_files(self, workbook:str) -> []:
        key = self.get_cache_key(workbook)
        files = []
        self.get_cache(workbook)
        for item in self.cache[key]:
            files.append(self.cache[key][item]['file'])
        return files

    def initialize(self, workbook):
        # ~ self.log.debug("Initializing workbook '%s'", workbook)
        cache_files = self.get_cache_files(workbook)
        for filepath in cache_files:
            if os.path.exists(filepath):
                os.unlink(filepath)
                # ~ self.log.debug("\tDeleting file '%s'", os.path.basename(filepath))

        for filepath in cache_files:
            dirpath = os.path.dirname(filepath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
                # ~ self.log.debug("\tCreating directory '%s'", dirpath)

        key = self.get_cache_key(workbook)
        del(self.cache[key])
        self.get_cache(workbook)
        self._save_cache(workbook)

    def get_cache_key(self, workbook):
        source, target = ENV['Projects']['Default']['Languages']
        return "%s-%s-%s" % (workbook, source, target)

    def save(self, workbook):
        self._save_cache(workbook)
        # ~ self.log.debug("Workbook '%s' cache saved", workbook)

    def add_sentence(self, workbook:str, filename: str, sid: str, sentence: str, tokens: []) -> bool:
        source, target = ENV['Projects']['Default']['Languages']
        cache = self.get_cache(workbook)
        sentences = cache['sentences']['data']
        added = False
        if sid not in sentences:
            sentences[sid] = {}
            sentences[sid][source] = sentence
            try:
                # ~ filenames = sentences[sid]['filename']
                filenames.append(filename)
                sentences[sid]['filename'] = filenames
            except:
                sentences[sid]['filename'] = [filename]
            sid_tokens = []
            sentences[sid]['tokens'] = tokens
            added = True
            cache['sentences']['data'] = sentences

        # Register filename/sentence
        try:
            sents = cache['filenames']['data'][filename]
            sents.append(sid)
            cache['filenames']['data'][filename] = sents
        except:
            cache['filenames']['data'][filename] = [sid]

        self.set_cache(workbook, cache)

        return added

    def add_token(self, workbook:str, token: Token, sid: str, topic: str, subtopic: str):
        cache = self.get_cache(workbook)
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
        finally:
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

            lemma_data = cache['lemmas']['data']
            try:
                sentences = lemma_data[token.lemma_]
                if not sid in sentences:
                    sentences.append(sid)
                lemma_data[token.lemma_] = sentences
            except:
                lemma_data[token.lemma_] = [sid]

            cache['topics']['data'] = topic_data
            cache['tokens']['data'][token.text] = token_data
            cache['lemmas']['data'] = lemma_data
            self.set_cache(workbook, cache)

            self.app.duden.get_metadata(token)

        # ~ self.tokens[token.text]['gender'] = token.morph.get('gender')
        # ~ self.log.debug("Added token '%s'", token.text)

    def get_token(name: str) -> {}:
        try:
            return self.tokens[name]
        except KeyError:
            return {}
