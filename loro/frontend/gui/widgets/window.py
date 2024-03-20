#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
import time
import threading
from gi.repository import Gio, Adw, GObject, Gtk  # type:ignore

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.run_async import RunAsync
from loro.frontend.gui.models import Workbook
from loro.frontend.gui.widgets.preferences import PreferencesWindow
from loro.frontend.gui.widgets.status import StatusWindow
from loro.frontend.gui.widgets.editor import Editor
from loro.frontend.gui.widgets.dashboard import Dashboard
from loro.frontend.gui.widgets.browser import Browser
from loro.frontend.gui.icons import ICON


# ~ WINDOW: Window = None

class Window(Adw.ApplicationWindow):
    about_window: Adw.AboutWindow = None

    def __init__(self, **kwargs) -> None:
        self.log = get_logger('Window')
        super().__init__(**kwargs)
        GObject.GObject.__init__(self)
        GObject.signal_new('window-presented', Window, GObject.SignalFlags.RUN_LAST, None, () )
        self.connect('window-presented', self._finish_loading)
        self.app = kwargs['application']
        self._create_actions()
        self._build_ui()
        self.present()
        self.emit('window-presented')

    def _finish_loading(self, *args):
        # ViewSwitcher
        # Widgets
        self.editor = Editor(self.app)
        self.dashboard = Dashboard(self.app)
        self.browser = Browser(self.app)
        self.status = Adw.StatusPage()
        spinner = Gtk.Spinner()
        spinner.set_spinning(True)
        spinner.start()
        self.status.set_title('Loading spaCy')
        self.status.set_child(spinner)
        self.viewstack = Adw.ViewStack()
        self.viewstack.connect("notify::visible-child", self._stack_page_changed)
        self.viewstack.add_titled_with_icon(self.dashboard, 'dashboard', 'Dashboard', 'com.github.t00m.Loro-dashboard-symbolic')
        self.stack_page_editor = self.viewstack.add_titled_with_icon(self.editor, 'workbooks', 'Workbooks', 'com.github.t00m.Loro-workbooks')
        self.viewstack.add_titled_with_icon(self.browser, 'browser', 'Reports', 'com.github.t00m.Loro-printer-symbolic')

        self.status_page = self.viewstack.add_titled_with_icon(self.status, 'status', 'Status', 'com.github.t00m.Loro-dialog-question-symbolic')
        self.status_page.set_visible(True)
        self.viewstack.set_visible_child_name('status')

        viewswitcher = Adw.ViewSwitcher()
        viewswitcher.set_valign(Gtk.Align.CENTER)
        viewswitcher.set_stack(self.viewstack)
        self.headerbar.set_title_widget(viewswitcher)
        self.mainbox.append(self.headerbar)
        self.mainbox.append(self.viewstack)
        self.set_content(self.mainbox)
        self.dashboard.update_dashboard()
        self.editor.connect('workbooks-updated', self.dashboard.update_dashboard)



        # Set widgets state
        self.btnSidebarLeft.set_active(True)
        self.btnRefresh.connect('clicked', self.update_workbook)

    def _stack_page_changed(self, viewstack, gparam):
        page = viewstack.get_visible_child_name()
        if page == 'workbooks':
            self.hboxDashboard.set_visible(False)
        else:
            self.hboxDashboard.set_visible(True)

    def _build_ui(self):
        self.set_title(_("Loro"))
        self.mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Headerbar with ViewSwitcher
        self.headerbar = Adw.HeaderBar()

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
        self.headerbar.pack_start(menu_btn)

        self.hboxDashboard = self.app.factory.create_box_horizontal(spacing=3, margin=0)
        self.btnSidebarLeft = self.app.factory.create_button_toggle(icon_name='com.github.t00m.Loro-sidebar-show-left-symbolic', callback=self.toggle_sidebar_left)
        self.hboxDashboard.append(self.btnSidebarLeft)

        self.ddWorkbooks = self.app.factory.create_dropdown_generic(Workbook, enable_search=True)
        # ~ self.ddWorkbooks.get_style_context().add_class(class_name='caption')
        self.ddWorkbooks.set_valign(Gtk.Align.CENTER)
        self.ddWorkbooks.connect("notify::selected-item", self._on_workbook_selected)
        self.ddWorkbooks.set_hexpand(False)
        self.hboxDashboard.append(self.ddWorkbooks)

        self.headerbar.pack_start(self.hboxDashboard)

        # ~ expander = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        self.btnRefresh = self.app.factory.create_button(icon_name=ICON['REFRESH'], tooltip='Refresh') #, callback=self._update_workbook)
        # ~ toolbox.append(expander)
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_show_text(False)
        self.progressbar.set_visible(False)
        self.headerbar.pack_end(self.progressbar)
        self.headerbar.pack_end(self.btnRefresh)

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

    def toggle_sidebar_left(self, toggle_button, data):
        visible = toggle_button.get_active()
        self.dashboard.sidebar_left.set_visible(visible)
        if visible:
            self.dashboard.sidebar_left.set_margin_start(6)
            self.dashboard.sidebar_left.set_margin_end(6)
        else:
            self.dashboard.sidebar_left.set_margin_start(0)
            self.dashboard.sidebar_left.set_margin_end(0)

    def get_dropdown_workbooks(self):
        return self.ddWorkbooks

    def _on_workbook_selected(self, *args):
        self.dashboard._on_workbook_selected()

    def _create_actions(self) -> None:
        """
        Create actions for main menu
        """
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
        _create_action(
            "status",
            lambda *_: StatusWindow(self).show(),
            ["<primary>comma"],
        )
        _create_action("about", _about)
        _create_action(
            "quit",
            lambda *_: self.props.application.quit(),
            ["<primary>q", "<primary>w"],
        )

    def update_workbook(self, *args):
        self.progressbar.set_visible(True)
        self.progressbar.set_show_text(True)
        RunAsync(self.pulse)
        RunAsync(self.dashboard._update_workbook)

    def pulse(self):
        # This function updates the progress bar every 1s.
        # ~ running = True
        while True:
            time.sleep(0.5)
            filename, fraction = self.app.workflow.get_progress()
            running = fraction > 0.0
            # ~ self.log.debug("progressbar visible? %s", running)
            if running:
                self.progressbar.set_fraction(fraction)
                self.progressbar.set_text(filename)
            else:
                self.progressbar.set_fraction(0.0)
            self.progressbar.set_visible(running)
            # ~ self.log.debug("%s > %f", filename, fraction)

