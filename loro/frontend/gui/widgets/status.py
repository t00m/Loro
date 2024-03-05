#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: watcher.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Preferences window
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from gi.repository import Adw, Gtk  # type:ignore

try:
    import spacy
    SPACY_INSTALLED = True
except:
    SPACY_INSTALLED = False

if TYPE_CHECKING:
    from loro.frontend.gui.widgets.window import Window

from loro.frontend.gui import GTK_VERSION, ADW_VERSION

ICON_OK = 'emblem-default-symbolic'
ICON_KO = 'emblem-important-symbolic'


class StatusWindow(Adw.PreferencesWindow):

    def __init__(self, win: Window) -> None:
        super().__init__()
        self.window: Window = win
        self.set_title('Status')
        self._build_ui()

    def _build_ui(self) -> None:
        self.set_transient_for(self.window)
        self.set_search_enabled(False)

        versions_group: Adw.PreferencesGroup = Adw.PreferencesGroup(
            title=_("Components version"),
        )

        if Gtk.MAJOR_VERSION == 4 and Gtk.MINOR_VERSION >= 8 and Gtk.MICRO_VERSION >= 3:
            icon_name = ICON_OK
        else:
            icon_name = ICON_KO
        row_gtk = Adw.ActionRow(
            title=_("Gtk"),
            icon_name=icon_name,
        )
        row_gtk.add_suffix(Gtk.Label.new(GTK_VERSION))
        versions_group.add(row_gtk)

        if Adw.MAJOR_VERSION == 1 and Adw.MINOR_VERSION >= 2 and Gtk.MICRO_VERSION >= 2:
            icon_name = ICON_OK
        else:
            icon_name = ICON_KO
        row_adw = Adw.ActionRow(
            title=_("Adw"),
            icon_name=icon_name,
        )
        row_adw.add_suffix(Gtk.Label.new(ADW_VERSION))
        versions_group.add(row_adw)

        components_page = Adw.PreferencesPage(
            title=_("Components"),
            # ~ icon_name="errands-appearance-symbolic"
        )
        components_page.add(versions_group)
        self.add(components_page)

        if SPACY_INSTALLED:
            info = spacy.info()
            SPACY_MAJOR, SPACY_MINOR, SPACY_MICRO = info['spacy_version'].split('.')
            if SPACY_MAJOR == '3':
                icon_name = ICON_OK
            else:
                icon_name = ICON_KO
            row_spacy = Adw.ActionRow(
                title=_("Spacy"),
                icon_name=icon_name,
            )
            row_spacy.add_suffix(Gtk.Label.new("Spacy %s" % info['spacy_version']))
            versions_group.add(row_spacy)
        else:
            row_spacy = Adw.ActionRow(
                title=_("Spacy"),
                icon_name=ICON_KO,
            )
            row_spacy.add_suffix(Gtk.Label.new('Not installed'))
            versions_group.add(row_spacy)
            # ~ {'spacy_version': '3.7.4', 'location': '/home/t00m/.local/lib/python3.11/site-packages/spacy', 'platform': 'Linux-6.1.0-18-amd64-x86_64-with-glibc2.36', 'python_version': '3.11.2', 'pipelines': {'de_core_news_lg': '3.7.0', 'de_core_news_sm': '3.7.0'}}
