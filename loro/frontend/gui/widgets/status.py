#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: status.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Status pages
"""

from gi.repository import Adw, Gtk  # type:ignore

from loro.backend.core.log import get_logger
from loro.frontend.gui.icons import ICON

class StatusPage(Gtk.Box):
    __gtype_name__ = 'StatusPage'

    def __init__(self, app):
        super(StatusPage, self).__init__(orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.app = app
        self.log = get_logger(__class__.__name__)

        scw = Gtk.ScrolledWindow()
        scw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.mainbox = self.app.factory.create_box_vertical(hexpand=True, vexpand=True)
        scw.set_child(self.mainbox)
        self.append(scw)

        self.vbox_head = self.app.factory.create_box_vertical(spacing=12, margin=12, vexpand=False, hexpand=True)

        # Title
        self.hbox_title = self.app.factory.create_box_horizontal(spacing=12, margin=12, vexpand=False, hexpand=True)
        self.lblTitle = Gtk.Label()
        self.lblTitle.get_style_context().add_class(class_name='title-1')
        self.hbox_title.append(self.lblTitle)
        self.hbox_title.set_valign(Gtk.Align.END)
        self.hbox_title.set_halign(Gtk.Align.CENTER)
        self.vbox_head.append(self.hbox_title)

        # Description
        self.hbox_desc = self.app.factory.create_box_horizontal(spacing=12, margin=12, vexpand=False, hexpand=True)
        self.lblDesc = Gtk.Label()
        self.lblDesc.get_style_context().add_class(class_name='title-4')
        self.hbox_desc.append(self.lblDesc)
        self.hbox_desc.set_valign(Gtk.Align.START)
        self.hbox_desc.set_halign(Gtk.Align.CENTER)
        self.vbox_head.append(self.hbox_desc)

        self.mainbox.append(self.vbox_head)

    def set_title(self, title: str):
        self.lblTitle.set_markup(title)

    def set_description(self, description: str):
        self.lblDesc.set_markup(description)

class StatusPageNoWorkbooks(StatusPage):
    __gtype_name__ = 'StatusPageNoWorkbooks'

    def __init__(self, app):
        super(StatusPageNoWorkbooks, self).__init__(app)
        self.set_title('No workbooks available')
        self.set_description("Please, create a new one")
        self.hbox_title.set_valign(Gtk.Align.END)
        self.hbox_title.set_vexpand(True)


class StatusPageCurrentWorkbook(StatusPage):
    __gtype_name__ = 'StatusPageCurrentWorkbook'

    def __init__(self, app):
        super(StatusPageCurrentWorkbook, self).__init__(app)

        self.hbox_title.set_valign(Gtk.Align.START)
        self.hbox_title.set_vexpand(False)
        self.hbox_desc.set_valign(Gtk.Align.START)
        self.hbox_desc.set_vexpand(False)

        self.vbox_body = self.app.factory.create_box_vertical(spacing=12, margin=12, vexpand=True, hexpand=True)
        self.app.add_widget("status-body", self.vbox_body)

        # ~ # Toolbar
        # ~ toolbar = self.app.factory.create_box_horizontal()
        # ~ toolbar.get_style_context().add_class(class_name='card')
        # ~ toolbar.get_style_context().add_class(class_name='toolbar')
        # ~ toolbar.get_style_context().add_class(class_name='linked')
        # ~ self.app.add_widget('status-box-toolbar', toolbar)
        # ~ button_r = self.app.factory.create_button(icon_name=ICON['WB_REFRESH'], tooltip='Refresh/Compile workbook', callback=self.app.actions.workbook_compile)
        # ~ self.app.add_widget('status-workbook-refresh', button_r)
        # ~ button_e = self.app.factory.create_button(icon_name=ICON['WB_EDIT'], tooltip='Edit workbook', callback=self.app.actions.workbook_edit)
        # ~ self.app.add_widget('status-workbook-edit', button_e)
        # ~ button_d = self.app.factory.create_button(icon_name=ICON['WB_DELETE'], tooltip='Delete workbook', callback=self.app.actions.workbook_delete)
        # ~ self.app.add_widget('status-workbook-delete', button_d)
        # ~ button_d.get_style_context().add_class(class_name='error')
        # ~ toolbar.append(button_r)
        # ~ toolbar.append(button_e)
        # ~ toolbar.append(button_d)
        # ~ toolbar.set_valign(Gtk.Align.START)
        # ~ toolbar.set_halign(Gtk.Align.CENTER)
        # ~ self.vbox_body.append(toolbar)
        # ~ self.vbox_body.set_valign(Gtk.Align.START)
        # ~ self.vbox_body.set_halign(Gtk.Align.CENTER)

        vbox_topics = self.app.factory.create_box_vertical()
        vbox_topics.get_style_context().add_class(class_name='title-4')
        vbox_topics.set_halign(Gtk.Align.CENTER)
        vbox_topics.set_valign(Gtk.Align.START)
        self.lblTopics = Gtk.Label()
        self.lblSubtopics = Gtk.Label()
        vbox_topics.append(self.lblTopics)
        vbox_topics.append(self.lblSubtopics)
        self.vbox_body.append(vbox_topics)
        self.mainbox.append(self.vbox_body)

        # Progressbar box
        hbox = self.app.factory.create_box_horizontal(hexpand=True, vexpand=True)
        self.app.add_widget('status-box-progressbar', hbox)
        progressbar = self.app.add_widget('progressbar', Gtk.ProgressBar())
        progressbar.set_hexpand(True)
        progressbar.set_valign(Gtk.Align.CENTER)
        progressbar.set_show_text(True)
        hbox.append(progressbar)
        hbox.set_valign(Gtk.Align.CENTER)
        hbox.set_halign(Gtk.Align.FILL)
        hbox.set_margin_start(36)
        hbox.set_margin_end(36)
        hbox.set_visible(False)
        self.mainbox.append(hbox)

    def set_topics(self, workbook: str):
        self.lblTopics.set_markup('<b>Topics: %s</b>' % ', '.join(self.app.cache.get_topics(workbook)))
        self.lblSubtopics.set_markup('<b>Subtopics: %s</b>' % ', '.join(self.app.cache.get_subtopics(workbook)))
