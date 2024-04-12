#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import time
import threading

from gi.repository import Gio, Adw, GLib, Gtk  # type:ignore

from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.status import StatusPageNoWorkbooks
from loro.frontend.gui.widgets.status import StatusPageCurrentWorkbook


class Dashboard(Gtk.Box):
    __gtype_name__ = 'Dashboard'

    def __init__(self, app):
        super(Dashboard, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.log = get_logger('Dashboard')
        self.app = app
        self._build_dashboard()
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        ddWorkbooks.connect("notify::selected-item", self.update)
        sid = GLib.timeout_add(interval=500, function=self.update)
        self.log.debug("Signal Id: %d", sid)

    def _build_dashboard(self):
        viewstack = self.app.add_widget('dashboard-viewstack', Adw.ViewStack())
        sttWBNone = StatusPageNoWorkbooks(self.app)
        sttWBCurrent = StatusPageCurrentWorkbook(self.app)
        viewstack.add_titled(sttWBNone, 'wb-none', 'No workbooks')
        viewstack.add_titled(sttWBCurrent, 'wb-current', 'Current workbook')
        viewstack.set_visible_child_name('wb-current')
        self.append(viewstack)
        self.app.workflow.connect('workflow-finished', self.update)

    def update(self, *args):
        self.log.debug('Updating dashboard')
        window = self.app.get_widget('window')
        if window is None:
            self.log.warning("Window not ready yet! Keep waiting...")
            return True

        workbook = self.app.actions.workbook_get_current()
        if workbook is None:
            return
        self.log.debug("Displaying workbook '%s'", workbook.id)

        viewstack = self.app.get_widget('dashboard-viewstack')
        if workbook.id is None:
            viewstack.set_visible_child_name('wb-none')
        else:
            page = viewstack.get_child_by_name('wb-current')
            page.set_title("Workbook %s" % workbook.id)
            page.set_description("Some description")
            page.set_topics(workbook.id)
            toolbar = self.app.get_widget('workbook-toolbar')
            toolbar.set_visible(True)
            box_pgb = self.app.get_widget('status-box-progressbar')
            box_pgb.set_visible(False)
            viewstack.set_visible_child_name('wb-current')
            self.app.report.build_pdf(workbook.id)

        return False
