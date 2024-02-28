#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: views.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Different views based on ColumnView widget
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import Pango

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.models import Item


class ColumnViewToken(ColumnView):
    """ Custom ColumnView widget for tokens """
    __gtype_name__ = 'ColumnViewToken'

    def __init__(self, app):
        super().__init__(app, item_type=Item)
        self.cv.append_column(self.column_id)
        self.column_id.set_visible(False)
        self.column_title.set_title(_('Id'))
        self.cv.append_column(self.column_title)
        self.column_title.set_title(_('Token'))
