#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import GObject
from loro.backend.core.log import get_logger


class Stats(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Stats')
        GObject.GObject.__init__(self)
        GObject.signal_new('stats-finished', Stats, GObject.SignalFlags.RUN_LAST, None, () )
        self.log.debug("Stats initialized")

    def analyze(self, workbook: str) -> {}:
        wbcache = self.app.dictionary.get_cache(workbook)
        tokens = wbcache['tokens']['data']
        stats = {}
        stats['postags'] = {}
        stats['lemmas'] = {}

        for token in tokens:
            # Analyze POS Tags
            try:
                for postag in tokens[token]['postags']:
                    if postag not in stats['postags']:
                        stats['postags'][postag] = {}
                        stats['postags'][postag]['count'] = 1
                        stats['postags'][postag]['tokens'] = [token]
                    else:
                        stats['postags'][postag]['count'] += 1
                        if token not in stats['postags'][postag]['tokens']:
                            stats['postags'][postag]['tokens'].append(token)
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
        return self.analyze(workbook)
