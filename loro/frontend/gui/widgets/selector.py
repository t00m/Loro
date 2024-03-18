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

from MiAZ.backend.log import get_logger
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
        boxViews = self.factory.create_box_horizontal(spacing=0, hexpand=False, vexpand=True)
        self.boxLeft = self.factory.create_box_vertical(spacing=0, hexpand=False, vexpand=True)
        boxControls = Gtk.CenterBox()
        boxControls.set_orientation(Gtk.Orientation.VERTICAL)
        self.boxRight = self.factory.create_box_vertical(spacing=0, hexpand=False, vexpand=True)
        boxViews.append(self.boxLeft)
        boxViews.append(boxControls)
        boxViews.append(self.boxRight)
        self.append(boxViews)

        # Available
        # ~ self.frmViewAv = Gtk.Frame()
        title = Gtk.Label()
        title.set_markup(_('<b>Files available</b>'))
        self.boxLeft.append(title)
        # ~ self.boxLeft.append(self.frmViewAv)

        # Controls
        boxSel = self.factory.create_box_vertical()
        self.btnAddToUsed = self.factory.create_button('com.github.t00m.Loro-selector-add', width=16) #, callback=self._on_item_used_add)
        self.btnRemoveFromUsed = self.factory.create_button('com.github.t00m.Loro-selector-remove', width=16) #, callback=self._on_item_used_remove)
        boxSel.append(self.btnAddToUsed)
        boxSel.append(self.btnRemoveFromUsed)
        boxControls.set_center_widget(boxSel)

        # Used
        # ~ self.frmViewSl = Gtk.Frame()
        title = Gtk.Label()
        title.set_markup(_('<b>In this workbook</b>'))
        self.boxRight.append(title)
        # ~ self.boxRight.append(self.frmViewSl)

        self._setup_view_finish()

    def set_action_add_to_used(self, callback):
        self.btnAddToUsed.connect('clicked', callback)

    def set_action_remove_from_used(self, callback):
        self.btnRemoveFromUsed.connect('clicked', callback)

    def statusbar_message(self, dtype: str = 'warning', message: str = ''):
        icon_name = {}
        icon_name["info"] = "dialog-information-symbolic"
        icon_name["warning"] = "dialog-warning-symbolic"
        icon_name["error"] = "dialog-error-symbolic"
        icon_name["question"] = "dialog-question-symbolic"
        icon_name[""] = None
        self.sbicon.set_from_icon_name(icon_name[dtype])
        self.sbtext.set_markup(message)

    def add_columnview_available(self, columnview):
        self.boxLeft.append(columnview)
        # ~ columnview.set_filter(self._do_filter_view)
        # ~ columnview.column_title.set_expand(True)
        # ~ columnview.cv.connect("activate", self._on_selected_item_available_notify)
        # ~ self.frmViewAv.set_child(columnview)
        # ~ columnview.cv.sort_by_column(columnview.column_title, Gtk.SortType.ASCENDING)
        # ~ columnview.cv.get_style_context().add_class(class_name='caption')

    def add_columnview_used(self, columnview):
        self.boxRight.append(columnview)
        # ~ columnview.set_filter(None)
        # ~ columnview.column_title.set_expand(True)
        # ~ self.frmViewSl.set_child(columnview)
        # ~ columnview.cv.sort_by_column(columnview.column_title, Gtk.SortType.ASCENDING)
        # ~ columnview.cv.get_style_context().add_class(class_name='caption')

    def _setup_view_finish(self, *args):
        pass

    def update(self, *args):
        self._update_view_available()
        self._update_view_used()
        # ~ self.statusbar_message('', '')

    def _on_item_used_add(self, *args):
        return
        # ~ changed = False
        # ~ items_used = self.config.load_used()
        # ~ for item_available in self.viewAv.get_selected_items():
            # ~ items_used[item_available.id] = item_available.title
            # ~ self.log.debug("Using %s (%s)", item_available.id, item_available.title)
            # ~ changed = True
        # ~ if changed:
            # ~ self.config.save_used(items=items_used)
            # ~ self._update_view_used()

    def _on_item_used_remove(self, *args):
        return
        # ~ value_used = False
        # ~ changed = False
        # ~ items_used = self.config.load_used()
        # ~ items_available = self.config.load_available()
        # ~ for item_used in self.viewSl.get_selected_items():
            # ~ if item_used.id not in items_available:
                # ~ items_available[item_used.id] = item_used.title
            # ~ if self.config.model == Repository:
                # ~ value_used = False
            # ~ elif self.config.model == Project:
                # ~ self.projects = self.backend.projects
                # ~ docs = self.projects.docs_in_project(item_used.id)
                # ~ value_used = len(docs) > 0
            # ~ else:
                # ~ value_used = self.util.field_used(self.config.model, item_used.id)

            # ~ if not value_used:
                # ~ del(items_used[item_used.id])
                # ~ changed = True
                # ~ text = _('Removed %s (%s) from used') % (item_used.id, item_used.title)
                # ~ self.log.debug(text)
            # ~ else:
                # ~ dtype = "warning"
                # ~ text = _('%s %s is still being used by some docs') % (self.config.model.__title__, item_used.id)
                # ~ self.statusbar_message(dtype, text)
        # ~ if changed:
            # ~ self.config.save_used(items=items_used)
            # ~ self.config.save_available(items=items_available)
            # ~ self._update_view_used()
            # ~ self._update_view_available()

    def _on_item_available_add(self, *args):
        return
        # ~ if self.edit:
            # ~ dialog = MiAZDialogAdd(self.app, self.get_root(), _('%s: add a new item') % self.config.config_for, _('Name'), _('Description'))
            # ~ search_term = self.entry.get_text()
            # ~ dialog.set_value1(search_term)
            # ~ dialog.connect('response', self._on_response_item_available_add)
            # ~ dialog.show()

    def _on_response_item_available_add(self, dialog, response):
        return
        # ~ if response == Gtk.ResponseType.ACCEPT:
            # ~ key = dialog.get_value1()
            # ~ value = dialog.get_value2()
            # ~ if len(key) > 0:
                # ~ self.config.add_available(key.upper(), value)
                # ~ self.log.debug("%s (%s) added to list of available items", key, value)
                # ~ self.update()
        # ~ dialog.destroy()

    def _on_item_available_rename(self, item):
        return
        # ~ dialog = MiAZDialogAdd(self.app, self.get_root(), _('%s: rename item') % self.config.config_for, _('Name'), _('Description'))
        # ~ dialog.set_value1(item.id)
        # ~ dialog.set_value2(item.title)
        # ~ dialog.connect('response', self._on_response_item_available_rename, item)
        # ~ dialog.show()

    def _on_response_item_available_rename(self, dialog, response, item):
        return
        # ~ if response == Gtk.ResponseType.ACCEPT:
            # ~ oldkey = item.id
            # ~ newkey = dialog.get_value1()
            # ~ newval = dialog.get_value2()
            # ~ self.log.debug("Renaming %s by %s (%s)", oldkey, newkey, newval)
            # ~ if len(newkey) > 0:
                # ~ # Rename items used
                # ~ items_used = self.config.load_used()
                # ~ if oldkey in items_used:
                    # ~ self.config.remove_used(oldkey)
                    # ~ self.config.add_used(newkey, newval)
                    # ~ self.log.debug("Renamed items_used")
                # ~ # Rename items available
                # ~ items_available = self.config.load_available()
                # ~ self.config.remove_available(oldkey)
                # ~ self.config.add_available(newkey, newval)
                # ~ self.log.debug("%s renamed to %s (%s) in the list of available items", oldkey, newkey, newval)
                # ~ self.update()
        # ~ dialog.destroy()

    def _on_item_available_remove(self, *args):
        return
        # ~ keys = []
        # ~ for item_available in self.viewAv.get_selected_items():
            # ~ keys.append(item_available.id)
        # ~ self.config.remove_available_batch(keys)
        # FIXME: self.config.remove_used(item.id)
        # ~ self.update()
        # ~ self.entry.set_text('')
        # ~ self.entry.activate()

    def _on_selected_item_available_notify(self, colview, pos):
        return
        # ~ model = colview.get_model()
        # ~ item = model.get_item(pos)
        # ~ self._on_item_available_rename(item)

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
