#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File: wbeditor.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Workbook editor

import os
from gi.repository import Adw, Gtk  # type:ignore

from loro.backend.core.log import get_logger
from loro.frontend.gui.icons import ICON
from loro.frontend.gui.models import Filepath, Workbook
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.widgets.views import ColumnViewFilesAvailable
from loro.frontend.gui.widgets.views import ColumnViewFilesUsed
from loro.frontend.gui.icons import ICON
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.core.util import get_inputs
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_metadata_from_filename
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.selector import Selector
from loro.frontend.gui.widgets.filedialog import open_file_dialog
from loro.backend.core.util import get_default_languages
from loro.frontend.gui.widgets.toolbar import Toolbar

class WorkbookEditor(Gtk.Box):
    __gtype_name__ = 'WorkbookEditor'

    def __init__(self, app):
        super(WorkbookEditor, self).__init__(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        self.app = app
        self.log = get_logger(__class__.__name__)
        self.selected_file = None
        self._build_ui()

    def _build_ui(self):
        # Selector
        self.selector = Selector(app=self.app)
        self.selector.set_margin_bottom(margin=0)

        ### Left toolbox
        # ~ lefttlb = Toolbar(self.app, position='left')
        # ~ self.append(lefttlb)
        # ~ lefttlb.set_start_widget(self.app.factory.create_button(title='View'))
        # ~ lefttlb.set_start_widget(self.app.factory.create_button(title='Edit'))

        vboxLeftSidebar = self.app.factory.create_box_horizontal(spacing=6, margin=0, vexpand=True, hexpand=False)
        LeftSidebarToolbox = self.app.factory.create_box_vertical()
        LeftSidebarToolbox.set_margin_top(margin=6)
        self.btnHideAv = self.app.factory.create_button_toggle(icon_name='com.github.t00m.Loro-sidebar-show-left-symbolic', tooltip='Show/Hide available files', callback=self._on_toggle_views)
        self.btnHideAv.set_active(False)
        separator1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.button_r = self.app.factory.create_button(icon_name=ICON['WB_COMPILE'], tooltip='Refresh/Compile workbook', width=16, callback=self.app.actions.workbook_compile)
        self.app.add_widget('status-workbook-refresh', self.button_r)
        self.btnAdd = self.app.factory.create_button(icon_name=ICON['DOC_NEW'], width=16, tooltip='Add new document', callback=self._on_document_add)
        self.btnRename = self.app.factory.create_button(icon_name=ICON['DOC_EDIT'], width=16, tooltip='Rename document', callback=self._on_document_rename)
        self.btnImport= self.app.factory.create_button(icon_name=ICON['DOC_IMPORT'], width=16, tooltip='Import docs', callback=self._on_document_import)
        separator2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.btnDelete = self.app.factory.create_button(icon_name=ICON['TRASH'], width=16, tooltip='Delete doc', callback=self._on_document_delete)
        expander = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        LeftSidebarToolbox.append(self.btnHideAv)
        LeftSidebarToolbox.append(separator1)
        LeftSidebarToolbox.append(self.button_r)
        LeftSidebarToolbox.append(self.btnAdd)
        LeftSidebarToolbox.append(self.btnRename)
        LeftSidebarToolbox.append(self.btnImport)
        LeftSidebarToolbox.append(separator2)
        LeftSidebarToolbox.append(self.btnDelete)
        LeftSidebarToolbox.append(expander)
        vboxLeftSidebar.append(LeftSidebarToolbox)
        vboxLeftSidebar.append(Gtk.Separator())
        self.append(vboxLeftSidebar)

        self.selector.set_action_add_to_used(self._on_view_used_add)
        self.selector.set_action_remove_from_used(self._on_view_used_remove)
        self.cvfilesAv = ColumnViewFilesAvailable(self.app)
        self.cvfilesAv.set_single_selection()
        self.cvfilesAv.get_style_context().add_class(class_name='monospace')
        self.cvfilesAv.set_hexpand(True)
        self.cvfilesAv.set_vexpand(True)
        selection = self.cvfilesAv.get_selection()
        selection.connect('selection-changed', self._on_view_available_select_filename)
        self.selector.add_columnview_available(self.cvfilesAv)

        self.cvfilesUsed = ColumnViewFilesUsed(self.app)
        self.cvfilesUsed.set_single_selection()
        self.cvfilesUsed.get_style_context().add_class(class_name='monospace')
        self.cvfilesUsed.set_hexpand(True)
        self.cvfilesUsed.set_vexpand(True)
        selection = self.cvfilesUsed.get_selection()
        selection.connect('selection-changed', self._on_view_used_select_filename)
        self.selector.add_columnview_used(self.cvfilesUsed)
        self.append(self.selector)

        ## Right: Editor view/toolbar and right toolbar
        ### Editor Toolbox
        self.visor = self.app.factory.create_box_vertical(hexpand=True, vexpand=True)
        toolbox = self.app.factory.create_box_horizontal(spacing=6)
        self.btnSave = self.app.factory.create_button(icon_name='com.github.t00m.Loro-document-save-symbolic', width=16, tooltip='Save changes', callback=self._on_document_save)
        self.lblFileName = self.app.factory.create_label()
        toolbox.append(self.btnSave)
        toolbox.append(self.lblFileName)
        self.visor.append(toolbox)

        ### Editor GtkSource
        scrwindow = Gtk.ScrolledWindow()
        self.editorview = self.app.factory.create_editor_view()
        scrwindow.set_child(self.editorview)
        self.visor.append(scrwindow)
        self.append(self.visor)

        # Empty box (trick)
        self.boxnull = self.app.factory.create_box_vertical(hexpand=False, vexpand=True)
        self.boxnull.append(Gtk.Label.new(' '))
        self.append(self.boxnull)

        ### Rigth toolbox
        self.RightSidebarToolbox = self.app.factory.create_box_vertical(spacing=6, margin=0, vexpand=True, hexpand=False)
        self.RightSidebarToolbox.set_margin_top(margin=6)
        self.btnHideSourceEditor = self.app.factory.create_button_toggle(icon_name='com.github.t00m.Loro-sidebar-show-right-symbolic', tooltip='Show/Hide editor', callback=self._on_toggle_editor)
        self.btnHideSourceEditor.set_active(True)
        self.RightSidebarToolbox.append(self.btnHideSourceEditor)
        separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        self.RightSidebarToolbox.append(separator)
        self.append(self.RightSidebarToolbox)

        self._on_toggle_views(self.btnHideAv, None)

    def _set_enable_renaming(self, enabled):
        self.btnRename.set_sensitive(enabled)

    def _set_enable_deleting(self, enabled):
        self.btnDelete.set_sensitive(enabled)

    def _on_toggle_views(self, button, gparam):
        visible = button.get_active()
        self.selector.boxLeft.set_visible(visible)
        self.selector.set_hexpand(True)
        self.selector.boxControls.set_visible(visible)
        # ~ self.visor.set_visible(not visible)
        if not visible:
            self.selector.set_hexpand(False)
            self.boxnull.set_visible(True)
        else:
            self.selector.set_hexpand(True)
            self.boxnull.set_visible(False)

    def _on_toggle_editor(self, button, gparam):
        visible = button.get_active()
        self.visor.set_visible(visible)
        self.boxnull.set_hexpand(not visible)

    def _on_view_used_add(self, *args):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        filepath = self.cvfilesAv.get_item()
        filename = os.path.basename(filepath.id)
        self.app.workbooks.update(workbook.id, filename, True)
        self.log.debug("File '%s' enabled for workbook '%s'? %s", filename, workbook.id, True)
        self.update_files_view(workbook.id)

    def _on_view_used_remove(self, *args):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        filepath = self.cvfilesUsed.get_item()
        filename = os.path.basename(filepath.id)
        self.app.workbooks.update(workbook.id, filename, False)
        self.log.debug("File '%s' enabled for workbook '%s'? %s", filename, workbook.id, False)
        self.update_files_view(workbook.id)

    def _on_view_available_select_filename(self, selection, position, n_items):
        model = self.cvfilesAv.get_model_filter()
        # ~ model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            filename = model.get_item(pos)
            self.selected_file = filename.id
            # ~ self.log.debug("Selected available: '%s'", self.selected_file)
            # ~ self.log.debug("File available selected: %s", filename.title)
            self._on_display_file(filename.id)
            # ~ self._set_enable_renaming(True)
            # ~ self._set_enable_deleting(True)

    def _on_view_used_select_filename(self, selection, position, n_items):
        model = self.cvfilesUsed.get_model_filter()
        # ~ model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            filename = model.get_item(pos)
            self.selected_file = filename.id
            # ~ self.log.debug("Selected used: '%s'", self.selected_file)
            # ~ self.log.debug("File used selected: %s", filename.title)
            self._on_display_file(filename.id)
            # ~ self._set_enable_renaming(True)
            # ~ self._set_enable_deleting(True)

    def _on_display_file(self, filename: str):
        text = open(filename).read()
        textbuffer = self.editorview.get_buffer()
        textbuffer.set_text(text)
        basename = os.path.basename(filename)
        self.lblFileName.set_markup(basename)
        self.lblFileName.get_style_context().add_class(class_name='caption')

    # ~ def _on_workbook_selected(self, dropdown):
        # ~ workbook = dropdown.get_selected_item()
        # ~ if workbook is None:
            # ~ return
        # ~ self.current_workbook = workbook.id
        # ~ if workbook is not None:
            # ~ self.log.debug("Selected workbook: %s", workbook.id)
            # ~ if workbook.id != 'None':
                # ~ self.update_files_view(workbook.id)
                # ~ self.cvfilesUsed.set_title("On workbook %s" % workbook.id)

    def update_files_view(self, wbname: str):
        # Update files
        source, target = get_default_languages()
        files = get_inputs()
        itemsAv = []
        itemsUsed = []
        for filepath in files:
            topic, subtopic, suffix = get_metadata_from_filepath(filepath)
            title = os.path.basename(filepath)
            if wbname == 'None':
                belongs = False
            else:
                belongs = self.app.workbooks.have_file(wbname, title)
            item = Filepath(id=filepath, title=title)
            itemsAv.append(item)
            if belongs:
                itemsUsed.append(item)
        self.cvfilesAv.update(itemsAv)
        self.cvfilesUsed.update(itemsUsed)
        if len(files) > 0:
            selection = self.cvfilesAv.get_selection()
            selection.select_item(0, True)
            filename = selection.get_selected_item()
            self.selected_file = filename.id
            # ~ self.log.debug("File selected: %s", filename.title)
            self._on_display_file(filename.id)

    def _on_document_add(self, *args):
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
            ddWorkbooks = self.app.get_widget('dropdown-workbooks')
            workbook = ddWorkbooks.get_selected_item()
            filename = lblFilename.get_text()
            textbuffer = editorview.get_buffer()
            start = textbuffer.get_start_iter()
            end = textbuffer.get_end_iter()
            contents = textbuffer.get_text(start, end, False)
            source, target = get_default_languages()
            filepath = os.path.join(get_project_input_dir(), filename)
            with open(filepath, 'w') as fout:
                fout.write(contents)
                self.log.info("Document '%s' created", filename)
                self.update()
            return filename

        window = self.app.get_widget('window')
        vbox = self.app.factory.create_box_vertical(margin=6, spacing=6)
        vbox.props.width_request = 800
        vbox.props.height_request = 600
        workbooks = self.app.workbooks.get_all()
        topics = set()
        subtopics = set()
        for wbname in workbooks:
            for topic in self.app.cache.get_topics(wbname):
                topics.add(topic)
            for subtopic in self.app.cache.get_subtopics(wbname):
                subtopics.add(subtopic)
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
        hbox = self.app.factory.create_box_horizontal(margin=6, spacing=6, hexpand=True)
        cmbTopic = self.app.factory.create_combobox_with_entry(_("Topic"), topics)
        cmbSubtopic = self.app.factory.create_combobox_with_entry(_("Subopic"), subtopics)
        cmbSuffix = self.app.factory.create_combobox_with_entry(_("Suffix / Sequence / etc..."), suffixes)
        etyTopic = cmbTopic.get_child()
        etySubtopic = cmbSubtopic.get_child()
        etySuffix = cmbSuffix.get_child()
        lblFilename = Gtk.Label()
        lblFilename.set_selectable(True)
        scrwindow = Gtk.ScrolledWindow()
        editorview = self.app.factory.create_editor_view()
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

    def _on_document_rename(self, *args):
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

        def _confirm(_, res, old_name, lblFilename):
            # FIXME: document should be renamed also in worbooks
            if res == "cancel":
                return

            source_path = os.path.join(get_project_input_dir(), old_name)
            new_name = lblFilename.get_text()
            target_path = os.path.join(get_project_input_dir(), new_name)
            shutil.move(source_path, target_path)
            # ~ self.log.debug("Document renamed from '%s' to '%s'", os.path.basename(source_path), os.path.basename(target_path))
            self.update_files_view(self.current_workbook)

            return new_name

        if self.selected_file is None:
            return

        window = self.app.get_widget('window')
        basename = os.path.basename(self.selected_file)
        vbox = self.app.factory.create_box_vertical(margin=6, spacing=6)
        vbox.props.width_request = 800

        workbooks = self.app.workbooks.get_all()
        topics = set()
        subtopics = set()
        for wbname in workbooks:
            for topic in self.app.cache.get_topics(wbname):
                topics.add(topic)
            for subtopic in self.app.cache.get_subtopics(wbname):
                subtopics.add(subtopic)
        suffixes = []

        dialog = Adw.MessageDialog(
            transient_for=window,
            hide_on_close=True,
            heading=_("Rename %s" % basename),
            default_response="add",
            close_response="cancel",
            extra_child=vbox,
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("add", _("Add"))
        dialog.set_response_enabled("add", False)
        dialog.set_response_appearance("add", Adw.ResponseAppearance.SUGGESTED)
        hbox = self.app.factory.create_box_horizontal(margin=6, spacing=6, hexpand=True)
        cmbTopic = self.app.factory.create_combobox_with_entry(_("Topic"), topics)
        cmbSubtopic = self.app.factory.create_combobox_with_entry(_("Subopic"), subtopics)
        cmbSuffix = self.app.factory.create_combobox_with_entry(_("Suffix / Sequence / etc..."), suffixes)
        etyTopic = cmbTopic.get_child()
        etySubtopic = cmbSubtopic.get_child()
        etySuffix = cmbSuffix.get_child()

        topic, subtopic, suffix = get_metadata_from_filepath(self.selected_file)
        etyTopic.set_text(topic)
        etySubtopic.set_text(subtopic)
        etySuffix.set_text(suffix)

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
        dialog.connect("response", _confirm, self.selected_file, lblFilename)
        dialog.present()

    def _on_document_import(self, *args):
        os.system("xdg-open '%s'" % get_project_input_dir())
        # ~ self.log.debug("Open Input directory")

    def _on_document_delete(self, *args):
        pass
        # FIXME: Check if it exists in Workbooks, delete it from them
        # and then, delete it from disk
        # ~ self.log.debug(args)

    def _on_document_save(self, *args):
        textbuffer = self.editorview.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        with open(self.selected_file, 'w') as fsel:
            text = textbuffer.get_text(start, end, False)
            fsel.write(text)
            self.log.info("File '%s' saved", os.path.basename(self.selected_file))
