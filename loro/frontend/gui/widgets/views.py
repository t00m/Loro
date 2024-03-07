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
from loro.frontend.gui.widgets.columnview import ColLabel, ColCheck
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
        self.column_title.set_visible(False)

        self.factory_topic = Gtk.SignalListItemFactory()
        self.factory_topic.connect("setup", self._on_factory_setup_topic)
        self.factory_topic.connect("bind", self._on_factory_bind_topic)

        self.factory_subtopic = Gtk.SignalListItemFactory()
        self.factory_subtopic.connect("setup", self._on_factory_setup_subtopic)
        self.factory_subtopic.connect("bind", self._on_factory_bind_subtopic)

        self.factory_suffix = Gtk.SignalListItemFactory()
        self.factory_suffix.connect("setup", self._on_factory_setup_suffix)
        self.factory_suffix.connect("bind", self._on_factory_bind_suffix)

        self.factory_belongsto = Gtk.SignalListItemFactory()
        self.factory_belongsto.connect("setup", self._on_factory_setup_belongsto)
        self.factory_belongsto.connect("bind", self._on_factory_bind_belongsto)

        # Setup columnview columns
        self.column_topic = Gtk.ColumnViewColumn.new(_('Topic'), self.factory_topic)
        self.column_subtopic = Gtk.ColumnViewColumn.new(_('Subtopic'), self.factory_subtopic)
        self.column_suffix = Gtk.ColumnViewColumn.new(_('Suffix'), self.factory_suffix)
        self.column_belongsto = Gtk.ColumnViewColumn.new(_('Active?'), self.factory_belongsto)

        self.cv.append_column(self.column_topic)
        self.cv.append_column(self.column_subtopic)
        self.cv.append_column(self.column_suffix)
        self.cv.append_column(self.column_belongsto)

        self.column_topic.set_expand(True)
        self.column_subtopic.set_expand(True)

        # Sorting
        self.prop_topic_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='topic')
        self.prop_subtopic_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='subtopic')
        self.prop_count_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_number_func, user_data='count')
        self.prop_translation_sorter = Gtk.CustomSorter.new(sort_func=self._on_sort_string_func, user_data='translation')

        self.column_topic.set_sorter(self.prop_topic_sorter)
        self.column_subtopic.set_sorter(self.prop_subtopic_sorter)

        # Default sorting by date
        # ~ self.cv.sort_by_column(self.column_title, Gtk.SortType.DESCENDING)

    def set_toggle_button_callback(self, callback):
        self.toggle_button_callback = callback

    def set_column_belongs_visible(self, visible):
        self.column_belongsto.set_visible(visible)

    def _on_factory_setup_topic(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_topic(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.topic)

    def _on_factory_setup_subtopic(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_subtopic(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.subtopic)

    def _on_factory_setup_suffix(self, factory, list_item):
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_suffix(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.suffix)

    def _on_factory_setup_belongsto(self, factory, list_item):
        box = ColCheck()
        list_item.set_child(box)

    def _on_factory_bind_belongsto(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        checkbox = box.get_first_child()
        checkbox.connect('toggled', self.toggle_button_callback, item)
        checkbox.set_active(item.belongs)

class ColumnViewToken(ColumnView):
    """ Custom ColumnView widget for tokens """
    __gtype_name__ = 'ColumnViewToken'

    def __init__(self, app):
        super().__init__(app, item_type=Item)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Id'))
        self.cv.append_column(self.column_title)
        self.column_title.set_title(_('Token'))
        self.column_title.set_expand(True)

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

        # Default sorting by date
        # ~ self.cv.sort_by_column(self.column_title, Gtk.SortType.DESCENDING)

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
        box = ColLabel()
        list_item.set_child(box)

    def _on_factory_bind_translation(self, factory, list_item):
        box = list_item.get_child()
        item = list_item.get_item()
        label = box.get_first_child()
        label.set_markup(item.translation)
