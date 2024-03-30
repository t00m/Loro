#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: browser.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Web browser module based on WebKit
# https://lazka.github.io/pgi-docs/WebKit2-4.0/classes/WebView.html
# https://lazka.github.io/pgi-docs/WebKit2-4.0/classes/PolicyDecision.html#WebKit2.PolicyDecision
# https://lazka.github.io/pgi-docs/WebKit2-4.0/enums.html#WebKit2.PolicyDecisionType
"""

import os
import sys
import logging

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Soup', '3.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Soup
from gi.repository import WebKit

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.run_async import RunAsync
from loro.backend.core.util import get_project_target_workbook_dir


class Browser(Gtk.Box):
    __gtype_name__ = 'Browser'

    def __init__(self, app):
        super(Browser, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.log = get_logger('Browser')
        # ~ logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        self._setup_widget()
        self.log.debug("Browser initialized")
        self.app.report.connect('report-finished', self.load_report)
        # ~ loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        # ~ self.log.debug(loggers)

    def _setup_widget(self):
        # Webkit context
        # ~ self.web_context = WebKit.WebContext.get_default()
        # ~ self.web_context.set_cache_model(WebKit.CacheModel.DOCUMENT_VIEWER)
        # ~ self.web_context.set_process_model(WebKit.ProcessModel.MULTIPLE_SECONDARY_PROCESSES)
        # ~ web_context.register_uri_scheme('basico', self._on_basico_scheme)

        # Webkit settings
        # ~ self.web_settings = WebKit.Settings()
        # ~ self.web_settings.set_enable_smooth_scrolling(True)
        # ~ self.web_settings.set_enable_plugins(False)

        # ~ WebKit.WebView.__init__(self,
                                 # ~ web_context=self.web_context,
                                 # ~ settings=self.web_settings)
        # ~ self.connect('context-menu', self._on_append_items)
        toolbar = self.app.factory.create_box_horizontal(hexpand=True, vexpand=False)
        toolbar.get_style_context().add_class(class_name='toolbar')
        self.app.add_widget('browser-toolbar', toolbar)
        btnPrint = self.app.factory.create_button(icon_name='com.github.t00m.Loro-printer-symbolic', callback=self.print_report)
        toolbar.append(btnPrint)
        self.wv = self.app.add_widget('browser-webview', WebKit.WebView())
        self.wv.connect('decide-policy', self._on_decide_policy)
        self.wv.connect('load-changed', self._on_load_changed)
        self.wv.connect('load-failed',self._on_load_failed)
        self.wv.set_hexpand(True)
        self.wv.set_vexpand(True)
        self.append(toolbar)
        self.append(self.wv)
        self.set_hexpand(True)
        self.set_vexpand(True)

    def print_report(self, *args):
        printOperation = WebKit.PrintOperation.new(self.wv)
        printOperation.run_dialog()

    def _get_api(self, uri):
        """Use Soup.URI to split uri
        Args:
            uri (str)
        Returns:
            A list with two strings representing a path and fragment
        """
        path = None
        fragment = None

        if uri:
            soup_uri = Soup.URI.new(uri)
            action = soup_uri.host
            args = soup_uri.path.split('/')[1:]

        return [action, args]

    def _on_append_items(self, webview, context_menu, hit_result_event, event):
        """Attach custom actions to browser context menu"""
        # ~ # Example:
        # ~ action = Gtk.Action("help", "Basico Help", None, None)
        # ~ action.connect("activate", self.display_help)
        # ~ option = WebKit.ContextMenuItem().new(action)
        # ~ context_menu.prepend(option)
        pass


    def load_url(self, url: str):
        self.log.debug("Loading url")
        if not url.startswith('file://'):
            url = 'file://%s' % url
        self.wv.load_uri(url)

    def load_report(self, *args):
        ddWorkbooks = self.app.get_widget('dd-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        # ~ self.log.debug("Loading report for Workbook '%s'", workbook.id)
        source, target = ENV['Projects']['Default']['Languages']
        DIR_OUTPUT = get_project_target_workbook_dir(source, target, workbook.id)
        report_url = os.path.join(DIR_OUTPUT, '%s.html' % workbook.id)
        # ~ self.log.debug(report_url)
        self.load_url(report_url)
        # ~ self.load_url('file:///home/t00m/Documentos/Loro/Projects/DE/output/EN/A1/A1.html')
        # ~ GLib.idle_add(self.load_report_url)
        # ~ self.log.debug("Report loaded")

    def load_report_url(self):
        # ~ content = open(self.report_url, 'r').read()
        # ~ self.load_html(content=content)
        self.load_url(self.report_url)

    def _on_decide_policy(self, webview, decision, decision_type):
        """Decide what to do when clicked on link
        Args:
            webview (WebKit2.WebView)
            decision (WebKit2.PolicyDecision)
            decision_type (WebKit2.PolicyDecisionType)
        Returns:
            True to stop other handlers from being invoked for the event.
            False to propagate the event further.
        """
        if decision_type is WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            action = WebKit.NavigationPolicyDecision.get_navigation_action(decision)
            uri = webview.get_uri()
            filename = uri[7:]
            self.log.debug("URL intercepted: %s", uri)
            self.log.debug("Filename: %s", filename)
            if not os.path.exists(filename):
                self.log.error("Page %s not found", os.path.basename(filename))
                return True
            click = action.get_mouse_button() != 0
            if click:
                self.log.debug("User clicked in link: %s", uri)

    def _on_load_changed(self, webview, event):
        uri = webview.get_uri()
        if event == WebKit.LoadEvent.STARTED:
            self.log.debug("Load started for url: %s", uri)
        elif event == WebKit.LoadEvent.COMMITTED:
            self.log.debug("Load committed for url: %s", uri)
        elif event == WebKit.LoadEvent.FINISHED:
            self.log.debug("Load finished for url: %s", uri)
            if len(uri) == 0:
                self.log.debug("Url not loaded")

    def _on_load_failed(self, webview, load_event, failing_uri, error):
        self.log.error(error)
        self.load_url('file://error_404.html')