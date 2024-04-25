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
        stats['summary'] = {}

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

        stats['summary']['topics'] = ', '.join(self.app.cache.get_topics(workbook))
        stats['summary']['subtopics'] = ', '.join(self.app.cache.get_subtopics(workbook))
        stats['summary']['filenames'] = ', '.join(self.app.cache.get_filenames(workbook))
        stats['summary']['postags'] = ', '.join(["%d %s" % (v, self.app.nlp.explain_term(k)) for k, v in sorted(stats['counters']['postags'].items(), key=lambda x: x[0], reverse=False)])

        try:
            counter_nouns = stats['counters']['LemmaByPOS']['NOUN']
            stats['summary']['nouns_all'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_nouns.items(), key=lambda x: x[0], reverse=False)])
            stats['summary']['nouns_common'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_nouns.most_common(10), key=lambda x: x[1], reverse=True)])
        except KeyError:
            stats['summary']['nouns_all'] = 'No nouns in this workbook'
            stats['summary']['nouns_common'] = ''

        try:
            counter_verbs = stats['counters']['LemmaByPOS']['VERB']
            stats['summary']['verbs_all'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_verbs.items(), key=lambda x: x[0], reverse=False)])
            stats['summary']['verbs_common'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_verbs.most_common(10), key=lambda x: x[1], reverse=True)])
        except KeyError:
            stats['summary']['verbs_all'] = 'No verbs in this workbook'
            stats['summary']['verbs_common'] = ''

        try:
            counter_adjs = stats['counters']['LemmaByPOS']['ADJ']
            stats['summary']['adjs_all'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_adjs.items(), key=lambda x: x[0], reverse=False)])
            stats['summary']['adjs_common'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_adjs.most_common(10), key=lambda x: x[1], reverse=True)])
        except KeyError:
            stats['summary']['adjs_all'] = 'No adjetives in this workbook'
            stats['summary']['adjs_common'] = ''

        try:
            counter_advs = stats['counters']['LemmaByPOS']['ADV']
            stats['summary']['advs_all'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_advs.items(), key=lambda x: x[0], reverse=False)])
            stats['summary']['advs_common'] = ', '.join(["%s (%d)" % (k, v) for k, v in sorted(counter_advs.most_common(10), key=lambda x: x[1], reverse=True)])
        except KeyError:
            stats['summary']['advs_all'] = 'No adverbs in this workbook'
            stats['summary']['advs_common'] = ''

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
