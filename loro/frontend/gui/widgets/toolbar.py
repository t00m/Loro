#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File: toolbar.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Simple toolbar widget with no buttons

from gi.repository import Adw, Gtk  # type:ignore

from loro.backend.core.log import get_logger

class Toolbar(Gtk.Box):
    __gtype_name__ = 'Toolbar'

    def __init__(self, app, position:str = 'top'):
        self.position = position
        if position == 'top':
            super(Toolbar, self).__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=False)
        if position == 'left':
            super(Toolbar, self).__init__(orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=False)

        self.app = app
        self.log = get_logger(__class__.__name__)
        self._build_ui()

    def _build_ui(self):
        if self.position in ['top', 'left']:
            self.toolbar = Gtk.CenterBox(orientation=Gtk.Orientation.HORIZONTAL)
            self.append(self.toolbar)
            self.append(Gtk.Separator())
        else:
            self.toolbar = Gtk.CenterBox(orientation=Gtk.Orientation.HORIZONTAL)
            self.append(Gtk.Separator())
            self.append(self.toolbar)

        self.toolbar.get_style_context().add_class(class_name='toolbar')
        self.toolbar.get_style_context().add_class(class_name='linked')

    def set_start_widget(self, widget):
        self.toolbar.set_start_widget(widget)

    def set_center_widget(self, widget):
        self.toolbar.set_center_widget(widget)

    def set_end_widget(self, widget):
        self.toolbar.set_end_widget(widget)

