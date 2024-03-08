#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os

import gi

from gi.repository import Gio, GObject, Adw, Gtk  # type:ignore

from loro.frontend.gui.factory import WidgetFactory
from loro.frontend.gui.actions import WidgetActions
from loro.frontend.gui.models import Filepath, Workbook
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.widgets.views import ColumnViewFiles
from loro.frontend.gui.icons import ICON
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.core.util import get_inputs
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_metadata_from_filename
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.log import get_logger
from loro.backend.services.nlp.spacy import explain_term

class Editor(Gtk.Box):
    __gtype_name__ = 'Editor'

    def __init__(self, app):
        super(Editor, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.log = get_logger('Editor')
        self.app = app
        self.window = self.app.get_main_window()
        self.actions = WidgetActions(self.app)
        self.factory = WidgetFactory(self.app)
        self.selected_file = None
        GObject.signal_new('workbooks-updated', Editor, GObject.SignalFlags.RUN_LAST, None, () )
        GObject.signal_new('filenames-updated', Editor, GObject.SignalFlags.RUN_LAST, None, () )
        self._build_editor()
        self._update_editor()
        self._enable_renaming(False)
        self._enable_deleting(False)

    def _enable_renaming(self, enabled):
        self.btnRename.set_sensitive(enabled)

    def _enable_deleting(self, enabled):
        self.btnDelete.set_sensitive(enabled)

    def _build_editor(self):
        self.set_margin_top(margin=6)
        self.set_margin_end(margin=6)
        self.set_margin_bottom(margin=6)
        self.set_margin_start(margin=6)

        # Content View
        editor = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        editor.set_margin_top(margin=6)

        ## Wdigets distribution
        self.boxLeft = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True)
        self.boxLeft.set_margin_end(margin=6)
        self.boxRight = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.boxRight.set_margin_start(margin=6)
        self.hpaned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.hpaned.set_start_child(self.boxLeft)
        self.hpaned.set_end_child(self.boxRight)
        self.hpaned.set_position(450)
        self.hpaned.set_resize_start_child(False)
        editor.append(self.hpaned)

        ## Left: Files view & Workbooks management
        ### Workbooks
        hbox = self.factory.create_box_horizontal(spacing=6, margin=6, vexpand=False, hexpand=True)
        self.ddWorkbooks = self.factory.create_dropdown_generic(Workbook, enable_search=True)
        self.ddWorkbooks.connect("notify::selected-item", self._on_workbook_selected)
        self.ddWorkbooks.set_hexpand(False)
        hbox.append(self.ddWorkbooks)
        expander = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        self.btnWBAdd = self.factory.create_button(icon_name=ICON['DOC_NEW'], tooltip='Add a new workbook', callback=self._add_workbook)
        self.btnWBEdit = self.factory.create_button(icon_name=ICON['DOC_EDIT'], tooltip='Edit workbook name', callback=self._edit_workbook)
        self.btnWBDel = self.factory.create_button(icon_name=ICON['DOC_DELETE'], tooltip='Delete selected workbook', callback=self._delete_workbook)
        hbox.append(expander)
        hbox.append(self.btnWBAdd)
        hbox.append(self.btnWBEdit)
        hbox.append(self.btnWBDel)
        self.boxLeft.append(hbox)

        ### Files Toolbox
        vbox = self.factory.create_box_horizontal(spacing=6, margin=6, vexpand=True, hexpand=False)
        toolbox = self.factory.create_box_vertical()
        toolbox.set_margin_bottom(margin=6)
        self.btnAdd = self.factory.create_button(icon_name=ICON['DOC_NEW'], tooltip='Add new document', callback=self._add_document)
        self.btnRename = self.factory.create_button(icon_name=ICON['DOC_EDIT'], tooltip='Rename document', callback=self._rename_document)
        self.btnImport= self.factory.create_button(icon_name=ICON['DOC_DELETE'], tooltip='Import docs', callback=self._import_document)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.btnDelete = self.factory.create_button(icon_name=ICON['TRASH'], tooltip='Delete doc', callback=self._delete_document)
        expander = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        self.btnRefresh = self.factory.create_button(icon_name=ICON['REFRESH'], tooltip='Refresh', callback=self._update_editor)
        toolbox.append(self.btnAdd)
        toolbox.append(self.btnRename)
        toolbox.append(self.btnImport)
        toolbox.append(separator)
        toolbox.append(self.btnDelete)
        toolbox.append(expander)
        toolbox.append(self.btnRefresh)
        vbox.append(toolbox)

        ### Files view
        self.cvfiles = ColumnViewFiles(self.app)
        self.cvfiles.set_single_selection()
        self.cvfiles.set_toggle_button_callback(self._filename_toggled)
        self.cvfiles.get_style_context().add_class(class_name='monospace')
        self.cvfiles.set_hexpand(True)
        self.cvfiles.set_vexpand(True)
        selection = self.cvfiles.get_selection()
        selection.connect('selection-changed', self._on_file_selected)
        vbox.append(self.cvfiles)
        self.boxLeft.append(vbox)

        ## Right: Editor view
        ### Editor Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        toolbox.set_margin_bottom(margin=6)
        self.btnSave = self.factory.create_button(icon_name='document-save-symbolic', tooltip='Save changes', callback=self._save_document)
        toolbox.append(self.btnSave)
        self.boxRight.append(toolbox)

        ### Editor GtkSource
        scrwindow = Gtk.ScrolledWindow()
        self.editorview = self.factory.create_editor_view()
        scrwindow.set_child(self.editorview)
        self.boxRight.append(scrwindow)
        self.append(editor)

    def _filename_toggled(self, toggle_button, filepath):
        workbook = self.ddWorkbooks.get_selected_item()
        active = toggle_button.get_active()
        filename = os.path.basename(filepath.id)
        self.log.debug("File '%s' enabled for workbook '%s'? %s", filename, workbook.id, active)
        self.app.workbooks.update(workbook.id, filename, active)

    def _add_workbook(self, *args):
        def _confirm(_, res, entry):
            if res == "cancel":
                return
            name = entry.get_text()
            self.log.debug("Accepted workbook name: %s", name)
            self.app.workbooks.add(name)
            self._update_editor()
            self.emit('workbooks-updated')

        def _allow(entry, gparam, dialog):
            name = entry.get_text()
            exists = self.app.workbooks.exists(name)
            dialog.set_response_enabled("add", not exists)

        window = self.app.get_main_window()
        vbox = self.factory.create_box_vertical(margin=6, spacing=6)
        # ~ vbox.props.width_request = 600
        # ~ vbox.props.height_request = 480
        etyWBName = Gtk.Entry()
        etyWBName.set_placeholder_text('Type the workbook name...')
        vbox.append(etyWBName)
        dialog = Adw.MessageDialog(
            transient_for=window,
            hide_on_close=True,
            heading=_("Add new workbook"),
            default_response="add",
            close_response="cancel",
            extra_child=vbox,
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("add", _("Add"))
        dialog.set_response_enabled("add", False)
        dialog.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)
        dialog.connect("response", _confirm, etyWBName)
        etyWBName.connect("notify::text", _allow, dialog)
        dialog.present()

    def _edit_workbook(self, *args):
        def _confirm(_, res, entry, old_name):
            if res == "cancel":
                return
            new_name = entry.get_text()
            self.log.debug("Accepted workbook name: %s", new_name)
            self.app.workbooks.rename(old_name, new_name)
            self._update_editor()
            self.emit('workbooks-updated')

        def _allow(entry, gparam, dialog):
            name = entry.get_text()
            exists = self.app.workbooks.exists(name)
            dialog.set_response_enabled("rename", not exists)

        workbook = self.ddWorkbooks.get_selected_item()
        if workbook is None:
            return

        window = self.app.get_main_window()
        vbox = self.factory.create_box_vertical(margin=6, spacing=6)
        etyWBName = Gtk.Entry()
        etyWBName.set_text(workbook.id)
        old_name = workbook.id
        vbox.append(etyWBName)
        dialog = Adw.MessageDialog(
            transient_for=window,
            hide_on_close=True,
            heading=_("Rename workbook"),
            default_response="rename",
            close_response="cancel",
            extra_child=vbox,
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("rename", _("Rename"))
        dialog.set_response_enabled("rename", False)
        dialog.set_response_appearance("rename", Adw.ResponseAppearance.SUGGESTED)
        dialog.connect("response", _confirm, etyWBName, old_name)
        etyWBName.connect("notify::text", _allow, dialog)
        dialog.present()

    def _delete_workbook(self, *args):
        workbook = self.ddWorkbooks.get_selected_item()
        if workbook is not None:
            self.app.workbooks.delete(workbook.id)
            self._update_editor()
            self.emit('workbooks-updated')

    def _on_file_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            filename = model.get_item(pos)
            self.selected_file = filename.id
            self.log.debug("File selected: %s", filename.title)
            self.display_file(filename.id)
            self._enable_renaming(True)
            self._enable_deleting(True)

    def display_file(self, filename: str):
        text = open(filename).read()
        textbuffer = self.editorview.get_buffer()
        textbuffer.set_text(text)

    def _on_workbook_selected(self, dropdown, gparam):
        workbook = dropdown.get_selected_item()
        if workbook is not None:
            self.log.debug("Selected workbook: %s", workbook.id)
            if workbook.id == 'None':
                self.cvfiles.set_column_belongs_visible(False)
            else:
                self.cvfiles.set_column_belongs_visible(True)
                self._update_files_view(workbook.id)

    def _update_files_view(self, wbname: str):
        # Update files
        source, target = ENV['Projects']['Default']['Languages']
        files = get_inputs(source)
        items = []
        for filepath in files:
            topic, subtopic, suffix = get_metadata_from_filepath(filepath)
            title = os.path.basename(filepath)
            if wbname == 'None':
                belongs = False
            else:
                belongs = self.app.workbooks.have_file(wbname, title)
            items.append(Filepath(
                                id=filepath,
                                title=title,
                                topic=topic.title(),
                                subtopic=subtopic.title(),
                                suffix=suffix,
                                belongs=belongs
                            )
                        )
        self.cvfiles.update(items)
        if len(files) > 0:
            selection = self.cvfiles.get_selection()
            selection.select_item(0, True)
            filename = selection.get_selected_item()
            self.log.debug("File selected: %s", filename.title)
            self.display_file(filename.id)

    def _add_document(self, *args):
        def _update_filename(_, gparam, data):
            enabled = False
            dialog, label, etyt, etys, etyu = data
            topic = etyt.get_text().upper()
            subtopic = etys.get_text().upper()
            suffix = etyu.get_text().upper()
            label.set_text("%s-%s_%s.txt" % (topic, subtopic, suffix))
            if len(topic) > 1 and len(subtopic) > 1 and len(suffix) > 0:
                enabled = True
            dialog.set_response_enabled("add", enabled)
            # ~ self.log.debug("Document name: %s -> %s", label.get_text(), enabled)

        def _confirm(_, res, lblFilename, editorview):
            if res == "cancel":
                return
            workbook = self.ddWorkbooks.get_selected_item()
            filename = lblFilename.get_text()
            textbuffer = editorview.get_buffer()
            start = textbuffer.get_start_iter()
            end = textbuffer.get_end_iter()
            contents = textbuffer.get_text(start, end, False)
            source, target = ENV['Projects']['Default']['Languages']
            input_dir = get_project_input_dir(source)
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'w') as fout:
                fout.write(contents)
                self.log.debug("Document '%s' created", filename)
                self._update_files_view(workbook.id)
            # ~ topic, subtopic, suffix = get_metadata_from_filename(filename)
            return filename

        window = self.app.get_main_window()
        vbox = self.factory.create_box_vertical(margin=6, spacing=6)
        vbox.props.width_request = 800
        vbox.props.height_request = 600
        workbooks = self.app.workbooks.get_all()
        topics = set()
        for wbname in workbooks:
            dictionary = self.app.workbooks.get_dictionary(wbname)
            for topic in dictionary.get_topics():
                topics.add(topic)
        # ~ topics = list(self.app.dictionary.get_topics().keys())
        subtopics = []
        suffixes = []

        dialog = Adw.MessageDialog(
            transient_for=window,
            hide_on_close=True,
            heading=_("Add new document"),
            default_response="add",
            close_response="cancel",
            extra_child=vbox,
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("add", _("Add"))
        dialog.set_response_enabled("add", False)
        dialog.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)
        hbox = self.factory.create_box_horizontal(margin=6, spacing=6, hexpand=True)
        cmbTopic = self.factory.create_combobox_with_entry(_("Topic"), topics)
        cmbSubtopic = self.factory.create_combobox_with_entry(_("Subopic"), subtopics)
        cmbSuffix = self.factory.create_combobox_with_entry(_("Suffix / Sequence / etc..."), suffixes)
        etyTopic = cmbTopic.get_child()
        etySubtopic = cmbSubtopic.get_child()
        etySuffix = cmbSuffix.get_child()
        lblFilename = Gtk.Label()
        lblFilename.set_selectable(True)
        scrwindow = Gtk.ScrolledWindow()
        editorview = self.factory.create_editor_view()
        scrwindow.set_child(editorview)
        data = (dialog, lblFilename, etyTopic, etySubtopic, etySuffix)
        etyTopic.connect("notify::text", _update_filename, data)
        etySubtopic.connect("notify::text", _update_filename, data)
        etySuffix.connect("notify::text", _update_filename, data)
        hbox.append(cmbTopic)
        hbox.append(cmbSubtopic)
        hbox.append(cmbSuffix)
        vbox.append(hbox)
        vbox.append(lblFilename)
        vbox.append(scrwindow)
        dialog.connect("response", _confirm, lblFilename, editorview)
        dialog.present()

    def _rename_document(self, *args):
        def _update_filename(_, gparam, data):
            enabled = False
            dialog, label, etyt, etys, etyu = data
            topic = etyt.get_text().upper()
            subtopic = etys.get_text().upper()
            suffix = etyu.get_text().upper()
            label.set_text("%s-%s_%s.txt" % (topic, subtopic, suffix))
            if len(topic) > 1 and len(subtopic) > 1 and len(suffix) > 0:
                enabled = True
            dialog.set_response_enabled("add", enabled)
            # ~ self.log.debug("Document name: %s -> %s", label.get_text(), enabled)

        def _confirm(_, res, lblFilename):
            if res == "cancel":
                return
            filename = lblFilename.get_text()
            self.log.debug("Accepted document name: %s", filename)
            # ~ topic, subtopic, suffix = get_metadata_from_filename(filename)
            return filename

        window = self.app.get_main_window()
        vbox = self.factory.create_box_vertical(margin=6, spacing=6)
        vbox.props.width_request = 800
        # ~ vbox.props.height_request = 600
        # ~ topics = list(self.app.dictionary.get_topics().keys())
        topics = []
        subtopics = []
        suffixes = []

        dialog = Adw.MessageDialog(
            transient_for=window,
            hide_on_close=True,
            heading=_("Rename selected document"),
            default_response="add",
            close_response="cancel",
            extra_child=vbox,
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("add", _("Add"))
        dialog.set_response_enabled("add", False)
        dialog.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)
        hbox = self.factory.create_box_horizontal(margin=6, spacing=6, hexpand=True)
        cmbTopic = self.factory.create_combobox_with_entry(_("Topic"), topics)
        cmbSubtopic = self.factory.create_combobox_with_entry(_("Subopic"), subtopics)
        cmbSuffix = self.factory.create_combobox_with_entry(_("Suffix / Sequence / etc..."), suffixes)
        etyTopic = cmbTopic.get_child()
        etySubtopic = cmbSubtopic.get_child()
        etySuffix = cmbSuffix.get_child()
        lblFilename = Gtk.Label()
        lblFilename.set_selectable(True)
        data = (dialog, lblFilename, etyTopic, etySubtopic, etySuffix)
        etyTopic.connect("notify::text", _update_filename, data)
        etySubtopic.connect("notify::text", _update_filename, data)
        etySuffix.connect("notify::text", _update_filename, data)
        hbox.append(cmbTopic)
        hbox.append(cmbSubtopic)
        hbox.append(cmbSuffix)
        vbox.append(hbox)
        vbox.append(lblFilename)
        dialog.connect("response", _confirm, lblFilename)
        dialog.present()

    def _import_document(self, *args):
        self.log.debug(args)

    def _delete_document(self, *args):
        self.log.debug(args)

    def _save_document(self, *args):
        textbuffer = self.editorview.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        with open(self.selected_file, 'w') as fsel:
            text = textbuffer.get_text(start, end, False)
            fsel.write(text)
            self.log.info("File '%s' saved", os.path.basename(self.selected_file))

    def _update_editor(self, *args):
        # Update workbooks
        workbooks = self.app.workbooks.get_all()
        items = []
        if len(workbooks) == 0:
            items.append(('None', 'No workbooks created yet'))
        else:
            items = []
            for workbook in workbooks:
                items.append((workbook, 'Workbook %s' % workbook))
        self.actions.dropdown_populate(self.ddWorkbooks, Workbook, items)
        self.ddWorkbooks.set_selected(0)



