#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import time
import threading
from gi.repository import Gio, Adw, GLib, Gtk  # type:ignore

from loro.backend.core.run_async import RunAsync
# ~ from loro.frontend.gui.models import Item, Topic, Subtopic, POSTag, Token, Sentence, Analysis, Workbook
# ~ from loro.frontend.gui.widgets.columnview import ColumnView
# ~ from loro.frontend.gui.widgets.views import ColumnViewToken
# ~ from loro.frontend.gui.widgets.views import ColumnViewSentences
# ~ from loro.frontend.gui.widgets.views import ColumnViewAnalysis
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.core.util import find_item
from loro.backend.core.log import get_logger
# ~ from loro.backend.services.nlp.spacy import explain_term
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_project_target_dir
from loro.backend.core.util import get_project_target_workbook_dir
from loro.frontend.gui.icons import ICON
from loro.frontend.gui.widgets.status import StatusPageNoWorkbooks
from loro.frontend.gui.widgets.status import StatusPageEmpty
from loro.frontend.gui.widgets.status import StatusPageCurrentWorkbook

from loro.frontend.gui.icons import ICON

class Dashboard(Gtk.Box):
    __gtype_name__ = 'Dashboard'

    def __init__(self, app):
        super(Dashboard, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.log = get_logger('Dashboard')
        self.app = app
        self._build_dashboard()
        GLib.timeout_add(interval=500, function=self.update_dashboard)

    def _build_dashboard(self):
        viewstack = self.app.add_widget('dashboard-viewstack', Adw.ViewStack())
        sttWBEmpty = StatusPageEmpty(self.app, True)
        sttWBNone = StatusPageNoWorkbooks(self.app, True)
        sttWBCurrent = StatusPageCurrentWorkbook(self.app, True)
        viewstack.add_titled(sttWBEmpty, 'wb-empty', 'Empty')
        viewstack.add_titled(sttWBNone, 'wb-none', 'No workbooks')
        viewstack.add_titled(sttWBCurrent, 'wb-current', 'Current workbook')
        viewstack.set_visible_child_name('wb-current')
        self.append(viewstack)

    def display_report(self, *args):
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

    def compile_workbook(self, *args):
        # ~ window = self.app.get_widget('window')
        progressbar = self.app.get_widget('progressbar')
        RunAsync(self._start_workflow)
        RunAsync(self.pulse)

    def pulse(self):
        # This function updates the progress
        progressbar = self.app.get_widget('progressbar')
        while True:
            time.sleep(0.5)
            filename, fraction = self.app.workflow.get_progress()
            running = fraction > 0.0
            # ~ self.log.debug("progressbar visible? %s", running)
            if running:
                progressbar.set_fraction(fraction)
                progressbar.set_text(filename)
            else:
                progressbar.set_fraction(0.0)
            # ~ self.log.debug("%s > %f", filename, fraction)

    def _start_workflow(self, *args):
        window = self.app.get_widget('window')
        if window is None:
            self.log.warning("Window still not ready! Keep waiting...")
            return True
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook is None:
            return
        self.log.debug("Workbook['%s'] update requested", workbook.id)

        # ~ #FIXME: somehow, when the workflow emits the signal, it provokes
        # ~ # core dumps
        # ~ self.app.workflow.connect('workflow-finished', self.update_dashboard)

        files = self.app.workbooks.get_files(workbook.id)
        self.app.workflow.start(workbook.id, files)
        # ~ self.set_current_workbook(workbook)

    def set_translation(self, *args):
        self.log.debug(args)

    def update_dashboard(self, *args):
        self.log.debug('Updating dashboard')
        window = self.app.get_widget('window')
        if window is None:
            self.log.warning("Window still not ready! Keep waiting...")
            return True

        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        self.log.debug("Workbook.Id: %s", workbook.id)
        return False

    def set_current_workbook(self, workbook: Workbook):
        viewstack = self.app.get_widget('dashboard-viewstack')
        page = viewstack.get_child_by_name('wb-current')
        page.set_title("Workbook %s" % workbook.id)
        vbox = self.app.factory.create_box_vertical()
        cbox = Gtk.CenterBox()
        hbox = self.app.factory.create_box_horizontal()
        button_r = self.app.factory.create_button(icon_name=ICON['WB_REFRESH'], tooltip='Delete this workbook', callback=self.compile_workbook)
        button_e = self.app.factory.create_button(icon_name=ICON['WB_EDIT'], tooltip='Edit workbook name', callback=self.app.actions.workbook_edit)
        button_d = self.app.factory.create_button(icon_name=ICON['WB_DELETE'], tooltip='Delete this workbook', callback=self.app.actions.workbook_delete)
        hbox.append(button_r)
        hbox.append(button_e)
        hbox.append(button_d)
        cbox.set_center_widget(hbox)
        vbox.append(cbox)
        vbox_empty = self.app.factory.create_box_vertical(hexpand=True, vexpand=True)
        vbox.append(Gtk.Label())
        vbox.append(vbox_empty)
        progressbar = self.app.add_widget('progressbar', Gtk.ProgressBar())
        progressbar.set_hexpand(True)
        progressbar.set_valign(Gtk.Align.CENTER)
        progressbar.set_show_text(True)
        vbox.append(progressbar)
        page.set_child(vbox)
        viewstack.set_visible_child_name('wb-current')
        self.log.debug("Displaying workbook: '%s'", workbook.id)
