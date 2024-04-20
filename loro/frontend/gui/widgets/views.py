#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: views.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Different views based on ColumnView widget
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import Pango

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.widgets.columnview import ColLabel, ColCheck, ColEntry
from loro.frontend.gui.models import Item, Filepath


class ColumnViewFiles(ColumnView):
    """ Custom ColumnView widget for managing files in the editor """
    __gtype_name__ = 'ColumnViewFiles'

    def __init__(self, app):
        super().__init__(app, item_type=Filepath)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Id'))
        self.cv.append_column(self.column_title)
        self.column_title.set_title(_('Filename'))
        self.column_title.set_expand(True)
        self.column_title.set_visible(True)
        self.set_has_frame(True)

class ColumnViewFilesAvailable(ColumnViewFiles):
    """ Custom ColumnView widget for managing files in the editor """
    __gtype_name__ = 'ColumnViewFilesAvailable'

    def __init__(self, app):
        super().__init__(app)
        self.column_title.set_title(_('Files available'))

class ColumnViewFilesUsed(ColumnViewFiles):
    """ Custom ColumnView widget for managing files in the editor """
    __gtype_name__ = 'ColumnViewFilesUsed'

    def __init__(self, app):
        super().__init__(app)
        self.column_title.set_title(_('Files in workbook'))

class ColumnViewToken(ColumnView):
    """ Custom ColumnView widget for tokens """
    __gtype_name__ = 'ColumnViewToken'

    def __init__(self, app):
        super().__init__(app, item_type=Item)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Id'))
        self.cv.append_column(self.column_title)
        self.column_title.set_title(_('Word'))
        self.column_title.set_expand(True)

