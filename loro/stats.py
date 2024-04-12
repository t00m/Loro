#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from collections import Counter

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
        self.app.workflow.connect('workflow-finished', self._on_update_stats)
        # ~ self.log.debug("Stats initialized")

    def _on_update_stats(self, workflow, workbook):
        self.get(workbook)

    def analyze(self, workbook: str) -> {}:
        wbcache = self.app.cache.get_cache(workbook)
        tokens = wbcache['tokens']['data']
        stats = {}
        stats['postags'] = {}
        stats['lemmas'] = {}
        stats['tokens'] = {}
        stats['counters'] = {}
        stats['counters']['TokenByPOS'] = {}
        stats['counters']['LemmaByPOS'] = {}

        tokens_counter = Counter()
        for tid in tokens:
            token = tokens[tid]
            count = tokens[tid]['count']
            stats['tokens'][tid] = token['count']
            tokens_counter[tid] = tokens[tid]['count']
            lemma = tokens[tid]['lemma']
            postag = tokens[tid]['postag']

            # Counter for tokens by POS
            try:
                stats['counters']['TokenByPOS'][postag]
            except KeyError:
                stats['counters']['TokenByPOS'][postag] = Counter()
            stats['counters']['TokenByPOS'][postag][tid] = count

            # Counter for tokens by POS
            try:
                stats['counters']['LemmaByPOS'][postag]
            except KeyError:
                stats['counters']['LemmaByPOS'][postag] = Counter()
            stats['counters']['LemmaByPOS'][postag][lemma] = count

            # Analyze POS tags
            try:
                stats['postags'][postag]['count'] += 1
                if token not in stats['postags'][postag]['tokens']:
                    stats['postags'][postag]['tokens'].append(tid)
                if lemma not in stats['postags'][postag]['lemmas']:
                    stats['postags'][postag]['lemmas'].append(lemma)
            except KeyError:
                stats['postags'][postag] = {}
                stats['postags'][postag]['count'] = 1
                stats['postags'][postag]['tokens'] = [tid]
                stats['postags'][postag]['lemmas'] = [lemma]

            # Analyze lemmas
            try:
                stats['lemmas'][lemma]['count'] += 1
                if token not in stats['lemmas'][lemma]['tokens']:
                    stats['lemmas'][lemma]['tokens'].append(tid)
            except KeyError:
                stats['lemmas'][lemma] = {}
                stats['lemmas'][lemma]['count'] = 1
                stats['lemmas'][lemma]['tokens'] = [tid]

        stats['counters']['tokens'] = tokens_counter

        # Counter for POS tags
        postags_counter = Counter()
        for postag in stats['postags']:
            postags_counter[postag] = stats['postags'][postag]['count']
        stats['counters']['postags'] = postags_counter

        # Counter for lemmas
        lemmas_counter = Counter()
        for lemma in stats['lemmas']:
            lemmas_counter[lemma] = stats['lemmas'][lemma]['count']
        stats['counters']['lemmas'] = lemmas_counter

        self.log.debug("Workbook '%s' stats generated", workbook)
        self.emit('stats-finished')
        return stats

    def get(self, workbook: str) -> {}:
        stats = self.analyze(workbook)
        DIR_WB_CONFIG = self.app.cache.get_cache_dir(workbook)
        FILE_WB_STATS = os.path.join(DIR_WB_CONFIG, '%s_stats.json' % workbook)
        json_save(FILE_WB_STATS, stats)
        # ~ for postag in stats['counters']['TokenByPOS']:
            # ~ pos_counter = stats['counters']['TokenByPOS'][postag]
            # ~ self.log.debug("(POSTAG) %s: %s", postag, pos_counter.most_common(10))

        # ~ for postag in stats['counters']['LemmaByPOS']:
            # ~ lemma_counter = stats['counters']['LemmaByPOS'][postag]
            # ~ self.log.debug("(LEMMAS) %s: %s", postag, lemma_counter.most_common(10))

        return stats
