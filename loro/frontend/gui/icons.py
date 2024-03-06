#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: icons.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Icon manager
"""

import os

import pkg_resources

import gi
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf

from loro.backend.core.log import get_logger
from loro.backend.core.env import ENV
from loro.backend.core.util import valid_key

# FIXME: Review this module
class IconManager(GObject.GObject):
    def __init__(self, app):
        super(IconManager, self).__init__()
        self.app = app
        self.log = get_logger('IconManager')
        win = Gtk.Window()
        self.theme = Gtk.IconTheme.get_for_display(win.get_display())
        ICONSDIR = os.path.join(ENV['APP']['PGKDATADIR'], 'resources', 'icons', 'scalable')
        self.log.debug("ICONS DIR: %s", ICONSDIR)
        self.theme.add_search_path(ICONSDIR)
        self.paintable = {}
        self.gicondict = {}
        self.icondict = {}
        self.pixbufdict = {}
        self.imgdict = {}

    def choose_icon(self, icon_list: list) -> str:
        found = 'unknown'
        for icon_name in icon_list:
            if self.theme.has_icon(icon_name):
                found = icon_name;
                break
        return found

    def get_pixbuf_by_name(self, name, width=24, height=24) -> Pixbuf:
        key = valid_key("%s-%d-%d" % (name, width, height))
        try:
            pixbuf = self.pixbufdict[key]
        except:
            paintable = self.theme.lookup_icon(name, None, width, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.FORCE_REGULAR)
            gfile = paintable.get_file()
            path = gfile.get_path()
            pixbuf = Pixbuf.new_from_file_at_size(path, width, height)
            self.pixbufdict[key] = pixbuf
        return pixbuf

    def get_image_by_name(self, name: str, width: int = 24, height: int = 24) -> Gtk.Image:
        pixbuf = self.get_pixbuf_by_name(name, width, height)
        return Gtk.Image.new_from_pixbuf(pixbuf)

    def get_mimetype_icon(self, mimetype: str) -> Gtk.Image:
        try:
            gicon = self.gicondict[mimetype]
        except:
            gicon = Gio.content_type_get_icon(mimetype)
            self.gicondict[mimetype] = gicon
        return gicon


