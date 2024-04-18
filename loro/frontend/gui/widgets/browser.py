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
from loro.backend.core.util import get_default_languages


class Browser(Gtk.Box):
    __gtype_name__ = 'Browser'

    def __init__(self, app):
        super(Browser, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.log = get_logger('Browser')
        # ~ logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger("urllib3").setLevel(logging.CRITICAL)
        self._setup_widget()
        self._connect_signals()
        self.wv.load_uri('') # webkit-pdfjs-viewer://pdfjs/web/viewer.html?file=)
        self.log.debug("Browser initialized")
        # ~ self.app.report.connect('report-finished', self.load_reports)
        # ~ loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        # ~ self.log.debug(loggers)

    def _connect_signals(self):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        ddWorkbooks.connect("notify::selected-item", self.update)

    def _setup_widget(self):
        # Webkit context
        self.web_context = WebKit.WebContext.get_default()
        self.web_context.set_cache_model(WebKit.CacheModel.DOCUMENT_BROWSER)

        # Webkit settings
        self.web_settings = WebKit.Settings()
        self.web_settings.set_enable_smooth_scrolling(True)
        self.web_settings.set_allow_file_access_from_file_urls(True)
        self.web_settings.set_enable_html5_local_storage(True)
        self.web_settings.set_enable_html5_database(True)
        self.web_settings.set_enable_page_cache(True)
        self.web_settings.set_enable_offline_web_application_cache(True)
        self.web_settings.set_allow_file_access_from_file_urls(True)
        self.web_settings.set_allow_modal_dialogs(True)
        self.web_settings.set_allow_top_navigation_to_data_urls(True)
        self.web_settings.set_allow_universal_access_from_file_urls(True)
        self.web_settings.set_auto_load_images(True)
        self.web_settings.set_disable_web_security(True)
        self.web_settings.set_enable_back_forward_navigation_gestures(True)
        self.web_settings.set_enable_caret_browsing(True)
        self.web_settings.set_enable_developer_extras(True)
        self.web_settings.set_enable_dns_prefetching(True)
        self.web_settings.set_enable_encrypted_media(True)
        self.web_settings.set_enable_fullscreen(True)
        self.web_settings.set_enable_html5_database(True)
        self.web_settings.set_enable_html5_local_storage(True)
        self.web_settings.set_enable_hyperlink_auditing(True)
        self.web_settings.set_enable_javascript(True)
        self.web_settings.set_enable_javascript_markup(True)
        self.web_settings.set_enable_media(True)
        self.web_settings.set_enable_media_capabilities(True)
        self.web_settings.set_enable_media_stream(True)
        self.web_settings.set_enable_mediasource(True)
        self.web_settings.set_enable_mock_capture_devices(True)
        self.web_settings.set_enable_offline_web_application_cache(True)
        self.web_settings.set_enable_page_cache(True)
        self.web_settings.set_enable_resizable_text_areas(True)
        self.web_settings.set_enable_site_specific_quirks(True)
        self.web_settings.set_enable_smooth_scrolling(True)
        self.web_settings.set_enable_spatial_navigation(True)
        self.web_settings.set_enable_tabs_to_links(True)
        self.web_settings.set_enable_webaudio(True)
        self.web_settings.set_enable_webgl(True)
        self.web_settings.set_enable_webrtc(True)
        self.web_settings.set_enable_write_console_messages_to_stdout(True)
        self.web_settings.set_javascript_can_access_clipboard(True)
        self.web_settings.set_javascript_can_open_windows_automatically(True)
        self.web_settings.set_media_playback_allows_inline(True)
        self.web_settings.set_media_playback_requires_user_gesture(True)

        WebKit.WebView.__init__(self,
                     web_context=self.web_context,
                     settings=self.web_settings)

        # ~ self.connect('context-menu', self._on_append_items)

        # ~ toolbar = self.app.factory.create_box_horizontal(hexpand=True, vexpand=False)

        toolbar = self.app.add_widget('browser-toolbar', Gtk.CenterBox())
        toolbar.get_style_context().add_class(class_name='toolbar')
        toolbar.get_style_context().add_class(class_name='linkded')
        hboxButtons = self.app.factory.create_box_horizontal()
        btnPDFReport = self.app.factory.create_button(title='PDF Report', callback=self.load_report_pdf)
        btnWebReport = self.app.factory.create_button(title='Web Report', callback=self.load_report_html)
        hboxButtons.append(btnPDFReport)
        hboxButtons.append(btnWebReport)
        toolbar.set_center_widget(hboxButtons)
        # ~ btnPrint = self.app.factory.create_button(icon_name='com.github.t00m.Loro-printer-symbolic', width=16, callback=self.print_report)
        # ~ toolbar.set_end_widget(btnPrint)


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

    def display_help(self, *args):
        self.log.debug(args)

    def load_url(self, url: str):
        if not url.startswith('file://'):
            url = 'file://%s' % url
        self.wv.load_uri(url)
        # ~ self.log.debug("URL %s loaded", url)

    def _get_workbook_html_dir(self):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        return os.path.join(get_project_target_workbook_dir(workbook.id), 'html')

    def load_report_pdf(self, *args):
        output_dir = self._get_workbook_html_dir()
        pdf_report = os.path.join(output_dir, 'report.pdf')
        self.load_url(pdf_report)

    def load_report_html(self, *args):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        # ~ self.log.debug("Loading report for Workbook '%s'", workbook.id)
        source, target = get_default_languages()
        DIR_OUTPUT = os.path.join(get_project_target_workbook_dir(workbook.id), 'html')
        report_url = os.path.join(DIR_OUTPUT, '%s.html' % workbook.id)
        self.log.debug(report_url)
        self.load_url(report_url)
        self.log.debug("Web Report loaded")

    def load_landing_page(self, workflow, workbook: str):
        url = self.app.report.build_landing_page(workbook)
        self.log.debug("Landing page: %s", url)
        self.load_url(url)

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
            # ~ self.log.debug("URL intercepted: %s", uri)
            # ~ self.log.debug("Filename: %s", filename)
            if not os.path.exists(filename):
                self.log.error("Page %s not found", os.path.basename(filename))
                return True
            # ~ click = action.get_mouse_button() != 0
            # ~ if click:
                # ~ self.log.debug("User clicked in link: %s", uri)

    def _on_load_changed(self, webview, event):
        uri = webview.get_uri()
        # ~ if event == WebKit.LoadEvent.STARTED:
            # ~ self.log.debug("Load started for url: %s", uri)
        # ~ elif event == WebKit.LoadEvent.COMMITTED:
            # ~ self.log.debug("Load committed for url: %s", uri)
        # ~ elif event == WebKit.LoadEvent.FINISHED:
            # ~ self.log.debug("Load finished for url: %s", uri)
            # ~ if len(uri) == 0:
                # ~ self.log.debug("Url not loaded")

    def _on_load_failed(self, webview, load_event, failing_uri, error):
        self.log.error(error)
        self.load_url('file://error_404.html')

    def update(self, *args):
        pass
