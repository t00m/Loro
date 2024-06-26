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
from loro.backend.services.nlp.spacy import NLP
from loro.backend.services.duden.duden import Duden
from loro.workbook import Workbook
from loro.workflow import Workflow
from loro.cache import Cache
from loro.translate import Translate
from loro.stats import Stats
from loro.report import Report
from loro.disrec import DisasterRecovery
from loro.frontend.gui.factory import WidgetFactory
from loro.frontend.gui.actions import WidgetActions


class Application(Adw.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=ENV['APP']['ID'],
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.log = get_logger('Application')
        self.set_resource_base_path("/com/github/t00m/Loro/")
        self._widgets = {}
        self.window = None
        self.dr = DisasterRecovery(self)
        self.nlp = NLP(self)
        self.cache = Cache(self)
        self.workflow = Workflow(self)
        self.workbooks = Workbook(self)
        self.stats = Stats(self)
        self.translate = Translate(self)
        self.factory = WidgetFactory(self)
        self.actions = WidgetActions(self)
        self.report = Report(self)
        self.duden = Duden(self)

    def do_activate(self) -> None:
        from loro.frontend.gui.widgets.window import Window
        self.window = Window(application=self)
        self.window.set_default_size(1024, 728)
        self.add_widget('window', self.window)

    def add_widget(self, name: str, widget):
        # Add widget, but do not overwrite
        if name not in self._widgets:
            self._widgets[name] = widget
            return widget
        else:
            self.log.error("A widget with name '%s' already exists with type(%s)", name, type(self._widgets[name]))
            return None

    def set_widget(self, name: str, widget):
        # Overwrite existing widget
        if name in self._widgets:
            self._widgets[name] = widget
            return widget
        else:
            self.log.error("A widget with name '%s' doesn't exists", name)

    def get_widget(self, name):
        try:
            return self._widgets[name]
        except KeyError:
            return None

def start():
    resource = Gio.Resource.load(os.path.join(ENV['APP']['PGKDATADIR'], 'loro.gresource'))
    resource._register()
    sys.exit(Application().run())

