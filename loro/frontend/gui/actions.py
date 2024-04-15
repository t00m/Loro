#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: actions.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: App actions
"""

import os
import time
from gettext import gettext as _

from gi.repository import Adw
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import get_project_target_workbook_dir
from loro.backend.core.run_async import RunAsync
from loro.frontend.gui.widgets.editor import Editor
from loro.frontend.gui.models import Workbook

class WidgetActions(GObject.GObject):
    def __init__(self, app):
        self.log = get_logger('Actions')
        self.app = app

    def document_display(self, doc):
        self.log.debug("Displaying %s", doc)
        self.util.filename_display(doc)

    def document_open_location(self, item):
        self.log.debug("Open file location for %s", item.id)
        self.util.filename_open_location(item.id)

    def dropdown_populate(self, dropdown, item, data):
        model_filter = dropdown.get_model()
        model_sort = model_filter.get_model()
        model = model_sort.get_model()
        model.remove_all()

        for key, value in data:
            model.append(item(id=key, title=value))

    def workbook_create(self, *args):
        def _confirm(_, res, entry):
            if res == "cancel":
                return
            name = entry.get_text()
            # ~ self.log.debug("Accepted workbook name: %s", name)
            self.app.workbooks.add(name)
            # ~ window = self.app.get_widget('window')
            # ~ window.emit('workbooks-updated')
            self.update_dropdown_workbooks()

        def _allow(entry, gparam, dialog):
            name = entry.get_text()
            exists = self.app.workbooks.exists(name)
            dialog.set_response_enabled("add", not exists)

        window = self.app.get_widget('window')
        vbox = self.app.factory.create_box_vertical(margin=6, spacing=6)
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

    def workbook_delete(self, *args):
        #FIXME: Require confirmation
        self.log.debug("Deleting workbook")
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook.id is not None:
            self.app.workbooks.delete(workbook.id)
            # ~ window = self.app.get_widget('window')
            # ~ window.emit('workbooks-updated')
            self.update_dropdown_workbooks()

    def workbook_translate(self, *args):
        notebook = self.app.get_widget('notebook')
        translator = self.app.get_widget('translator')
        translator.update()
        notebook.set_current_page(3)
        return

    def workbook_summary(self, *args):
        notebook = self.app.get_widget('notebook')
        notebook.set_current_page(0)

    def workbook_study(self, *args):
        notebook = self.app.get_widget('notebook')
        notebook.set_current_page(1)

    def workbook_edit(self, *args):
        notebook = self.app.get_widget('notebook')
        editor = self.app.get_widget('editor')
        editor.update()
        notebook.set_current_page(2)
        return


        def _confirm(_, res, entry, old_name):
            if res == "cancel":
                return
            # ~ window = self.app.get_widget('window')
            new_name = entry.get_text()
            # ~ self.log.debug("Accepted workbook name: %s", new_name)
            self.app.workbooks.rename(old_name, new_name)
            self.update_dropdown_workbooks()
            # ~ window.emit('workbooks-updated')

        def _allow(entry, gparam, dialog):
            name = entry.get_text()
            exists = self.app.workbooks.exists(name)
            # ~ dialog.set_response_enabled("rename", not exists)
            dialog.set_response_enabled("save", True)

        window = self.app.get_widget('window')
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook.id is None:
            return

        vbox = self.app.factory.create_box_vertical(margin=3, spacing=3, hexpand=True, vexpand=True)
        cbox = Gtk.CenterBox()
        cbox.set_hexpand(True)
        hbox_name = self.app.factory.create_box_horizontal(margin=3, spacing=3, hexpand=True, vexpand=False)
        lblWBName = Gtk.Label()
        lblWBName.set_markup('<b>Name </b>')
        etyWBName = Gtk.Entry()
        etyWBName.set_text(workbook.id)
        old_name = workbook.id
        hbox_name.append(lblWBName)
        hbox_name.append(etyWBName)
        cbox.set_center_widget(hbox_name)
        vbox.append(cbox)
        editor = Editor(self.app)
        editor.update()
        vbox.append(editor)
        dialog = Adw.MessageDialog(
            transient_for=window,
            hide_on_close=True,
            heading=_("Edit workbook"),
            default_response="save",
            close_response="cancel",
            extra_child=vbox,
        )
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("save", _("Save changes"))
        dialog.set_response_enabled("save", True)
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
        dialog.connect("response", _confirm, etyWBName, old_name)
        etyWBName.connect("notify::text", _allow, dialog)
        dialog.set_default_size(1024, 728)
        dialog.present()

    def workbook_compile(self, *args):
        def start_workflow(*args):
            ddWorkbooks = self.app.get_widget('dropdown-workbooks')
            workbook = ddWorkbooks.get_selected_item()
            if workbook is None:
                return
            self.log.debug("Workbook['%s'] update requested", workbook.id)
            viewstack = self.app.get_widget('dashboard-viewstack')
            viewstack.set_visible_child_name('wb-progressbar')
            files = self.app.workbooks.get_files(workbook.id)
            self.app.workflow.start(workbook.id, files)
            self.app.report.build_pdf(workbook.id)

        def pulse():
            progressbar = self.app.get_widget('progressbar')

            while True:
                time.sleep(0.250)
                filename, fraction = self.app.workflow.get_progress()
                running = fraction > 0.0
                if running:
                    progressbar.set_fraction(fraction)
                    progressbar.set_text(filename)
                else:
                    progressbar.set_fraction(0.0)

                if not self.app.workflow.running:
                    break;
            return False

        RunAsync(start_workflow)
        RunAsync(pulse)

    def report_display(self, *args):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook.id is None:
            self.log.warning("No workbooks available")
            return
        DIR_OUTPUT = get_project_target_workbook_dir(workbook.id)
        report_url = os.path.join(DIR_OUTPUT, '%s.html' % workbook.id)
        report_url = self.app.report.get_url(workbook.id)
        if not os.path.exists(report_url):
            self.app.report.build(workbook.id)
        browser = self.app.get_widget('browser')
        browser.load_url(report_url)

    def update_dropdown_workbooks(self, *args):
        workbooks = self.app.workbooks.get_all()
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        toolbar = self.app.get_widget('window-toolbar')
        data = []
        wbnames = workbooks.keys()
        if len(wbnames) == 0:
            ddWorkbooks.set_visible(False)
            toolbar.set_visible(False)
            data.append((None, 'No workbooks available'))
        else:
            ddWorkbooks.set_visible(True)
            toolbar.set_visible(True)
            for workbook in wbnames:
                data.append((workbook, "Workbook %s" % workbook))
        self.app.actions.dropdown_populate(ddWorkbooks, Workbook, data)

    def workbook_get_current(self, *args):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        return ddWorkbooks.get_selected_item()

