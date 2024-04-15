#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: summary.py
# Author: Tomás Vírseda
# License: GPL v3
"""

import os
import sys

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.icons import ICON


class Summary(Gtk.Box):
    __gtype_name__ = 'Summary'

    def __init__(self, app):
        super(Summary, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.log = get_logger('Summary')
        self._setup_widget()

    def _setup_widget(self):

        header = Gtk.CenterBox()
        body = self.app.factory.create_box_vertical(hexpand=True, vexpand=True)
        footer = Gtk.CenterBox()
        self.append(header)
        self.append(body)
        self.append(footer)


        self.lblWBId = Gtk.Label.new('Summary')


        body.append(self.lblWBId)
        # ~ footer.set_start_widget(button_d)

        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        ddWorkbooks.connect("notify::selected-item", self.update)

    def update(self, *args):
        workbook = self.app.actions.workbook_get_current()
        if workbook is None:
            return
        if workbook.id is None:
            return
        self.lblWBId.set_text(workbook.id)
