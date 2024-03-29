#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from gi.repository import GObject
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save


class Stats(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Stats')
        GObject.GObject.__init__(self)
        GObject.signal_new('stats-finished', Stats, GObject.SignalFlags.RUN_LAST, None, () )
        # ~ self.log.debug("Stats initialized")

    def analyze(self, workbook: str) -> {}:
        wbcache = self.app.dictionary.get_cache(workbook)
        tokens = wbcache['tokens']['data']
        stats = {}
        stats['postags'] = {}
        stats['lemmas'] = {}

        for token in tokens:
            lemma = tokens[token]['lemmas'][0]
            # Analyze POS Tags
            try:
                for postag in tokens[token]['postags']:
                    if postag not in stats['postags']:
                        stats['postags'][postag] = {}
                        stats['postags'][postag]['count'] = 1
                        stats['postags'][postag]['tokens'] = [token]
                        stats['postags'][postag]['lemmas'] = [lemma]
                    else:
                        stats['postags'][postag]['count'] += 1
                        if token not in stats['postags'][postag]['tokens']:
                            stats['postags'][postag]['tokens'].append(token)
                        if lemma not in stats['postags'][postag]['lemmas']:
                            stats['postags'][postag]['lemmas'].append(lemma)
            except Exception as error:
                self.log.error(error)
                raise

            # Analyze lemmas
            try:
                for lemma in tokens[token]['lemmas']:
                    if lemma not in stats['lemmas']:
                        stats['lemmas'][lemma] = {}
                        stats['lemmas'][lemma]['count'] = 1
                        stats['lemmas'][lemma]['tokens'] = [token]
                    else:
                        stats['lemmas'][lemma]['count'] += 1
                        if token not in stats['lemmas'][lemma]['tokens']:
                            stats['lemmas'][lemma]['tokens'].append(token)
            except Exception as error:
                self.log.error(error)
                stats = {}
        self.emit('stats-finished')
        return stats

    def get(self, workbook: str) -> {}:
        stats = self.analyze(workbook)
        DIR_WB_CONFIG = self.app.dictionary.get_cache_dir(workbook)
        FILE_WB_STATS = os.path.join(DIR_WB_CONFIG, '%s_stats.json' % workbook)
        json_save(FILE_WB_STATS, stats)
        return stats
