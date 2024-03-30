#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import threading
from gi.repository import Gio, Adw, GLib, Gtk  # type:ignore

from loro.backend.core.run_async import RunAsync
from loro.frontend.gui.models import Item, Topic, Subtopic, POSTag, Token, Sentence, Analysis, Workbook
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.widgets.views import ColumnViewToken
from loro.frontend.gui.widgets.views import ColumnViewSentences
from loro.frontend.gui.widgets.views import ColumnViewAnalysis
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.core.util import find_item
from loro.backend.core.log import get_logger
from loro.backend.services.nlp.spacy import explain_term
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_project_target_dir
from loro.backend.core.util import get_project_target_workbook_dir
from loro.frontend.gui.icons import ICON

class Dashboard(Gtk.Box):
    __gtype_name__ = 'Dashboard'
    counter = 0

    def __init__(self, app):
        super(Dashboard, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        __class__.counter += 1
        self.log = get_logger('Dashboard')
        self.app = app
        self.current_topic = 'ALL'
        self.current_subtopic = 'ALL'
        self.current_postag = 'ALL'
        self.selected = []
        self.selected_tokens = []
        self.selected_workbook = None
        self._build_dashboard()
        # ~ self.app.workflow.connect('workflow-finished', self._on_workbook_selected)
        GLib.timeout_add(interval=500, function=self.update_dashboard)
        # ~ self.update_dashboard()

    def _build_dashboard(self):
        self.set_margin_top(margin=0)
        self.set_margin_end(margin=6)
        self.set_margin_bottom(margin=6)
        self.set_margin_start(margin=0)

        # Toolbox
        # ~ toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)

        # ~ self.ddTopics = self.app.factory.create_dropdown_generic(Item, enable_search=True)
        # ~ self.ddTopics.connect("notify::selected-item", self._on_topic_selected)
        # ~ self.ddTopics.set_hexpand(False)
        # ~ toolbox.append(self.ddTopics)

        # ~ self.ddSubtopics = self.app.factory.create_dropdown_generic(Item, enable_search=True)
        # ~ self.ddSubtopics.connect("notify::selected-item", self._on_subtopic_selected)
        # ~ self.ddSubtopics.set_hexpand(False)
        # ~ toolbox.append(self.ddSubtopics)

        # ~ expander = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True)
        # ~ self.btnRefresh = self.app.factory.create_button(icon_name=ICON['REFRESH'], tooltip='Refresh', callback=self._update_workbook)
        # ~ toolbox.append(expander)
        # ~ toolbox.append(self.btnRefresh)

        # ~ self.append(toolbox)

        # Content View
        dashboard = self.app.factory.create_box_horizontal(hexpand=True, vexpand=True)
        dashboard.set_margin_top(margin=6)

        ## Wdigets distribution
        self.btnSidebarLeft = self.app.factory.create_button_toggle(icon_name='com.github.t00m.Loro-sidebar-show-left-symbolic', callback=self.toggle_sidebar_left)
        self.btnRefresh = self.app.factory.create_button(icon_name=ICON['REFRESH'], tooltip='Refresh', width=16, callback=self.update_workbook)
        self.btnReport = self.app.factory.create_button(icon_name='com.github.t00m.Loro-printer-symbolic', tooltip='Workbook report', width=16, callback=self.display_report)

        # ~ self.btnRefresh.connect('clicked', self.update_workbook)
        self.toolbar_left = self.app.factory.create_box_vertical(spacing=6, hexpand=False, vexpand=True)
        self.toolbar_left.set_margin_start(margin=0)
        self.toolbar_left.set_margin_end(margin=0)
        self.toolbar_left.append(self.btnSidebarLeft)
        self.toolbar_left.append(self.btnReport)
        self.toolbar_left.append(self.btnRefresh)
        self.sidebar_left = self.app.factory.create_box_horizontal(spacing=6, hexpand=False, vexpand=True)
        self.sidebar_left.append(self.toolbar_left)
        self.sidebar_left.set_margin_start(margin=0)
        self.sidebar_left.set_margin_end(margin=6)
        self.sidebar_right_up = self.app.factory.create_box_vertical(spacing=6, hexpand=True, vexpand=True)
        self.sidebar_right_up.set_margin_bottom(margin=6)
        self.sidebar_right_up.set_margin_start(margin=6)
        self.sidebar_right_down = self.app.factory.create_box_vertical(spacing=6, hexpand=True, vexpand=True)
        self.sidebar_right_down.set_margin_top(margin=6)
        self.sidebar_right_down.set_margin_start(margin=6)
        self.vpaned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.hpaned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.hpaned.set_start_child(self.sidebar_left)
        self.hpaned.set_end_child(self.vpaned)
        self.vpaned.set_start_child(self.sidebar_right_up)
        self.vpaned.set_end_child(self.sidebar_right_down)
        dashboard.append(self.hpaned)

        frame = Gtk.Frame()
        vbox = self.app.factory.create_box_vertical(vexpand=True, hexpand=True)
        self.ddPos = self.app.factory.create_dropdown_generic(Item, enable_search=True)
        self.ddPos.connect("notify::selected-item", self._on_postag_selected)
        self.ddPos.set_hexpand(False)
        vbox.append(self.ddPos)

        self.cvtokens = ColumnViewToken(self.app)
        self.cvtokens.get_style_context().add_class(class_name='monospace')
        selection = self.cvtokens.get_selection()
        selection.connect('selection-changed', self._on_tokens_selected)
        vbox.append(self.cvtokens)
        frame.set_child(vbox)
        self.sidebar_left.append(frame)

        frame = Gtk.Frame()
        self.cvsentences = ColumnViewSentences(self.app)
        self.cvsentences.get_style_context().add_class(class_name='monospace')
        selection = self.cvsentences.get_selection()
        selection.connect('selection-changed', self._on_sentence_selected)
        self.cvsentences.set_hexpand(True)
        self.cvsentences.set_vexpand(True)
        frame.set_child(self.cvsentences)
        self.sidebar_right_up.append(frame)

        frame = Gtk.Frame()
        self.cvanalysis = ColumnViewAnalysis(self.app)
        self.cvanalysis.get_style_context().add_class(class_name='monospace')
        self.cvanalysis.set_hexpand(True)
        self.cvanalysis.set_vexpand(True)
        frame.set_child(self.cvanalysis)
        self.sidebar_right_down.append(frame)

        self.append(dashboard)
        self.btnSidebarLeft.set_active(True)

    def toggle_sidebar_left(self, toggle_button, data):
        visible = toggle_button.get_active()
        # ~ self.log.debug("Left sidebar visible? %s", visible)
        # ~ if visible:
            # ~ self.hpaned.set_position(self.cur_pos)
        # ~ else:
            # ~ self.hpaned.set_position(0)
        # ~ self.hpaned.set_visible(visible)

        # ~ if visible:
            # ~ self.dashboard.sidebar_left.set_margin_start(6)
            # ~ self.dashboard.sidebar_left.set_margin_end(6)
        # ~ else:
            # ~ self.dashboard.sidebar_left.set_margin_start(0)
            # ~ self.dashboard.sidebar_left.set_margin_end(0)

    def display_report(self, *args):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        # ~ self.log.debug("Loading report for Workbook '%s'", workbook.id)
        source, target = ENV['Projects']['Default']['Languages']
        DIR_OUTPUT = get_project_target_workbook_dir(source, target, workbook.id)
        report_url = os.path.join(DIR_OUTPUT, '%s.html' % workbook.id)
        # ~ self.app.builder.kb(workbook.id)
        report = self.app.report.build(workbook.id)
        browser = self.app.get_widget('browser')
        browser.load_url(report)
        # ~ os.system("xdg-open '%s'" % report_url)

    def _update_analysis(self, sid: str):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        tokens = self.app.dictionary.get_tokens(workbook.id)
        sentences = self.app.dictionary.get_sentences(workbook.id)
        items = []
        for token in sentences[sid]['tokens']:
            items.append(Analysis(
                                id = token,
                                title = token,
                                lemma = tokens[token]['lemmas'][0],
                                postag = explain_term(tokens[token]['postags'][0]),
                                count = tokens[token]['count'],
                                translation = ''
                            )
                        )
        self.cvanalysis.update(items)

    def _update_sentences(self, token: Token):
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        tokens = self.app.dictionary.get_tokens(workbook.id)
        matches = []
        try:
            token_sids = tokens[token.id]['sentences']
            for token_sid in token_sids:
                matches.append(token_sid)
            sentences = self.app.dictionary.get_sentences(workbook.id)
            items = []
            for sid in matches:
                sentence = sentences[sid]['DE']
                items.append(Sentence(id=sid, title=sentence))
        except Exception as error:
            self.log.error(error)
            raise
            items = []
            items.append(Sentence(id='#ERROR#', title=error))
        self.cvsentences.update(items)
        self.log.info("Workbook['%s'] Token['%s']: %d sentences", workbook.id, token.id, len(matches))

    def _on_tokens_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            token = model.get_item(pos)
            self._update_sentences(token)

            # ~ self.selected_tokens.append(item.id)
        # ~ self.log.info("%d / %d" % (len(self.selected_tokens), len(model)))

    def _on_sentence_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            sentence = model.get_item(pos)
        self._update_analysis(sentence.id)

    def _on_workbook_selected(self, *args):
        self.clear_dashboard()
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook is None:
            return

        if workbook.id is None:
            window = self.app.get_widget('window')
            editor = self.app.get_widget('editor')
            window.show_stack_page('workbooks')
            editor._on_workbook_add()
            return

        stats = self.app.stats.get(workbook.id)
        tokens = self.app.dictionary.get_tokens(workbook.id)
        workbook_empty = len(tokens) == 0

        # Update POS Dropbox
        postags = set()
        for key in tokens:
            for postag in tokens[key]['postags']:
                postags.add(postag)

        data = []
        data.append(("ALL", "All Parts Of Speech"))
        for postag in postags:
            title = explain_term(postag).title()
            data.append((postag, explain_term(postag).title()))
        self.app.actions.dropdown_populate(self.ddPos, POSTag, data)
        self.log.debug("Workbook['%s'] selected", workbook.id)

    def clear_dashboard(self):
        self.cvtokens.clear()
        self.cvsentences.clear()
        self.cvanalysis.clear()

    def update_workbook(self, *args):
        window = self.app.get_widget('window')
        progressbar = self.app.get_widget('progressbar')


        RunAsync(self._update_workbook)
        RunAsync(window.pulse)
        # ~ self._update_workbook()

    def _update_workbook(self, *args):
        window = self.app.get_widget('window')
        if window is None:
            self.log.warning("Window still not ready! Keep waiting...")
            return True
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        if workbook is None:
            return
        self.log.debug("Workbook['%s'] update requested", workbook.id)

        # ~ #FIXME: somehow, when the workflow emits the signal, it provokes
        # ~ # core dumps
        # ~ self.app.workflow.connect('workflow-finished', self.update_dashboard)

        files = self.app.workbooks.get_files(workbook.id)
        # ~ GLib.idle_add(self.app.workflow.start, workbook.id, files)
        # ~ event = threading.Event()
        self.app.workflow.start(workbook.id, files)
        # ~ event.wait()
        self.set_current_workbook(workbook)
        # ~ self.log.debug("Current workbook: %s", workbook.title)

    def _on_topic_selected(self, *args):
        current_topic = self.ddTopics.get_selected_item()
        if current_topic is None:
            return
        # ~ self.log.debug("Topic selected: '%s'", current_topic.id)
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        topics = self.app.dictionary.get_topics(workbook.id)
        # ~ self.log.debug("Displaying subtopics for topic '%s'", current_topic.id)
        data = []
        data.append(("ALL", "All subtopics"))
        if current_topic.id == "ALL":
            all_subs = set()
            for topic in topics:
                for subtopic in topics[topic]:
                    all_subs.add(subtopic)
            for subtopic in all_subs:
                data.append((subtopic.upper(), subtopic.title()))
        else:
            subtopics = topics[current_topic.id]
            for subtopic in subtopics:
                data.append((subtopic, subtopic.title()))
        self.app.actions.dropdown_populate(self.ddSubtopics, Subtopic, data)

        if len(self.ddSubtopics.get_model()) > 0:
            self.ddSubtopics.set_selected(0)

    def _on_subtopic_selected(self, dropdown, gparam):
        current_topic = self.ddTopics.get_selected_item()
        current_subtopic = dropdown.get_selected_item()
        if current_topic is None:
            return
        if current_subtopic is None:
            return

        selected = []
        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        tokens = self.app.dictionary.get_tokens(workbook.id)
        for key in tokens.keys():
            if current_topic.id == 'ALL':
                if current_subtopic.id == 'ALL':
                    selected.append(key)
                else:
                    if current_subtopic.id in tokens[key]['subtopics']:
                        selected.append(key)
            else:
                if current_topic.id in tokens[key]['topics']:
                    if current_subtopic.id == 'ALL':
                        selected.append(key)
                    else:
                        if current_subtopic.id in tokens[key]['subtopics']:
                            selected.append(key)

        self.selected_tokens = selected
        # ~ self.log.info("Selected %d tokens for topic '%s' and subtopic '%s'", len(self.selected_tokens), current_topic.id, current_subtopic.id)

        # Update POS
        postags = set()
        for key in self.selected_tokens:
            for postag in tokens[key]['postags']:
                postags.add(postag)

        data = []
        data.append(("ALL", "All Part-Of-Speech tags"))
        for postag in postags:
            title = explain_term(postag).title()
            data.append((postag, explain_term(postag).title()))
        self.app.actions.dropdown_populate(self.ddPos, POSTag, data)

        # ~ self.app.actions.dropdown_populate(self.ddPos, Item, data)

        # ~ if matches:
        # ~ if len(dropdown.get_model()) > 0:
            # ~ # This is necessary. When Topic selection changes, subtopics
            # ~ # dropdown has no items and this fails

            # ~ items = []

            # ~ for key in tokens.keys():

    def _on_postag_selected(self, dropdown, gparam):
        if len(dropdown.get_model()) > 0:
            ddWorkbooks = self.app.get_widget('dropdown-workbooks')
            workbook = ddWorkbooks.get_selected_item()
            current_postag = dropdown.get_selected_item()
            postag = current_postag.id
            stats = self.app.stats.get(workbook.id)
            # ~ self.log.debug("Stats: %s", stats)
            # ~ return

            # ~ if stats is None:
                # ~ self._update_workbook()
                # ~ return
            # ~ self.log.debug(stats['postags'])

            if postag =='ALL':
                tokens = self.app.dictionary.get_tokens(workbook.id)
                selected = list(tokens.keys())
            else:
                selected = []
                for token in stats['postags'][postag]['tokens']:
                    selected.append(token)

            items = []
            lenmax = 25
            for key in selected:
                items.append(Token(id=key, title=key))
                if len(key) > lenmax:
                    lenmax = len(key)
            self.cvtokens.update(items)
            self.log.debug("Workbook['%s'] POStag['%s']: %d tokens", workbook.id, postag, len(selected))
            if lenmax < 25:
                lenmax = 25
            self.cur_pos = self.hpaned.get_position()
            new_pos = lenmax*10
            self.hpaned.set_position(new_pos)

    def update_dashboard(self, *args):
        self.log.debug('Updating dashboard')
        window = self.app.get_widget('window')
        if window is None:
            # ~ self.log.warning("Window still not ready! Keep waiting...")
            return True

        ddWorkbooks = self.app.get_widget('dropdown-workbooks')
        workbook = ddWorkbooks.get_selected_item()
        # ~ if self.selected_workbook is not None:
            # ~ self.log.debug("Trying to display saved workbook '%s'", self.selected_workbook.title)
            # ~ model = ddWorkbooks.get_model()
            # ~ pos = find_item(model, self.selected_workbook)
            # ~ item = model[pos]
            # ~ ddWorkbooks.set_selected(pos)

        self._on_workbook_selected(ddWorkbooks)
        return False

    def set_current_workbook(self, workbook: Workbook):
        self.selected_workbook = workbook
