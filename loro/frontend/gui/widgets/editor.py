#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os

from gi.repository import Gio, Adw, Gtk  # type:ignore

from loro.frontend.gui.factory import WidgetFactory
from loro.frontend.gui.actions import WidgetActions
from loro.frontend.gui.models import Filepath
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.widgets.views import ColumnViewFiles
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.core.util import get_inputs
from loro.backend.core.log import get_logger
from loro.backend.services.nlp.spacy import explain_term

class Editor(Gtk.Box):
    __gtype_name__ = 'Editor'

    def __init__(self, app):
        super(Editor, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.log = get_logger('Editor')
        self.app = app

        self.actions = WidgetActions(self.app)
        self.factory = WidgetFactory(self.app)
        self.current_topic = 'ALL'
        self.current_subtopic = 'ALL'
        self.current_postag = 'ALL'
        self.selected = []
        self.selected_tokens = []

        self._build_editor()
        self._update_editor()


    def _build_editor(self):
        self.set_margin_top(margin=6)
        self.set_margin_end(margin=6)
        self.set_margin_bottom(margin=6)
        self.set_margin_start(margin=6)

        # Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        self.btnAdd = self.factory.create_button('list-add-symbolic', 'Add document', self._add_document)
        toolbox.append(self.btnAdd)
        self.append(toolbox)

        # Content View
        editor = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        editor.set_margin_top(margin=6)

        ## Wdigets distribution
        self.boxLeft = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.boxLeft.set_margin_end(margin=6)
        self.boxRight = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.boxRight.set_margin_start(margin=6)
        self.hpaned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.hpaned.set_start_child(self.boxLeft)
        self.hpaned.set_end_child(self.boxRight)
        editor.append(self.hpaned)

        self.cvfiles = ColumnViewFiles(self.app)
        selection = self.cvfiles.get_selection()
        selection.connect('selection-changed', self._on_file_selected)
        self.boxLeft.append(self.cvfiles)

        self.append(editor)

    def _on_file_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            filename = model.get_item(pos)
            self.log.info("%s > %s", filename.id, filename.title)


    def _add_document(self, *args):
        self.log.debug(args)

    def _update_editor(self):
        source, target = ENV['Projects']['Default']['Languages']
        self.log.debug("%s > %s", source, target)
        files = get_inputs(source, target)
        self.log.debug(files)
        items = []
        for filepath in files:
            title = os.path.basename(filepath)
            items.append(Filepath(id=filepath, title=title))
        self.cvfiles.update(items)
