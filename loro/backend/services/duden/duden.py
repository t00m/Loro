#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: duden.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Duden module service for Loro
"""

# ~ from loro.backend.core.log import get_logger

try:
    import duden
    DUDEN_SERVICE = True
except ModuleNotFoundError:
    DUDEN_SERVICE = False

RECHTSCHREIBUNG = {
    'ä': 'ae',
    'ö': 'oe',
    'ü': 'ue',
    'ß': 'sz'
}

class DudenService:
    def __init__(self):
        # ~ self.log = get_logger('Duden')
        pass

    def rechtschreibung(self, word: str) -> str:
        duden_word = ''
        for letter in word:
            if letter in RECHTSCHREIBUNG:
                duden_word += RECHTSCHREIBUNG[letter]
            else:
                duden_word += letter
        return duden_word

ds = DudenService()
# ~ self.log.debug(ds.rechtschreibung('Große'))
print(ds.rechtschreibung('Große'))


DS = DudenService()
# ~ print("Enabled? %s" % DS.enabled)
