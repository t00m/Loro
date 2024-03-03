#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
from gi.repository import Gio, Adw, Gtk  # type:ignore

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.dashboard import Dashboard
from loro.frontend.gui.widgets.editor import Editor
from loro.frontend.gui.widgets.preferences import PreferencesWindow


WINDOW: Window = None

class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        self.log = get_logger('Window')
        super().__init__(**kwargs)
        self.app = kwargs['application']
        global WINDOW
        WINDOW = self
        self._create_actions()
        self._build_ui()
        self.present()

    def _build_ui(self):
        self.set_title(_("Loro"))

        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Headerbar with ViewSwitcher
        headerbar = Adw.HeaderBar()

        # Menu
        menu: Gio.Menu = Gio.Menu.new()
        bottom_section: Gio.Menu = Gio.Menu.new()
        bottom_section.append(_("Preferences"), "app.preferences")
        bottom_section.append(_("Keyboard Shortcuts"), "win.show-help-overlay")
        bottom_section.append(_("About Loro"), "app.about")
        menu.append_section(None, bottom_section)
        menu_btn: Gtk.MenuButton = Gtk.MenuButton(
            menu_model=menu,
            primary=True,
            icon_name="open-menu-symbolic",
            tooltip_text=_("Main Menu"),
        )
        headerbar.pack_start(menu_btn)

        # ViewSwitcher
        viewstack = Adw.ViewStack()
        viewstack.add_titled_with_icon(Dashboard(self.app), 'dashboard', 'Dashboard', 'accessories-dictionary-symbolic')
        viewstack.add_titled_with_icon(Editor(self.app), 'editor', 'Documents', 'emblem-documents-symbolic')

        viewswitcher = Adw.ViewSwitcher()
        viewswitcher.set_stack(viewstack)
        headerbar.set_title_widget(viewswitcher)
        mainbox.append(headerbar)
        mainbox.append(viewstack)
        self.set_content(mainbox)

        # TODO:
        # ~ from loro.frontend.gui.gsettings import GSettings
        self.props.width_request = 1024
        self.props.height_request = 768
        # ~ # Remember window state
        # ~ GSettings.bind("width", self, "default_width")
        # ~ GSettings.bind("height", self, "default_height")
        # ~ GSettings.bind("maximized", self, "maximized")
        # Setup theme
        # ~ Adw.StyleManager.get_default().set_color_scheme(GSettings.get("theme"))

    def _create_actions(self) -> None:
        """
        Create actions for main menu
        """
        self.log.debug("Creating actions")

        def _create_action(name: str, callback: callable, shortcuts=None) -> None:
            action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            if shortcuts:
                self.props.application.set_accels_for_action(f"app.{name}", shortcuts)
            self.props.application.add_action(action)

        def _about(*args) -> None:
            """
            Show about window
            """
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
        _create_action("about", _about)
        _create_action(
            "quit",
            lambda *_: self.props.application.quit(),
            ["<primary>q", "<primary>w"],
        )
