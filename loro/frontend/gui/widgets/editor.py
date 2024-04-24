#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import os
import shutil

import gi

from gi.repository import Gio, GObject, Adw, Gtk  # type:ignore

from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.translator import Translator
from loro.frontend.gui.widgets.wbeditor import WorkbookEditor
from loro.frontend.gui.widgets.toolbar import Toolbar
from loro.frontend.gui.icons import ICON


class Editor(Gtk.Box):
    __gtype_name__ = 'Editor'

    def __init__(self, app):
        super(Editor, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.log = get_logger('Editor')
        self.app = app
        # ~ GObject.signal_new('workbooks-updated', Editor, GObject.SignalFlags.RUN_LAST, None, () )
        # ~ GObject.signal_new('filenames-updated', Editor, GObject.SignalFlags.RUN_LAST, None, () )
        self._build_editor()
        # ~ self.update()
        # ~ self._set_enable_renaming(False)
        # ~ self._set_enable_deleting(False)
        # ~ self._connect_signals()
        self.log.debug("Editor initialited")

    def connect_signals(self):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        ddWorkbooks.connect("notify::selected-item", self.update)

    def _build_editor(self):
        mainbox = self.app.factory.create_box_vertical(margin=0, spacing=0, hexpand=True, vexpand=True)
        self.append(mainbox)

        wbeditor = self.app.add_widget('wbeditor', WorkbookEditor(self.app))
        translator = self.app.add_widget('translator', Translator(self.app))
        viewstack = self.app.add_widget('editor-viewstack', Adw.ViewStack())
        viewstack.add_titled_with_icon(wbeditor, 'editor', 'Editor', ICON['WB_EDIT'])
        viewstack.add_titled_with_icon(translator, 'translator', 'Translator', ICON['WB_TRANSLATE'])
        viewswitcher = self.app.add_widget('editor-viewswitcher', Adw.ViewSwitcher())
        viewswitcher.set_stack(viewstack)

        # Toolbar
        toolbar = Toolbar(self.app)

        # ~ hboxSuggestedActions = self.app.factory.create_box_horizontal()
        # ~ button_r = self.app.factory.create_button(icon_name=ICON['WB_REFRESH'], title='Compile', tooltip='Refresh/Compile workbook', width=16, callback=self.app.actions.workbook_compile)
        # ~ self.app.add_widget('status-workbook-refresh', button_r)
        # ~ sep = Gtk.Separator()
        # ~ button_t = self.app.factory.create_button(icon_name=ICON['WB_TRANSLATE'], title='Translate', tooltip='Translate workbook words and sentences', width=16, callback=self.app.actions.workbook_compile)
        # ~ self.app.add_widget('status-workbook-translate', button_t)
        # ~ hboxSuggestedActions.append(button_r)
        # ~ hboxSuggestedActions.append(sep)
        # ~ hboxSuggestedActions.append(button_t)
        # ~ toolbar.set_start_widget(hboxSuggestedActions)

        toolbar.set_center_widget(viewswitcher)

        # ~ button_d = self.app.factory.create_button(icon_name=ICON['WB_DELETE'], title='Delete workbook', tooltip='Delete workbook', width=16, callback=self.app.actions.workbook_delete)
        # ~ button_d.get_style_context().add_class(class_name='error')
        # ~ toolbar.set_end_widget(button_d)

        mainbox.append(toolbar)
        # ~ mainbox.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        mainbox.append(viewstack)

    # ~ def _finish_loading(self, *args):
        # ~ ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        # ~ ddWorkbooks.connect("notify::selected-item", self._on_workbook_selected)

    def update(self, *args):
        workbook = self.app.actions.workbook_get_current()
        if workbook is None:
            return

        self.current_workbook = workbook.id
        if workbook is not None:
            if workbook.id is not None:
                self.log.debug(workbook.id)
                # ~ self._update_files_view(workbook.id)
                # ~ self.cvfilesUsed.set_title("On workbook %s" % workbook.id)
                # ~ self.app.actions.show_editor()
            # ~ else:
                # ~ self.app.actions.show_warning_noworkbooks()
