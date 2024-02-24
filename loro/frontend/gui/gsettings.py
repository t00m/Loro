# Copyright 2023 Vlad Krupinskii <mrvladus@yandex.ru>
# SPDX-License-Identifier: MIT

from gi.repository import GLib, Gio, Gtk  # type:ignore

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger

log = get_logger('GSettings')

class GSettings:
    """Class for accessing gsettings"""

    gsettings: Gio.Settings = None
    initialized: bool = False

    def _check_init(self):
        if not self.initialized:
            self.init()

    @classmethod
    def bind(self, setting: str, obj: Gtk.Widget, prop: str, invert: bool = False) -> None:
        self._check_init(self)
        self.gsettings.bind(
            setting,
            obj,
            prop,
            (
                Gio.SettingsBindFlags.INVERT_BOOLEAN
                if invert
                else Gio.SettingsBindFlags.DEFAULT
            ),
        )

    @classmethod
    def get(self, setting: str):
        self._check_init(self)
        return self.gsettings.get_value(setting).unpack()

    @classmethod
    def set(self, setting: str, gvariant: str, value) -> None:
        self._check_init(self)
        self.gsettings.set_value(setting, GLib.Variant(gvariant, value))

    @classmethod
    def init(self) -> None:
        log.debug("Initialize GSettings")
        self.initialized = True
        self.gsettings = Gio.Settings.new(ENV['APP']['ID'])
