#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations
from gi.repository import Gio, Adw, Gtk  # type:ignore

from loro.frontend.gui.factory import WidgetFactory
from loro.frontend.gui.actions import WidgetActions
from loro.frontend.gui.models import Item, Topic, Subtopic, POSTag, Token, Sentence, Analysis
from loro.frontend.gui.widgets.columnview import ColumnView
from loro.frontend.gui.widgets.views import ColumnViewToken
from loro.frontend.gui.widgets.views import ColumnViewSentences
from loro.frontend.gui.widgets.views import ColumnViewAnalysis
from loro.backend.core.env import ENV
from loro.backend.core.util import json_load
from loro.backend.core.log import get_logger
from loro.backend.services.nlp.spacy import explain_term

class Dashboard(Gtk.Box):
    __gtype_name__ = 'Dashboard'

    def __init__(self, app):
        super(Dashboard, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.log = get_logger('Dashboard')
        self.app = app

        self.actions = WidgetActions(self.app)
        self.factory = WidgetFactory(self.app)
        self.current_topic = 'ALL'
        self.current_subtopic = 'ALL'
        self.current_postag = 'ALL'
        self.selected = []
        self.selected_tokens = []

        self._build_dashboard()
        self._update_dashboard()


    def _build_dashboard(self):
        self.set_margin_top(margin=6)
        self.set_margin_end(margin=6)
        self.set_margin_bottom(margin=6)
        self.set_margin_start(margin=6)

        # Toolbox
        toolbox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True)

        self.ddTopics = self.factory.create_dropdown_generic(Item, enable_search=True)
        self.ddTopics.connect("notify::selected-item", self._on_topic_selected)
        self.ddTopics.set_hexpand(False)
        toolbox.append(self.ddTopics)

        self.ddSubtopics = self.factory.create_dropdown_generic(Item, enable_search=True)
        self.ddSubtopics.connect("notify::selected-item", self._on_subtopic_selected)
        self.ddSubtopics.set_hexpand(False)
        toolbox.append(self.ddSubtopics)

        self.ddPos = self.factory.create_dropdown_generic(Item, enable_search=True)
        self.ddPos.connect("notify::selected-item", self._on_postag_selected)
        self.ddPos.set_hexpand(False)
        toolbox.append(self.ddPos)

        self.append(toolbox)

        # Content View
        dashboard = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, hexpand=True, vexpand=True)
        dashboard.set_margin_top(margin=6)

        ## Wdigets distribution
        self.boxLeft = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=False, vexpand=True)
        self.boxLeft.set_margin_end(margin=6)
        self.boxRightUp = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.boxRightUp.set_margin_bottom(margin=6)
        self.boxRightUp.set_margin_start(margin=6)
        self.boxRightDown = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True)
        self.boxRightDown.set_margin_top(margin=6)
        self.boxRightDown.set_margin_start(margin=6)
        self.vpaned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self.hpaned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.hpaned.set_start_child(self.boxLeft)
        self.hpaned.set_end_child(self.vpaned)
        self.vpaned.set_start_child(self.boxRightUp)
        self.vpaned.set_end_child(self.boxRightDown)
        dashboard.append(self.hpaned)

        self.cvtokens = ColumnViewToken(self.app)
        self.cvtokens.get_style_context().add_class(class_name='monospace')
        selection = self.cvtokens.get_selection()
        selection.connect('selection-changed', self._on_tokens_selected)
        self.boxLeft.append(self.cvtokens)

        self.cvsentences = ColumnViewSentences(self.app)
        self.cvsentences.get_style_context().add_class(class_name='monospace')
        selection = self.cvsentences.get_selection()
        selection.connect('selection-changed', self._on_sentence_selected)
        self.cvsentences.set_hexpand(True)
        self.cvsentences.set_vexpand(True)
        self.boxRightUp.append(self.cvsentences)

        self.cvanalysis = ColumnViewAnalysis(self.app)
        self.cvanalysis.get_style_context().add_class(class_name='monospace')
        self.cvanalysis.set_hexpand(True)
        self.cvanalysis.set_vexpand(True)
        self.boxRightDown.append(self.cvanalysis)

        self.append(dashboard)



    def _update_analysis(self, sid: str):
        tokens = self.app.dictionary.get_tokens()
        sentences = self.app.dictionary.get_sentences()
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
        tokens = self.app.dictionary.get_tokens()
        all_topics = self.app.dictionary.get_topics()
        selected_topic = self.ddTopics.get_selected_item().id
        selected_subtopic = self.ddSubtopics.get_selected_item().id
        matches = []
        token_sids = tokens[token.id]['sentences']

        for token_sid in token_sids:
            if selected_topic == 'ALL':
                for this_topic in all_topics:
                    if selected_subtopic == 'ALL':
                        for this_subtopic in all_topics[this_topic]:
                            if token_sid in all_topics[this_topic][this_subtopic]:
                                matches.append(token_sid)
                    else:
                        if token_sid in all_topics[this_topic][selected_subtopic]:
                            matches.append(token_sid)
            else:
                if selected_subtopic == 'ALL':
                    for this_subtopic in all_topics[selected_topic]:
                        if token_sid in all_topics[selected_topic][this_subtopic]:
                            matches.append(token_sid)
                else:
                    if token_sid in all_topics[selected_topic][selected_subtopic]:
                        matches.append(token_sid)

                # ~ for sid in topics[topic.id][subtopic.id]:
                # ~ if token_sid == sid:
                    # ~ matches.append(sid)
        self.log.debug("Displaying sentences for Topic['%s'] and Subtopic['%s']", selected_topic, selected_subtopic)
        sentences = self.app.dictionary.get_sentences()
        items = []
        for sid in matches:
            sentence = sentences[sid]['de']
            items.append(Sentence(id=sid, title=sentence))
        self.cvsentences.update(items)

        # ~ for topic in token_topics:
            # ~ for subtopic in topics[topic]:
                # ~ for sid in tokens[token.id]['sentences']:
                    # ~ if sid in topics[topic][subtopic]:
                        # ~ self.log.info("Token %s found in %s > %s:", token.id, topic, subtopic)
                        # ~ self.log.info("\t%s", sid)

    def _on_tokens_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            token = model.get_item(pos)
            self.log.info("%s > %s", token.id, token.title)
            self._update_sentences(token)

            # ~ self.selected_tokens.append(item.id)
        # ~ self.log.info("%d / %d" % (len(self.selected_tokens), len(model)))

    def _on_sentence_selected(self, selection, position, n_items):
        model = selection.get_model()
        bitset = selection.get_selection()
        for index in range(bitset.get_size()):
            pos = bitset.get_nth(index)
            sentence = model.get_item(pos)
            self.log.info("%s", sentence.title)
        self._update_analysis(sentence.id)


    def _on_topic_selected(self, *args):
        current_topic = self.ddTopics.get_selected_item()
        topics = self.app.dictionary.get_topics()
        self.log.debug("Displaying subtopics for topic '%s'", current_topic.id)
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
        self.actions.dropdown_populate(self.ddSubtopics, Subtopic, data)

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
        tokens = self.app.dictionary.get_tokens()
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
        self.log.info("Selected %d tokens for topic '%s' and subtopic '%s'", len(self.selected_tokens), current_topic.id, current_subtopic.id)

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
        self.actions.dropdown_populate(self.ddPos, POSTag, data)

        # ~ self.actions.dropdown_populate(self.ddPos, Item, data)

        # ~ if matches:
        # ~ if len(dropdown.get_model()) > 0:
            # ~ # This is necessary. When Topic selection changes, subtopics
            # ~ # dropdown has no items and this fails

            # ~ items = []

            # ~ for key in tokens.keys():


    def _on_postag_selected(self, dropdown, gparam):
        tokens = self.app.dictionary.get_tokens()
        if len(dropdown.get_model()) > 0:
            current_postag = dropdown.get_selected_item()
            postag = current_postag.id
            selected = []
            for key in self.selected_tokens:
                if postag == 'ALL':
                    selected.append(key)
                else:
                    if postag in tokens[key]['postags']:
                        selected.append(key)
                        # ~ self.log.debug("Key['%s'], POS['%s']", key, tokens[key]['postags'])

            items = []
            lenmax = 25
            for key in selected:
                lemma = tokens[key]['lemmas'][0]
                items.append(Token(id=key, title=key))
                if len(key) > lenmax:
                    lenmax = len(key)
            self.cvtokens.update(items)
            self.log.info("Selected %d tokens for POS tag '%s'", len(selected), postag)
            if lenmax < 25:
                lenmax = 25
            cur_pos = self.hpaned.get_position()
            new_pos = lenmax*8
            self.hpaned.set_position(new_pos)


    def _update_dashboard(self):
        # ~ # Update topics
        topics = self.app.dictionary.get_topics()
        data = []
        data.append(("ALL", "All topics"))
        for topic in topics.keys():
            data.append((topic.upper(), topic.title()))
        self.actions.dropdown_populate(self.ddTopics, Topic, data)

        # ~ # Update P-O-S
        # ~ fpos = self.app.dictionary.get_file_pos()
        # ~ adict = json_load(fpos)
        # ~ data = []
        # ~ for key in adict.keys():
            # ~ title = explain_term(key).title()
            # ~ data.append((key, title))
        # ~ self.actions.dropdown_populate(self.ddPos, Item, data)
