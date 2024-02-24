# Copyright 2023 Vlad Krupinskii <mrvladus@yandex.ru>
# SPDX-License-Identifier: MIT

from __future__ import annotations
from gi.repository import Gio, Adw, Gtk  # type:ignore

from loro.frontend.gui.gsettings import GSettings

WINDOW: Window = None


class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        global WINDOW
        WINDOW = self
        # ~ self._create_actions()
        self._build_ui()
        self.present()

    def _build_ui(self):
        self.set_title(_("Loro"))
        # ~ self.props.width_request = 360
        # ~ self.props.height_request = 200
        # ~ # Remember window state
        # ~ GSettings.bind("width", self, "default_width")
        # ~ GSettings.bind("height", self, "default_height")
        # ~ GSettings.bind("maximized", self, "maximized")
        # Setup theme
        # ~ Adw.StyleManager.get_default().set_color_scheme(GSettings.get("theme"))
        self.set_content(Gtk.Button())


    # ~ def _create_actions(self) -> None:
        # ~ """
        # ~ Create actions for main menu
        # ~ """
        # ~ Log.debug("Creating actions")

        # ~ def _create_action(name: str, callback: callable, shortcuts=None) -> None:
            # ~ action: Gio.SimpleAction = Gio.SimpleAction.new(name, None)
            # ~ action.connect("activate", callback)
            # ~ if shortcuts:
                # ~ self.props.application.set_accels_for_action(f"app.{name}", shortcuts)
            # ~ self.props.application.add_action(action)

        # ~ def _about(*args) -> None:
            # ~ """
            # ~ Show about window
            # ~ """
            # ~ if not self.about_window:
                # ~ self.about_window = Adw.AboutWindow(
                    # ~ transient_for=self,
                    # ~ version=VERSION,
                    # ~ application_icon=APP_ID,
                    # ~ application_name=_("Loro"),
                    # ~ copyright="© 2024 Tomás Vírseda",
                    # ~ website="https://github.com/t00m/Loro",
                    # ~ issue_url="https://github.com/t00m/Loro/issues",
                    # ~ license_type=Gtk.License.GPL_3_0,
                    # ~ translator_credits=_("translator-credits"),
                    # ~ modal=True,
                    # ~ hide_on_close=True,
                # ~ )
            # ~ self.about_window.present()

        # ~ _create_action(
            # ~ "preferences",
            # ~ lambda *_: PreferencesWindow(self).show(),
            # ~ ["<primary>comma"],
        # ~ )
        # ~ _create_action("about", _about)
        # ~ _create_action("import", _import)
        # ~ _create_action("secret_notes", _secret_notes)
        # ~ _create_action("sync", _sync, ["<primary>f"])
        # ~ _create_action(
            # ~ "quit",
            # ~ lambda *_: self.props.application.quit(),
            # ~ ["<primary>q", "<primary>w"],
        # ~ )
