#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os

import gi
gi.require_version('GtkSource', '5')
from gi.repository import Gio, Adw, Gtk, GtkSource  # type:ignore

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
        self.hpaned.set_position(400)
        self.hpaned.set_resize_start_child(False)
        editor.append(self.hpaned)

        ## Left: Files view

        ### Files Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        toolbox.set_margin_bottom(margin=6)
        self.btnAdd = self.factory.create_button('document-new-symbolic', 'Add doc', self._add_document)
        self.btnImport= self.factory.create_button('list-add-symbolic', 'Import docs', self._import_document)
        self.btnDelete = self.factory.create_button('edit-delete-symbolic', 'Delete doc', self._delete_document)
        toolbox.append(self.btnAdd)
        toolbox.append(self.btnImport)
        toolbox.append(self.btnDelete)
        self.boxLeft.append(toolbox)

        ### Files view
        self.cvfiles = ColumnViewFiles(self.app)
        selection = self.cvfiles.get_selection()
        selection.connect('selection-changed', self._on_file_selected)
        self.boxLeft.append(self.cvfiles)

        ## Right: Editor view
        ### Editor Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        toolbox.set_margin_bottom(margin=6)
        self.btnSave = self.factory.create_button('document-save-symbolic', 'Save changes', self._save_document)
        toolbox.append(self.btnSave)
        self.boxRight.append(toolbox)

        ### Editor GtkSource
        editorview = GtkSource.View(
            height_request=-1,
            top_margin=12,
            bottom_margin=12,
            left_margin=12,
            right_margin=12,
            wrap_mode=3,
            show_line_numbers=True,
            show_line_marks=True,
            show_right_margin=True,
            css_classes=["card"],
        )
        editorview.set_background_pattern(GtkSource.BackgroundPatternType.GRID)
        editorview.set_monospace(True)
        self.buffer = editorview.get_buffer()
        editorview.set_vexpand(True)

        # ~ # Save button
        # ~ self.notes_save_btn: Gtk.Button = Gtk.Button(
            # ~ icon_name="emblems-documents-symbolic",
            # ~ css_classes=["circular", "suggested-action"],
            # ~ halign=Gtk.Align.END,
            # ~ valign=Gtk.Align.END,
            # ~ margin_bottom=6,
            # ~ margin_end=6,
            # ~ tooltip_text=_("Save"),
            # ~ visible=False,
        # ~ )
        # ~ self.notes_save_btn.connect("clicked", lambda *_: self._update_editor())


        self.boxRight.append(editorview)

        self.append(editor)

    def _on_file_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            filename = model.get_item(pos)
            self.log.info("%s > %s", filename.id, filename.title)
            text = open(filename.id).read()
            self.buffer.set_text(text)


    def _add_document(self, *args):
        self.log.debug(args)

    def _import_document(self, *args):
        self.log.debug(args)

    def _delete_document(self, *args):
        self.log.debug(args)

    def _save_document(self, *args):
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
