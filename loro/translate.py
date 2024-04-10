#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import get_project_config_dir
from loro.backend.core.util import json_load, json_save


class Translate:
    def __init__(self, app):
        self.app = app
        self.log = get_logger('Translate')
        config_path_tokens = self.get_cache_path_tokens()
        config_path_sentences = self.get_cache_path_sentences()

        if not os.path.exists(config_path_tokens):
            json_save(config_path_tokens, {})
        if not os.path.exists(config_path_sentences):
            json_save(config_path_sentences, {})

        self.log.debug("Translate module initialized")

    def _save_sentences(self, cache):
        cache_path = self.get_cache_path_sentences()
        json_save(cache_path, cache)

    def _save_tokens(self, cache):
        cache_path = self.get_cache_path_tokens()
        json_save(cache_path, cache)

    def get_cache_path_tokens(self) -> str:
        return os.path.join(get_project_config_dir(), 'translations_tokens.json')

    def get_cache_path_sentences(self) -> str:
        return os.path.join(get_project_config_dir(), 'translations_sentences.json')

    def get_cache_tokens(self):
        fcache = self.get_cache_path_tokens()
        return json_load(fcache)

    def get_cache_sentences(self):
        fcache = self.get_cache_path_sentences()
        return json_load(fcache)

    def get_token(self, token: str, target: str) -> str:
        cache = self.get_cache_tokens()
        try:
            return cache[token][target]
        except KeyError:
            return ''

    def set_token(self, token: str, target: str, translation: str):
        cache = self.get_cache_tokens()
        try:
            cache[token]
        except KeyError:
            cache[token] = {}

        cache[token][target] = translation
        self.log.debug("Translation for Token '%s' in language '%s' set to '%s'", token, target, translation)
        self._save_tokens(cache)

    def set_sentence(self, sid: str, target: str, translation: str):
        cache = self.get_cache_sentences()
        try:
            cache[sid]
        except KeyError:
            cache[sid] = {}

        cache[sid][target] = translation
        self.log.debug("Translation for Sentence '%s' in language '%s' set to '%s'", sid, target, translation)
        self._save_sentences(cache)

    def get_sentence(self, sid: str, target: str) -> str:
        cache = self.get_cache_sentences()
        try:
            return cache[sid][target]
        except KeyError:
            return ''

    def exists_token(self, token: str) -> bool:
        cache = self.get_cache_tokens()
        try:
            cache[token]
            return True
        except:
            return False

    def exists_sentence(self, sid: str) -> bool:
        cache = self.get_cache_sentences()
        try:
            cache[sid]
            return True
        except:
            return False
