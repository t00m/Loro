#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: selector.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Custom widget to manage available/used config items
"""

import os
from datetime import datetime
from gettext import gettext as _

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from loro.backend.core.log import get_logger
from loro.frontend.gui.models import Filepath, Workbook
from loro.frontend.gui.widgets.views import ColumnViewFiles


class Selector(Gtk.Box):
    def __init__(self, app):
        self.app = app
        self.factory = self.app.factory
        self.log = get_logger('Selector')
        super(Selector, self).__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True, spacing=0)

        # Entry and buttons for operations (edit/add/remove)
        self.boxOper = Gtk.Box(spacing=3, orientation=Gtk.Orientation.HORIZONTAL)
        self.boxOper.set_vexpand(False)
        self.append(self.boxOper)
        boxViews = self.factory.create_box_horizontal(spacing=0, hexpand=True, vexpand=True)
        self.boxLeft = self.factory.create_box_vertical(spacing=0, hexpand=True, vexpand=True)
        self.boxLeft.props.width_request = 300
        self.boxControls = Gtk.CenterBox()
        self.boxControls.set_orientation(Gtk.Orientation.VERTICAL)
        self.boxRight = self.factory.create_box_vertical(spacing=0, hexpand=True, vexpand=True)
        self.boxRight.props.width_request = 300
        boxViews.append(self.boxLeft)
        boxViews.append(self.boxControls)
        boxViews.append(self.boxRight)
        self.append(boxViews)

        # Available
        # ~ label = Gtk.Label()
        # ~ label.set_markup(_('<b>Files available</b>'))
        # ~ button = self.factory.create_button()
        # ~ button.set_child(label)
        # ~ button.set_has_frame(False)
        # ~ button.set_margin_bottom(margin=6)
        # ~ self.boxLeft.append(button)

        # Controls
        boxSel = self.factory.create_box_vertical()
        self.btnAddToUsed = self.factory.create_button('com.github.t00m.Loro-selector-add', width=16) #, callback=self._on_item_used_add)
        self.btnRemoveFromUsed = self.factory.create_button('com.github.t00m.Loro-selector-remove', width=16) #, callback=self._on_item_used_remove)
        boxSel.append(self.btnAddToUsed)
        boxSel.append(self.btnRemoveFromUsed)
        self.boxControls.set_center_widget(boxSel)

        # Used
        # ~ label = Gtk.Label()
        # ~ label.set_markup(_('<b>Files in this workbook</b>'))
        # ~ button = self.factory.create_button()
        # ~ button.set_child(label)
        # ~ button.set_has_frame(False)
        # ~ button.set_margin_bottom(margin=6)
        # ~ self.boxRight.append(button)

    def set_action_add_to_used(self, callback):
        self.btnAddToUsed.connect('clicked', callback)

    def set_action_remove_from_used(self, callback):
        self.btnRemoveFromUsed.connect('clicked', callback)

    def add_columnview_available(self, columnview):
        self.boxLeft.append(columnview)

    def add_columnview_used(self, columnview):
        self.boxRight.append(columnview)

    # ~ def hide_available(self, button, gparam):
        # ~ visible = button.get_active()
        # ~ self.boxLeft.set_visible(visible)
        # ~ self.boxControls.set_visible(visible)

    def _setup_view_finish(self, *args):
        pass

    def update(self, *args):
        self._update_view_available()
        self._update_view_used()

    def _update_view_available(self):
        items_available = []
        item_type = self.config.model
        items = self.config.load_available()
        for key in items:
            items_available.append(item_type(id=key, title=items[key]))
        self.viewAv.update(items_available)

    def _update_view_used(self):
        items_used = []
        item_type = self.config.model
        items = self.config.load_used()
        for key in items:
            items_used.append(item_type(id=key, title=items[key]))
        self.viewSl.update(items_used)

    def _on_filter_selected(self, *args):
        self.viewAv.refilter()
        self.viewSl.refilter()

    def _do_filter_view(self, item, filter_list_model):
        chunk = self.entry.get_text().upper()
        string = "%s%s" % (item.id, item.title)
        if chunk in string.upper():
            return True
        return False

    def _on_entrysearch_delete(self, *args):
        self.entry.set_text("")

    def get_search_entry(self):
        return self.entry
