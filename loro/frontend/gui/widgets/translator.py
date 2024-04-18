#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: translator.py
# Author: Tomás Vírseda
# License: GPL v3
"""

import os
import sys

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.views import ColumnViewTranslationToken
from loro.frontend.gui.widgets.views import ColumnViewTranslationSentence
from loro.frontend.gui.models import TokenTranslation
from loro.frontend.gui.models import SentenceTranslation
from loro.backend.core.util import get_default_languages

class Translator(Gtk.Box):
    __gtype_name__ = 'Translator'

    def __init__(self, app):
        super(Translator, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.log = get_logger('Translator')
        self._setup_widget()
        self._connect_signals()
        # ~ self._check()
        # ~ self.update()
        self.log.debug("Translator initialized")

    def _connect_signals(self):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        ddWorkbooks.connect("notify::selected-item", self.update)

    def _setup_widget(self):
        notebook = self.app.add_widget('translator-notebook', Gtk.Notebook())
        notebook.set_show_border(False)

        cvtl = self.app.add_widget('translator-view-tokens', ColumnViewTranslationToken(self.app))
        cvtl.set_filter(self._do_filter_view_tokens)
        notebook.append_page(cvtl, Gtk.Label.new('Words'))

        cvts = self.app.add_widget('translator-view-sentences', ColumnViewTranslationSentence(self.app))
        notebook.append_page(cvts, Gtk.Label.new('Sentences'))

        self.append(notebook)

    def _do_filter_view_tokens(self, item, filter_list_model):
        cvtl = self.app.get_widget('translator-view-tokens')
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook is None:
            return True

        if workbook.id is None:
            return False

        workbook_tokens = self.app.cache.get_tokens(workbook.id)
        if item.id in workbook_tokens:
            text = cvtl.search_entry.get_text()
            found = text.upper() in item.title.upper()
            # ~ self.log.debug("'%s' in '%s'? %s", text, item.title, found)
            if found:
                return True
        return False

    def _check(self):
        """
        FIXME: Do not use this approach. It loads all workbooks.

        Scan workbooks and check if tokens/sentences were already
        registered for translations
        """
        source, target = get_default_languages()
        translations = self.app.translate
        workbooks = self.app.workbooks.get_all()
        for workbook in workbooks:
            for token in self.app.cache.get_tokens(workbook):
                if not self.app.translate.exists_token(token):
                    self.app.translate.set_token(token, target, '')
            for sid in self.app.cache.get_sentences(workbook):
                if not self.app.translate.exists_sentence(sid):
                    self.app.translate.set_sentence(sid, target, '')

    def update(self, *args):
        workbook = self.app.actions.workbook_get_current()
        if workbook is None:
            return

        source, target = get_default_languages()
        cvtl = self.app.get_widget('translator-view-tokens')
        items = []
        tlcache = self.app.translate.get_cache_tokens()
        tokens = self.app.cache.get_tokens(workbook.id)

        for tid in tokens:
            token = tokens[tid]
            postag = self.app.nlp.explain_term(token['postag']).title()
            try:
                translation = tlcache[tid][target]
            except:
                translation = ''
            items.append(TokenTranslation(
                                id = tid,
                                title = token['title'],
                                postag = postag,
                                translation = translation
                            )
                        )
        cvtl.update(items)

        cvts = self.app.get_widget('translator-view-sentences')
        items = []
        tscache = self.app.translate.get_cache_sentences()
        self.log.error(tscache)
        sentences = self.app.cache.get_sentences(workbook.id)
        self.log.error(sentences)
        for sid in sentences:
            sent_source = sentences[sid][source]
            sent_target = tscache[sid][target]
            sent_filename = sentences[sid]['filename'][0]
            # ~ try:
                # ~ translation = tlcache[tid][target]
            # ~ except:
                # ~ translation = ''
            items.append(SentenceTranslation(
                                id = sid,
                                title = sent_source,
                                filename = sent_filename,
                                translation = sent_target
                            )
                        )
        cvts.update(items)




    def set_translation(self, entry, item):
        source, target = get_default_languages()
        cache = self.app.translate.get_cache_tokens()
        translation = entry.get_text()
        self.app.translate.set_token(item.id, target, translation)
        self.log.debug("Token '%s' translated to '%s'", item.id, entry.get_text())
        self.update()
