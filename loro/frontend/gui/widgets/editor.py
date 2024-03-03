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
from loro.backend.core.util import get_metadata_from_filepath
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
        self.selected_file = None
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
        self.btnAdd = self.factory.create_button(icon_name='document-new-symbolic', tooltip='Add new document', callback=self._add_document)
        self.btnImport= self.factory.create_button(icon_name='list-add-symbolic', tooltip='Import docs', callback=self._import_document)
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.btnDelete = self.factory.create_button(icon_name='edit-delete-symbolic', tooltip='Delete doc', callback=self._delete_document)
        expander = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        self.btnRefresh = self.factory.create_button(icon_name='view-refresh-symbolic', tooltip='Refresh', callback=self._update_editor)
        toolbox.append(self.btnAdd)
        toolbox.append(self.btnImport)
        toolbox.append(separator)
        toolbox.append(self.btnDelete)
        toolbox.append(expander)
        toolbox.append(self.btnRefresh)
        self.boxLeft.append(toolbox)

        ### Files view
        self.cvfiles = ColumnViewFiles(self.app)
        self.cvfiles.set_single_selection()
        self.cvfiles.get_style_context().add_class(class_name='monospace')
        selection = self.cvfiles.get_selection()
        selection.connect('selection-changed', self._on_file_selected)
        self.boxLeft.append(self.cvfiles)

        ## Right: Editor view
        ### Editor Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        toolbox.set_margin_bottom(margin=6)
        self.btnSave = self.factory.create_button(icon_name='document-save-symbolic', tooltip='Save changes', callback=self._save_document)
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
        self.boxRight.append(editorview)
        self.append(editor)

    def _on_file_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            filename = model.get_item(pos)
            self.log.debug("File selected: %s", filename.title)
            text = open(filename.id).read()
            self.buffer.set_text(text)
            self.selected_file = filename.id

    def _add_document(self, *args):
        self.log.debug(args)

    def _import_document(self, *args):
        self.log.debug(args)

    def _delete_document(self, *args):
        self.log.debug(args)

    def _save_document(self, *args):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        with open(self.selected_file, 'w') as fsel:
            text = self.buffer.get_text(start, end, False)
            fsel.write(text)
            self.log.info("File '%s' saved", os.path.basename(self.selected_file))

    def _update_editor(self, *args):
        source, target = ENV['Projects']['Default']['Languages']
        files = get_inputs(source, target)
        items = []
        for filepath in files:
            topic, subtopic = get_metadata_from_filepath(filepath)
            title = os.path.basename(filepath)
            items.append(Filepath(
                                id=filepath,
                                title=title,
                                topic=topic.title(),
                                subtopic=subtopic.title()
                            )
                        )
        self.cvfiles.update(items)
