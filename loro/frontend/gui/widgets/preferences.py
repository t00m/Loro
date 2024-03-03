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

if TYPE_CHECKING:
    from loro.frontend.gui.widgets.window import Window

from gi.repository import Adw, Gtk  # type:ignore


class PreferencesWindow(Adw.PreferencesWindow):

    def __init__(self, win: Window) -> None:
        super().__init__()
        self.window: Window = win
        self._build_ui()

    def _build_ui(self) -> None:
        self.set_transient_for(self.window)
        self.set_search_enabled(False)

