#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: actions.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: App actions
"""

from gettext import gettext as _

from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger

class WidgetActions(GObject.GObject):
    def __init__(self, app):
        self.log = get_logger('WidgetActions')
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
