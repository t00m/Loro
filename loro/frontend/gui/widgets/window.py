#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gio, Adw, Gtk  # type:ignore

from loro.backend.core.log import get_logger
from loro.frontend.gui.widgets.dashboard import Dashboard


class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        self.log = get_logger('Window')
        super().__init__(**kwargs)
        self.app = kwargs['application']
        global WINDOW
        WINDOW = self

        self._build_ui()
        self.present()

    def _build_ui(self):
        self.set_title(_("Loro"))

        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Headerbar with ViewSwitcher
        headerbar = Adw.HeaderBar()
        viewstack = Adw.ViewStack()
        viewstack.add_titled_with_icon(Dashboard(self.app), 'dashboard', 'Dashboard', 'accessories-dictionary-symbolic')
        viewstack.add_titled_with_icon(Gtk.Label.new('Preferences'), 'preferences', 'Preferences', 'preferences-system-symbolic')
        viewswitcher = Adw.ViewSwitcher()
        viewswitcher.set_stack(viewstack)
        headerbar.set_title_widget(viewswitcher) # It works, but it is disabled by now
        mainbox.append(headerbar)
        mainbox.append(viewstack)
        self.set_content(mainbox)

        # TODO:
        # ~ from loro.frontend.gui.gsettings import GSettings
        # ~ self.props.width_request = 1024
        # ~ self.props.height_request = 768
        # ~ # Remember window state
        # ~ GSettings.bind("width", self, "default_width")
        # ~ GSettings.bind("height", self, "default_height")
        # ~ GSettings.bind("maximized", self, "maximized")
        # Setup theme
        # ~ Adw.StyleManager.get_default().set_color_scheme(GSettings.get("theme"))

WINDOW: Window = None
