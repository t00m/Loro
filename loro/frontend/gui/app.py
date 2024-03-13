#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import gi  # type:ignore

gi.require_version("Adw", "1")
gi.require_version("Gtk", "4.0")

from gi.repository import Adw, Gio, Gtk  # type:ignore

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.workbook import Workbook
from loro.workflow import Workflow
from loro.dictionary import Dictionary
from loro.frontend.gui.factory import WidgetFactory


class Application(Adw.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=ENV['APP']['ID'],
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.set_resource_base_path("/com/github/t00m/Loro/")
        self.window = None
        self.dictionary = Dictionary(self)
        self.workflow = Workflow(self)
        self.workbooks = Workbook(self)
        self.factory = WidgetFactory(self)

    def do_activate(self) -> None:
        from loro.frontend.gui.widgets.window import Window
        self.window = Window(application=self)

    def get_main_window(self):
        return self.window

def start():
    resource = Gio.Resource.load(os.path.join(ENV['APP']['PGKDATADIR'], 'loro.gresource'))
    resource._register()
    sys.exit(Application().run())

