#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from gi.repository import GObject

from loro.backend.core.constants import LORO_USER_CNF
from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger


def json_load(filepath: str) -> {}:
    """Load into a dictionary a file in json format"""
    with open(filepath, 'r') as fin:
        adict = json.load(fin)
    return adict

def json_save(filepath: str, adict: {}) -> {}:
    """Save dictionary into a file in json format"""
    with open(filepath, 'w') as fout:
        json.dump(adict, fout, sort_keys=True, indent=4, ensure_ascii=False)

class Config(GObject.GObject):
    def __init__(self):
        super().__init__()
        self.log = get_logger('Config')

        # If config doesn't exist, create it
        try:
            CNF = self.get()
        except FileNotFoundError:
            CNF = {}
            CNF['Projects'] = {}
            CNF['Projects']['Default'] = {}
            CNF['Projects']['Default']['Languages'] = ENV['Projects']['Default']['Languages']
            json_save(LORO_USER_CNF, CNF)
            self.log.debug("Loro config file created with default values")

    def get(self):
        return json_load(LORO_USER_CNF)

    def get_default_languages(self):
        CNF = json_load(LORO_USER_CNF)
        return CNF['Projects']['Default']['Languages']

    def set_default_languages(self, source, target):
        CNF = self.get()
        CNF['Projects']['Default']['Languages'] = [(source, target)]
        json_save(LORO_USER_CNF, CNF)
