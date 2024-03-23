#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi  # type:ignore
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version('WebKit', '6.0')

from gi.repository import GObject
from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import WebKit

from loro.backend.core.log import get_logger

# ~ GObject.threads_init()

log = get_logger('GUI')

GTK_VERSION = "Gtk %s.%s.%s" % (Gtk.MAJOR_VERSION, Gtk.MINOR_VERSION, Gtk.MICRO_VERSION)
ADW_VERSION = "Adw %s.%s.%s" % (Adw.MAJOR_VERSION, Adw.MINOR_VERSION, Adw.MICRO_VERSION)

# ~ log.info(GTK_VERSION)
# ~ log.info(ADW_VERSION)