class ColumnViewTranslationToken(ColumnViewToken):
    """ Custom ColumnView widget for tokens translation """
    __gtype_name__ = 'ColumnViewTranslationToken'

    def __init__(self, app):
        super().__init__(app)

        self.factory_pos = Gtk.SignalListItemFactory()
        self.factory_pos.connect("setup", self._on_factory_setup_pos)
        self.factory_pos.connect("bind", self._on_factory_bind_pos)
        self.factory_translation = Gtk.SignalListItemFactory()
        self.factory_translation.connect("setup", self._on_factory_setup_translation)
        self.factory_translation.connect("bind", self._on_factory_bind_translation)
        self.column_postag = Gtk.ColumnViewColumn.new(_('Part Of Speech'), self.factory_pos)
        self.column_translation = Gtk.ColumnViewColumn.new(_('Translation'), self.factory_translation)
        self.column_title.set_expand(False)
        self.column_translation.set_expand(True)
        self.cv.append_column(self.column_postag)
        self.column_postag.set_expand(False)
        self.cv.append_column(self.column_translation)
        self.prop_postag_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='postag')
        self.column_postag.set_sorter(self.prop_postag_sorter)

    def _on_factory_setup_pos(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_pos(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_text(item.postag)

    def _on_factory_setup_translation(self, factory, list_item):
        box = ColEntry()
        list_item.set_child(box)

    def _on_factory_bind_translation(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        entry = box.get_first_child()
        translator = self.app.get_widget('translator')
        entry.connect('activate', translator.set_translation_token, item)
        entry.set_text(item.translation)


class ColumnViewTranslationSentence(ColumnViewToken):
    """ Custom ColumnView widget for sentence translation """
    __gtype_name__ = 'ColumnViewTranslationSentence'

    def __init__(self, app):
        super().__init__(app)

        self.factory_filename = Gtk.SignalListItemFactory()
        self.factory_filename.connect("setup", self._on_factory_setup_filename)
        self.factory_filename.connect("bind", self._on_factory_bind_filename)
        self.factory_translation = Gtk.SignalListItemFactory()
        self.factory_translation.connect("setup", self._on_factory_setup_translation)
        self.factory_translation.connect("bind", self._on_factory_bind_translation)
        self.column_filename = Gtk.ColumnViewColumn.new(_('Filename'), self.factory_filename)
        self.column_translation = Gtk.ColumnViewColumn.new(_('Translation'), self.factory_translation)
        self.column_title.set_expand(False)
        self.column_translation.set_expand(True)
        self.cv.append_column(self.column_filename)
        self.column_filename.set_expand(False)
        self.cv.append_column(self.column_translation)
        self.prop_filename_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='filename')
        self.column_filename.set_sorter(self.prop_filename_sorter)

    def _on_factory_bind_title(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.title)
        label.set_ellipsize(True)
        label.set_lines(5)
        label.set_property('ellipsize', Pango.EllipsizeMode.MIDDLE)

    def _on_factory_setup_filename(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_filename(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_text(item.filename)

    def _on_factory_setup_translation(self, factory, list_item):
        box = ColEntry()
        list_item.set_child(box)

    def _on_factory_bind_translation(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        entry = box.get_first_child()
        translator = self.app.get_widget('translator')
        entry.connect('activate', translator.set_translation_sentence, item)
        entry.set_text(item.translation)

class ColumnViewSentences(ColumnView):
    """ Custom ColumnView widget for tokens """
    __gtype_name__ = 'ColumnViewSentences'

    def __init__(self, app):
        super().__init__(app, item_type=Item)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Id'))
        self.cv.append_column(self.column_title)
        self.column_title.set_title(_('Sentences'))
        self.column_title.set_expand(True)

class ColumnViewAnalysis(ColumnView):
    """ Custom ColumnView widget for tokens """
    __gtype_name__ = 'ColumnViewAnalysis'

    def __init__(self, app):
        super().__init__(app, item_type=Item)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Token'))
        self.cv.append_column(self.column_title)

        self.factory_lemma = Gtk.SignalListItemFactory()
        self.factory_lemma.connect("setup", self._on_factory_setup_lemma)
        self.factory_lemma.connect("bind", self._on_factory_bind_lemma)

        self.factory_postag = Gtk.SignalListItemFactory()
        self.factory_postag.connect("setup", self._on_factory_setup_postag)
        self.factory_postag.connect("bind", self._on_factory_bind_postag)

        self.factory_count = Gtk.SignalListItemFactory()
        self.factory_count.connect("setup", self._on_factory_setup_count)
        self.factory_count.connect("bind", self._on_factory_bind_count)

        self.factory_translation = Gtk.SignalListItemFactory()
        self.factory_translation.connect("setup", self._on_factory_setup_translation)
        self.factory_translation.connect("bind", self._on_factory_bind_translation)

        # Setup columnview columns
        self.column_lemma = Gtk.ColumnViewColumn.new(_('Lemma'), self.factory_lemma)
        self.column_postag = Gtk.ColumnViewColumn.new(_('POS Tag'), self.factory_postag)
        self.column_count = Gtk.ColumnViewColumn.new(_('Count'), self.factory_count)
        self.column_translation = Gtk.ColumnViewColumn.new(_('Translation'), self.factory_translation)

        self.cv.append_column(self.column_lemma)
        self.cv.append_column(self.column_postag)
        self.cv.append_column(self.column_count)
        self.cv.append_column(self.column_translation)

        self.column_translation.set_expand(True)

        # Sorting
        self.prop_lemma_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='lemma')
        self.prop_postag_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='postag')
        self.prop_count_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_number_func, user_data='count')
        self.prop_translation_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='translation')

        self.column_lemma.set_sorter(self.prop_lemma_sorter)
        self.column_postag.set_sorter(self.prop_postag_sorter)
        self.column_count.set_sorter(self.prop_count_sorter)
        self.column_translation.set_sorter(self.prop_translation_sorter)

    def _on_factory_setup_lemma(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_lemma(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.lemma)

    def _on_factory_setup_postag(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_postag(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.postag)

    def _on_factory_setup_count(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_count(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup("%d" % item.count)

    def _on_factory_setup_translation(self, factory, list_item):
        box = ColEntry()
        list_item.set_child(box)

    def _on_factory_bind_translation(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        entry = box.get_first_child()
        dashboard = self.app.get_widget('dashboard')
        # ~ entry.connect('activate', dashboard.set_translation)
        entry.set_text(item.translation)
