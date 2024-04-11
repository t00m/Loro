#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: duden.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Duden module service for Loro
"""

import os

try:
    import duden
    DUDEN_SERVICE = False
except ModuleNotFoundError:
    DUDEN_SERVICE = False

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_config_dir

RECHTSCHREIBUNG = {
    'Ä' : 'Ae',
    'Ö' : 'Oe',
    'Ü' : 'Ue',
    'ä' : 'ae',
    'ö' : 'oe',
    'ü' : 'ue',
    'ß' : 'sz'
}


class Duden:
    def __init__(self, app):
        self.app = app
        self.log = get_logger('Duden')
        self.log.debug("Duden enabled? %s", DUDEN_SERVICE)
        self.duden = {}
        self._check()

    def _get_duden_cache_path(self):
        return os.path.join(get_project_config_dir(), 'duden.json')

    def _check(self, *args):
        if DUDEN_SERVICE:
            duden_cache = self._get_duden_cache_path()
            if not os.path.exists(duden_cache):
                json_save(duden_cache, {})
                self.log.debug("Duden cache created")
            else:
                self.duden = json_load(duden_cache)
                self.log.debug("Duden cache loaded (%d entries)", len(self.duden))

    def get_rechtschreibung(self, word: str) -> str:
        recht_word = ''
        for letter in word:
            if letter in RECHTSCHREIBUNG:
                recht_word += RECHTSCHREIBUNG[letter]
            else:
                recht_word += letter
        return recht_word

    def get_metadata(self, token) -> []:
        metadata = []
        if DUDEN_SERVICE:
            if token.text in self.duden:
                metadata = self.duden[token.text]
                # ~ self.log.debug("Word '%s' retrieved from Duden cache", token.text)
            else:
                duden_cache = self._get_duden_cache_path()
                if token.pos_ not in ['NOUN', 'NN', 'NR', 'NNP', 'NNS', 'NT']:
                    word = token.text.lower()
                else:
                    word = token.text
                recht_word = self.get_rechtschreibung(word)
                w = duden.get(recht_word)
                if w is not None:
                    metadata = w.export()
                    self.duden[token.text] = metadata
                    json_save(duden_cache, self.duden)
                    self.log.debug("Duden cache updated for word '%s' ('%s')", token.text, word)
                else:
                    self.duden[token.text] = {}
                    json_save(duden_cache, self.duden)
                    self.log.debug("Word '%s' ('%s') not found in Duden. Updating cache anyway", token.text, word)
        return metadata

    def get_word(self, word: str):
        try:
            return self.duden[word]
        except:
            return {}
