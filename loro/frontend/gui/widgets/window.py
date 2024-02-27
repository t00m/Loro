# Copyright 2023 Vlad Krupinskii <mrvladus@yandex.ru>
# SPDX-License-Identifier: MIT

from __future__ import annotations
from gi.repository import Gio, Adw, Gtk  # type:ignore

from loro.frontend.gui.gsettings import GSettings
from loro.frontend.gui.factory import WidgetFactory
from loro.frontend.gui.actions import WidgetActions
from loro.frontend.gui.models import Item
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.services.nlp.spacy import explain_term

WINDOW: Window = None


class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.app = kwargs['application']
        global WINDOW
        WINDOW = self
        self.actions = WidgetActions(self.app)
        self.factory = WidgetFactory(self.app)
        self._build_ui()
        self._update_ui()
        self.present()

    def _build_ui(self):
        self.set_title(_("Loro"))
        # ~ self.props.width_request = 1024
        # ~ self.props.height_request = 768
        # ~ # Remember window state
        # ~ GSettings.bind("width", self, "default_width")
        # ~ GSettings.bind("height", self, "default_height")
        # ~ GSettings.bind("maximized", self, "maximized")
        # Setup theme
        # ~ Adw.StyleManager.get_default().set_color_scheme(GSettings.get("theme"))

        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Headerbar
        headerbar = Adw.HeaderBar()
        viewstack = Adw.ViewStack()
        viewstack.add_titled(Gtk.Label.new('Dictionary'), 'dictionary', 'Dictionary')
        viewstack.add_titled(Gtk.Label.new('Preferences'), 'preferences', 'Preferences')
        viewswitcher = Adw.ViewSwitcher()
        viewswitcher.set_stack(viewstack)
        # ~ headerbar.set_title_widget(viewswitcher) # It works, but it is disabled by now
        mainbox.append(headerbar)

        # Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)
        toolbox.set_margin_top(margin=6)
        toolbox.set_margin_end(margin=6)
        toolbox.set_margin_bottom(margin=6)
        toolbox.set_margin_start(margin=6)

        self.ddTopics = self.factory.create_dropdown_generic(Item, enable_search=False)
        self.ddTopics.set_hexpand(False)
        self.ddTopics.connect("notify::selected-item", self._on_topic_selected)
        toolbox.append(self.ddTopics)

        self.ddSubtopics = self.factory.create_dropdown_generic(Item, enable_search=False)
        self.ddSubtopics.set_hexpand(False)
        toolbox.append(self.ddSubtopics)

        self.ddPos = self.factory.create_dropdown_generic(Item, enable_search=False)
        self.ddPos.set_hexpand(False)
        toolbox.append(self.ddPos)

        mainbox.append(toolbox)

        # Content View
        contentview = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        contentview.set_margin_top(margin=6)
        contentview.set_margin_end(margin=6)
        contentview.set_margin_bottom(margin=6)
        contentview.set_margin_start(margin=6)
        cvleft = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True)
        cvright = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        cvrightup = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        cvrightdown = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)

        contentview.append(cvleft)
        contentview.append(cvright)
        cvright.append(cvrightup)
        cvright.append(cvrightdown)
        mainbox.append(contentview)

        self.cvtokens = ColumnView(self.app, Item)
        cvleft.append(self.cvtokens)
        cvrightup.append(Gtk.Label.new('right up'))
        cvrightup.append(Gtk.Label.new('right down'))

        self.set_content(mainbox)

    def _on_topic_selected(self, *args):
        item = self.ddTopics.get_selected_item()
        topic = item.id

        fsubtopics = self.app.dictionary.get_file_subtopics()
        subtopics = json_load(fsubtopics)
        print(subtopics.keys())
        data = []
        for key in subtopics:
            if topic in subtopics[key]['topics']:
                data.append((key, key.title()))
        self.actions.dropdown_populate(self.ddSubtopics, Item, data)

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

    def _update_ui(self):

        ftopics = self.app.dictionary.get_file_topics()
        adict = json_load(ftopics)
        data = []
        for key in adict.keys():
            data.append((key, key.title()))
        self.actions.dropdown_populate(self.ddTopics, Item, data)

        fpos = self.app.dictionary.get_file_pos()
        adict = json_load(fpos)
        data = []
        for key in adict.keys():
            title = explain_term(key).title()
            data.append((key, title))
        self.actions.dropdown_populate(self.ddPos, Item, data)
