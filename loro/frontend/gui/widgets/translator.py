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
from loro.frontend.gui.widgets.views import ColumnViewTranslation
from loro.frontend.gui.models import TokenTranslation


class Translator(Gtk.Box):
    __gtype_name__ = 'Translator'

    def __init__(self, app):
        super(Translator, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.log = get_logger('Translator')
        self._setup_widget()
        self._check()
        # ~ self.update()
        self.log.debug("Translator initialized")

    def _setup_widget(self):
        cvtl = self.app.add_widget('translator-view-tokens', ColumnViewTranslation(self.app))
        cvtl.set_filter(self._do_filter_view_tokens)
        self.append(cvtl)

    def _do_filter_view_tokens(self, item, filter_list_model):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook is None:
            return True

        if workbook.id is None:
            return True
        workbook_tokens = self.app.cache.get_tokens(workbook.id)
        if item.id in workbook_tokens:
            return True
        return False

    def _check(self):
        """
        Scan workbooks and check if tokens/sentences were already
        registered for translations
        """
        source, target = ENV['Projects']['Default']['Languages']
        translations = self.app.translate
        workbooks = self.app.workbooks.get_all()
        for workbook in workbooks:
            for token in self.app.cache.get_tokens(workbook):
                if not self.app.translate.exists_token(token):
                    self.app.translate.set_token(token, target, '')
            for sid in self.app.cache.get_sentences(workbook):
                if not self.app.translate.exists_sentence(sid):
                    self.app.translate.set_sentence(sid, target, '')

    def update(self):
        source, target = ENV['Projects']['Default']['Languages']
        cvtl = self.app.get_widget('translator-view-tokens')
        items = []
        cache = self.app.translate.get_cache_tokens()
        for token in cache:
            items.append(TokenTranslation(
                                id = token,
                                title = token,
                                translation = cache[token][target]
                            )
                        )
        cvtl.update(items)

    def set_translation(self, entry, item):
        source, target = ENV['Projects']['Default']['Languages']
        cache = self.app.translate.get_cache_tokens()
        translation = entry.get_text()
        self.app.translate.set_token(item.id, target, translation)
        self.log.debug("Token '%s' translated to '%s'", item.id, entry.get_text())
