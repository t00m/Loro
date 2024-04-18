#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import sys
import time
import threading

from gi.repository import Gio, Adw, GObject, Gtk  # type:ignore

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.models import Workbook
from loro.frontend.gui.widgets.preferences import PreferencesWindow
from loro.frontend.gui.widgets.check import CheckWindow
from loro.frontend.gui.widgets.dashboard import Dashboard
# ~ from loro.frontend.gui.widgets.editor import Editor
# ~ from loro.frontend.gui.widgets.browser import Browser
# ~ from loro.frontend.gui.widgets.translator import Translator
from loro.frontend.gui.icons import ICON


class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        self.log = get_logger('Window')
        super().__init__(**kwargs)
        self.set_title(_("Loro"))
        self.connect('close-request', self._on_close_request)
        self.app = kwargs['application']
        self._create_actions()
        self._build_ui()
        self.present()
        self.app.actions.update_dropdown_workbooks()

    def _build_ui(self):
        # Main box to attach to the window
        mainbox = self.app.factory.create_box_vertical(spacing=0, margin=0, hexpand=True, vexpand=True)
        self.app.add_widget('window-mainbox', mainbox)

        # Headerbar
        headerbar = self.app.add_widget('headerbar', Adw.HeaderBar())
        mainbox.append(headerbar)

        # Hamburguer Menu
        menu: Gio.Menu = Gio.Menu.new()
        upper_section: Gio.Menu = Gio.Menu.new()
        upper_section.append(_("Create workbook"), "app.workbook_new")
        bottom_section: Gio.Menu = Gio.Menu.new()
        bottom_section.append(_("Preferences"), "app.preferences")
        bottom_section.append(_("Status"), "app.status")
        bottom_section.append(_("About Loro"), "app.about")
        bottom_section.append(_("Quit"), "app.quit")
        menu.append_section(None, upper_section)
        menu.append_section(None, bottom_section)
        menu_btn: Gtk.MenuButton = Gtk.MenuButton(
            menu_model=menu,
            primary=True,
            icon_name="open-menu-symbolic",
            tooltip_text=_("Main Menu"),
        )
        self.app.add_widget('window-btn-menu', menu_btn)
        menu_btn.set_valign(Gtk.Align.CENTER)
        headerbar.pack_start(menu_btn)

        # Workbooks Dropdown
        boxDpdWorkbooks = self.app.factory.create_box_horizontal(spacing=0, margin=0)
        self.app.add_widget('box-ddWorkbooks', boxDpdWorkbooks)
        ddWorkbooks = self.app.factory.create_dropdown_generic(Workbook, enable_search=True)
        self.app.add_widget('dropdown-workbooks', ddWorkbooks)
        ddWorkbooks.set_valign(Gtk.Align.CENTER)
        ddWorkbooks.set_hexpand(False)
        boxDpdWorkbooks.append(ddWorkbooks)
        headerbar.pack_start(boxDpdWorkbooks)

        # Workbook Toolbar
        toolbar = self.app.factory.create_box_horizontal(spacing=0, margin=0)
        self.app.add_widget('window-toolbar', toolbar)
        toolbar.get_style_context().add_class(class_name='toolbar')
        toolbar.get_style_context().add_class(class_name='linked')
        self.app.add_widget('status-box-toolbar', toolbar)
        button_s = self.app.factory.create_button(icon_name=ICON['WB_HOME'], width=16, tooltip='Workbook summary', callback=self.app.actions.workbook_summary)
        self.app.add_widget('status-workbook-summary', button_s)
        button_b= self.app.factory.create_button(icon_name=ICON['WB_STUDY'], width=16, tooltip='Study this workbook', callback=self.app.actions.workbook_study)
        self.app.add_widget('status-workbook-study', button_b)
        button_e = self.app.factory.create_button(icon_name=ICON['WB_EDIT'], width=16, tooltip='Edit workbook', callback=self.app.actions.workbook_edit)
        self.app.add_widget('status-workbook-edit', button_e)
        button_t = self.app.factory.create_button(icon_name=ICON['WB_TRANSLATE'], width=16, tooltip='Translate workbook', callback=self.app.actions.workbook_translate)
        self.app.add_widget('status-workbook-translate', button_t)
        toolbar.append(button_s)
        toolbar.append(button_b)
        toolbar.append(button_e)
        toolbar.append(button_t)
        headerbar.set_title_widget(toolbar)

        # Viewstack
        # ~ editor = self.app.add_widget('editor', Editor(self.app))
        # ~ browser = self.app.add_widget('browser', Browser(self.app))
        dashboard = self.app.add_widget('dashboard', Dashboard(self.app))
        viewstack = self.app.add_widget('window-viewstack', Adw.ViewStack())
        viewstack.connect("notify::visible-child", self._on_stack_page_changed)
        viewstack.add_titled_with_icon(dashboard, 'dashboard', 'Dashboard', 'com.github.t00m.Loro-go-home-symbolic')
        # ~ viewstack.add_titled_with_icon(editor, 'editor', 'Editor', 'com.github.t00m.Loro-text-editor-symbolic')
        # ~ viewstack.add_titled_with_icon(browser, 'study', 'Study', 'com.github.t00m.Loro-study-symbolic')
        # ~ viewswitcher = self.app.add_widget('viewswitcher', Adw.ViewSwitcher())
        # ~ viewswitcher.set_stack(viewstack)
        mainbox.append(viewstack)
        self.set_content(mainbox)

    def _on_close_request(self, *args):
        self.log.info("Quit application requested by user")
        self.app.quit()
        sys.exit(0)

    def show_stack_page(self, page_name: str):
        viewstack = self.app.get_widget('window-viewstack')
        viewstack.set_visible_child_name(page_name)

    def _on_stack_page_changed(self, viewstack, gparam):
        page = viewstack.get_visible_child_name()

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
            "workbook_new",
            lambda *_: self.app.actions.workbook_create(),
            # ~ ["<primary>comma"],
        )

        _create_action(
            "preferences",
            lambda *_: PreferencesWindow(self, self.app).show(),
            # ~ ["<primary>comma"],
        )
        _create_action(
            "status",
            lambda *_: CheckWindow(self).show(),
            # ~ ["<primary>comma"],
        )
        _create_action("about", _about)
        _create_action(
            "quit",
            lambda *_: self.props.application.quit(),
            ["<primary>q", "<primary>w"],
        )
