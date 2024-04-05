#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: status.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Status pages
"""

from gi.repository import Adw, Gtk  # type:ignore

from loro.backend.core.log import get_logger
from loro.frontend.gui.icons import ICON

class StatusPage(Gtk.Box):
    __gtype_name__ = 'StatusPage'

    def __init__(self, app, visible):
        super(StatusPage, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.log = get_logger(__class__.__name__)
        self.status = Adw.StatusPage()
        self.status.set_title('Status Page')
        self.status.set_child(Gtk.Label())
        self.status.set_visible(visible)
        self.append(self.status)

    def set_title(self, title: str):
        self.status.set_title(title)

    def set_visible(self, visible: bool):
        self.status.set_visible(visible)

    def set_child(self, child: Gtk.Widget):
        self.status.set_child(child)

class StatusPageEmpty(StatusPage):
    __gtype_name__ = 'StatusPageEmpty'

    def __init__(self, app, visible):
        super().__init__(app, visible)
        self.set_title('Empty Status Page')
        # ~ self.set_child(Gtk.Label.new('Empty'))

class StatusPageNoWorkbooks(StatusPage):
    __gtype_name__ = 'StatusPageNoWorkbooks'

    def __init__(self, app, visible):
        super().__init__(app, visible)
        self.set_title('No workbooks available')
        vbox = self.app.factory.create_box_vertical(hexpand=False, vexpand=False)
        button = self.app.factory.create_button(icon_name=ICON['WB_NEW'], title='Add a new workbook', width=16, tooltip='At least one workbook must be active in the application', callback=self.add_workbook)
        button.set_hexpand(False)
        vbox.append(button)
        vbox.set_valign(Gtk.Align.CENTER)
        self.set_child(vbox)

    def add_workbook(self, *args):
        editor = self.app.get_widget('editor')
        editor._on_workbook_add()

class StatusPageCurrentWorkbook(StatusPage):
    __gtype_name__ = 'StatusPageCurrentWorkbook'

    def __init__(self, app, visible):
        super().__init__(app, visible)
        vbox = self.app.factory.create_box_vertical(hexpand=False, vexpand=False)
        vbox.set_valign(Gtk.Align.CENTER)
        self.set_child(vbox)

    # ~ def set_title(self, workbook: str):
        # ~ self.set_title("Workbook %s" % workbook)
