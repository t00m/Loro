#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import time
import threading
from gi.repository import Gio, Adw, GObject, Gtk  # type:ignore

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.models import Workbook
from loro.frontend.gui.widgets.preferences import PreferencesWindow
from loro.frontend.gui.widgets.check import CheckWindow
from loro.frontend.gui.widgets.editor import Editor
from loro.frontend.gui.widgets.dashboard import Dashboard
from loro.frontend.gui.widgets.browser import Browser
from loro.frontend.gui.widgets.translator import Translator
from loro.frontend.gui.widgets.status import StatusPageEmpty
from loro.frontend.gui.widgets.status import StatusPageNoWorkbooks
from loro.frontend.gui.icons import ICON


class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        self.log = get_logger('Window')
        super().__init__(**kwargs)
        GObject.GObject.__init__(self)
        GObject.signal_new('window-presented', Window, GObject.SignalFlags.RUN_LAST, None, () )
        self.connect('window-presented', self._on_finish_loading)
        self.connect('close-request', self._on_close_request)
        self.app = kwargs['application']
        self._create_actions()
        self._build_ui()
        self.present()
        self.emit('window-presented')

    def _on_close_request(self, *args):
        self.log.info("Quit application requested by user")

    def _on_finish_loading(self, *args):
        # ViewSwitcher
        # Widgets
        browser = self.app.add_widget('browser', Browser(self.app))
        editor = self.app.add_widget('editor', Editor(self.app))
        dashboard = self.app.add_widget('dashboard', Dashboard(self.app))
        translator = self.app.add_widget('translator', Translator(self.app))
        viewstack = self.app.add_widget('window-viewstack', Adw.ViewStack())
        viewstack.connect("notify::visible-child", self._on_stack_page_changed)
        viewstack.add_titled_with_icon(dashboard, 'dashboard', 'Dashboard', 'com.github.t00m.Loro-go-home-symbolic')
        # ~ viewstack.add_titled_with_icon(editor, 'workbooks', 'Workbooks', 'com.github.t00m.Loro-workbooks')
        viewstack.add_titled_with_icon(browser, 'study', 'Study', 'com.github.t00m.Loro-study-symbolic')
        # ~ viewstack.add_titled_with_icon(translator, 'translator', 'Translations', 'com.github.t00m.Loro-translate-symbolic')
        viewswitcher = self.app.add_widget('viewswitcher', Adw.ViewSwitcher())
        viewswitcher.set_stack(viewstack)
        headerbar = self.app.get_widget('headerbar')
        headerbar.set_title_widget(viewswitcher)
        mainbox = self.app.get_widget('window-mainbox')
        mainbox.append(headerbar)
        mainbox.append(viewstack)
        self.set_content(mainbox)
        # ~ dashboard.update_dashboard()
        self.update_dropdown_workbooks()
        editor.connect('workbooks-updated', self.update_dropdown_workbooks)
        # ~ editor.connect('workbooks-updated', editor.update_editor)
        progressbar = self.app.get_widget('progressbar')
        mainbox.append(progressbar)

    def show_stack_page(self, page_name: str):
        viewstack = self.app.get_widget('window-viewstack')
        viewstack.set_visible_child_name(page_name)

    def _on_stack_page_changed(self, viewstack, gparam):
        page = viewstack.get_visible_child_name()
        # ~ self.log.debug("Switched to page '%s'", page)

    def _build_ui(self):
        self.set_title(_("Loro"))
        self.app.add_widget('window-mainbox', self.app.factory.create_box_vertical(spacing=0, margin=0, hexpand=True, vexpand=True))
        headerbar = self.app.add_widget('headerbar', Adw.HeaderBar())

        # Menu
        menu: Gio.Menu = Gio.Menu.new()
        bottom_section: Gio.Menu = Gio.Menu.new()
        bottom_section.append(_("Preferences"), "app.preferences")
        # ~ bottom_section.append(_("Keyboard Shortcuts"), "win.show-help-overlay")
        bottom_section.append(_("Status"), "app.status")
        bottom_section.append(_("About Loro"), "app.about")
        bottom_section.append(_("Quit"), "app.quit")
        menu.append_section(None, bottom_section)
        menu_btn: Gtk.MenuButton = Gtk.MenuButton(
            menu_model=menu,
            primary=True,
            icon_name="open-menu-symbolic",
            tooltip_text=_("Main Menu"),
        )
        menu_btn.set_valign(Gtk.Align.CENTER)
        headerbar.pack_start(menu_btn)
        boxDpdWorkbooks = self.app.factory.create_box_horizontal(spacing=3, margin=0)
        self.app.add_widget('box-ddWorkbooks', boxDpdWorkbooks)
        ddWorkbooks = self.app.factory.create_dropdown_generic(Workbook, enable_search=True)
        self.app.add_widget('dropdown-workbooks', ddWorkbooks)
        ddWorkbooks.set_valign(Gtk.Align.CENTER)
        ddWorkbooks.connect("notify::selected-item", self._on_workbook_selected)
        ddWorkbooks.set_hexpand(False)
        boxDpdWorkbooks.append(ddWorkbooks)
        headerbar.pack_start(boxDpdWorkbooks)
        progressbar = self.app.add_widget('progressbar', Gtk.ProgressBar())
        progressbar.set_hexpand(True)
        progressbar.set_valign(Gtk.Align.CENTER)
        progressbar.set_show_text(True)
        # ~ headerbar.pack_end(progressbar)
        # ~ self.props.width_request = 1024
        # ~ self.props.height_request = 768

    def _on_workbook_selected(self, dropdown, gparam):
        dashboard = self.app.get_widget('dashboard')
        editor = self.app.get_widget('editor')
        translator = self.app.get_widget('translator')
        workbook = dropdown.get_selected_item()
        if workbook is None:
            self.log.warning("No workbooks created yet")
            return
        self.log.debug("Selected workbook: '%s'", workbook.id)
        dashboard.set_current_workbook(workbook)
        # ~ dashboard.update_dashboard()
        dashboard.display_report()
        editor.update_editor()
        translator.update()

    def _create_actions(self) -> None:
        """Create actions for main menu"""
        def _create_action(name: str, callback: callable, shortcuts=None) -> None:
            action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            if shortcuts:
                self.props.application.set_accels_for_action(f"app.{name}", shortcuts)
            self.props.application.add_action(action)

        def _about(*args) -> None:
            """Show about window"""
            if not self.about_window:
                self.about_window = Adw.AboutWindow(
                    transient_for=self,
                    version=ENV['APP']['VERSION'],
                    application_icon=ENV['APP']['ID'],
                    application_name=_("Loro"),
                    copyright="© 2024 Tomás Vírseda",
                    website="https://github.com/t00m/Loro",
                    issue_url="https://github.com/t00m/Loro/issues",
                    license_type=Gtk.License.GPL_3_0,
                    translator_credits=_("translator-credits"),
                    modal=True,
                    hide_on_close=True,
                )
            self.about_window.present()

        _create_action(
            "preferences",
            lambda *_: PreferencesWindow(self).show(),
            ["<primary>comma"],
        )
        _create_action(
            "status",
            lambda *_: CheckWindow(self).show(),
            ["<primary>comma"],
        )
        _create_action("about", _about)
        _create_action(
            "quit",
            lambda *_: self.props.application.quit(),
            ["<primary>q", "<primary>w"],
        )

    def pulse(self):
        # This function updates the progress
        progressbar = self.app.get_widget('progressbar')
        while True:
            time.sleep(0.5)
            filename, fraction = self.app.workflow.get_progress()
            running = fraction > 0.0
            # ~ self.log.debug("progressbar visible? %s", running)
            if running:
                progressbar.set_fraction(fraction)
                progressbar.set_text(filename)
            else:
                progressbar.set_fraction(0.0)
            # ~ self.log.debug("%s > %f", filename, fraction)

    def update_dropdown_workbooks(self, *args):
        workbooks = self.app.workbooks.get_all()
        data = []
        wbnames = workbooks.keys()
        if len(wbnames) == 0:
            data.append((None, 'No workbooks available'))
        else:
            for workbook in wbnames:
                data.append((workbook, "Workbook %s" % workbook))

        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        self.app.actions.dropdown_populate(ddWorkbooks, Workbook, data)
