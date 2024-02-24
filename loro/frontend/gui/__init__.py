#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi  # type:ignore
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw
from gi.repository import Gtk

from loro.backend.core.log import get_logger

log = get_logger('GUI')

log.info("Adw %s.%s.%s", Adw.get_major_version(), Adw.get_minor_version(), Adw.get_micro_version())
log.info("Gtk %s.%s.%s", Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())

