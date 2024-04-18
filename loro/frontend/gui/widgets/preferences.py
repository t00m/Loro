#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: watcher.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Preferences window
"""

from __future__ import annotations

from gi.repository import Adw, Gtk  # type:ignore

from loro.backend.core.util import get_default_languages


class PreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, window, app) -> None:
        super().__init__()
        self.window = window
        self.app = app
        self._build_ui()

    def _build_ui(self) -> None:
        self.set_transient_for(self.window)
        self.set_search_enabled(False)

        langs_group: Adw.PreferencesGroup = Adw.PreferencesGroup(
            title=_("Languages"),
        )

        row_def_langs = Adw.ActionRow(
            title=_("Default languages"),
            subtitle=_("Source is the language you want to learn\nTarget is the language for translations")
        )
        source, target = get_default_languages()

        vbox_source = self.app.factory.create_box_vertical()
        vbox_source.append(Gtk.Label.new('Source'))
        vbox_source.append(Gtk.Label.new(source))
        row_def_langs.add_suffix(vbox_source)

        vbox_target = self.app.factory.create_box_vertical()
        vbox_target.append(Gtk.Label.new('Target'))
        vbox_target.append(Gtk.Label.new(target))
        row_def_langs.add_suffix(vbox_target)

        langs_group.add(row_def_langs)

        settings_page = Adw.PreferencesPage(
            title=_("Settings"),
            icon_name="com.github.t00m.Loro-view-pin-symbolic"
        )
        settings_page.add(langs_group)
        self.add(settings_page)
