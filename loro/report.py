#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from mako.template import Template
from gi.repository import GObject

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import get_project_target_workbook_dir
from loro.backend.core.util import create_directory, delete_directory
from loro.backend.core.util import json_save
from loro.backend.services.nlp import spacy

# UIKIT (getuikit.com)
DIR_UIKIT = os.path.join(ENV['APP']['PGKDATADIR'], 'resources', 'web', 'uikit')
DIR_UIKIT_CSS = os.path.join(DIR_UIKIT, 'css')
UIKIT_CSS = os.path.join(DIR_UIKIT_CSS, 'uikit.min.css')
PRINT_CSS = os.path.join(DIR_UIKIT_CSS, 'print.css')
DIR_UIKIT_JS = os.path.join(DIR_UIKIT, 'js')
UIKIT_MIN_JS = os.path.join(DIR_UIKIT_JS, 'uikit.min.js')
UIKIT_ICON_MIN_JS = os.path.join(DIR_UIKIT_JS, 'uikit-icons.min.js')

# Loro UIKit based templates
DIR_TPL = os.path.join(DIR_UIKIT, 'tpl')
TPL_HEADER = os.path.join(DIR_TPL, 'HTML_HEADER.tpl')
TPL_BODY_INDEX = os.path.join(DIR_TPL, 'HTML_BODY_INDEX.tpl')
TPL_BODY_LEMMA = os.path.join(DIR_TPL, 'HTML_BODY_LEMMA.tpl')
TPL_BODY_TOKEN = os.path.join(DIR_TPL, 'HTML_BODY_TOKEN.tpl')
TPL_BODY_SENTENCE = os.path.join(DIR_TPL, 'HTML_BODY_SENTENCE.tpl')
TPL_BODY_FILE = os.path.join(DIR_TPL, 'HTML_BODY_FILE.tpl')
TPL_FOOTER = os.path.join(DIR_TPL, 'HTML_FOOTER.tpl')
TPL_FOOTER_INDEX = os.path.join(DIR_TPL, 'HTML_FOOTER_INDEX.tpl')
TPL_FOOTER_LEMMA = os.path.join(DIR_TPL, 'HTML_FOOTER_LEMMA.tpl')
TPL_FOOTER_TOKEN = os.path.join(DIR_TPL, 'HTML_FOOTER_TOKEN.tpl')


class Report(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Report')
        GObject.GObject.__init__(self)
        GObject.signal_new('report-finished', Report, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        self.templates = {}
        self._add_templates()
        self.log.debug("Reporting initialized")
        self.app.workflow.connect('workflow-finished', self.update_report)

    def _add_templates(self):
        self.templates['HEADER'] = Template(filename=TPL_HEADER)
        self.templates['BODY_INDEX'] = Template(filename=TPL_BODY_INDEX)
        self.templates['BODY_LEMMA'] = Template(filename=TPL_BODY_LEMMA)
        self.templates['BODY_TOKEN'] = Template(filename=TPL_BODY_TOKEN)
        self.templates['BODY_SENTENCE'] = Template(filename=TPL_BODY_SENTENCE)
        self.templates['BODY_FILE'] = Template(filename=TPL_BODY_FILE)
        self.templates['FOOTER'] = Template(filename=TPL_FOOTER)
        self.templates['FOOTER_INDEX'] = Template(filename=TPL_FOOTER_INDEX)
        self.templates['FOOTER_LEMMA'] = Template(filename=TPL_FOOTER_LEMMA)
        self.templates['FOOTER_TOKEN'] = Template(filename=TPL_FOOTER_TOKEN)
        self.log.debug("Loro templates added")

    def template(self, name: str):
        return self.templates[name]

    def render_template(self, name, var={}):
        tpl = self.template(name)
        return tpl.render(var=var)

    def build(self, workbook: str) -> str:
        self.log.debug("Building report for workbook '%s'", workbook)
        source, target = ENV['Projects']['Default']['Languages']
        DIR_OUTPUT = get_project_target_workbook_dir(source, target, workbook)
        DIR_HTML = os.path.join(DIR_OUTPUT, 'html')
        var = {}
        var['workbook'] = {}
        var['workbook']['id'] = workbook
        var['workbook']['source'] = source
        var['workbook']['target'] = target
        var['workbook']['cache'] = self.app.workbooks.get_dictionary(workbook)
        json_save('/tmp/loro.cache.json', var['workbook']['cache'])

        var['workbook']['stats'] = self.app.stats.get(workbook)
        var['html'] = {}
        var['html']['uikit'] = {}
        var['html']['uikit']['css'] = UIKIT_CSS
        var['html']['uikit']['css_print'] = PRINT_CSS
        var['html']['uikit']['icon'] = UIKIT_ICON_MIN_JS
        var['html']['uikit']['js'] = UIKIT_MIN_JS
        var['html']['output'] = DIR_HTML
        var['html']['index'] = False

        self._prepare(var)
        self._build_token_pages(var)
        self._build_lemma_pages(var)
        self._build_sentence_pages(var)
        self._build_file_pages(var)
        url = self._build_index(var)
        self.log.debug("Report for workbook '%s' built", workbook)
        return url

    def _prepare(self, var: dict) -> bool:
        delete_directory(var['html']['output'])
        create_directory(var['html']['output'])

    def _build_token_pages(self, var: dict):
        workbook = var['workbook']['id']
        n = 0
        for token in var['workbook']['cache']['tokens']['data']:
            var['html']['index'] = False
            var['html']['title'] = "Token: %s" % token
            var['token'] = {}
            var['token']['name'] = token
            var['token']['properties'] = var['workbook']['cache']['tokens']['data'][token]
            header = self.render_template('HEADER', var)
            body = self.render_template('BODY_TOKEN', var)
            footer = self.render_template('FOOTER_TOKEN', var)
            html = header + body + footer
            url = os.path.join(var['html']['output'], 'Token_%s.html' % token)
            self._write_page(url, html)
            n += 1
        self.log.debug("Created %d pages for tokens", n)

    def _build_lemma_pages(self, var: dict):
        workbook = var['workbook']['id']
        n = 0
        for postag in var['workbook']['stats']['postags']:
            for lemma in var['workbook']['stats']['postags'][postag]['lemmas']:
                var['html']['index'] = False
                var['html']['title'] = "%s: %s" % (spacy.explain_term(postag), lemma)
                var['lemma'] = {}
                var['lemma']['name'] = lemma
                var['lemma']['postag'] = spacy.explain_term(postag).title()
                tokens = var['workbook']['stats']['lemmas'][lemma]['tokens']
                var['lemma']['tokens'] = tokens
                header = self.render_template('HEADER', var)
                body = self.render_template('BODY_LEMMA', var)
                footer = self.render_template('FOOTER_LEMMA', var)
                html = header + body + footer
                url = os.path.join(var['html']['output'], '%s_%s.html' % (postag, lemma))
                self._write_page(url, html)
                n += 1
        self.log.debug("Created %d pages for lemmas", n)

    def _build_sentence_pages(self, var: dict):
        workbook = var['workbook']['id']
        n = 0
        # ~ self.log.debug(var['workbook']['cache']['sentences']['data'])
        for sid in var['workbook']['cache']['sentences']['data']:
            var['html']['index'] = False
            var['html']['title'] = "Sentence: %s" % sid
            var['sentence'] = {}
            var['sentence']['sid'] = sid
            var['sentence']['text'] = var['workbook']['cache']['sentences']['data'][sid]['DE']
            # ~ self.log.debug(var['sentence']['properties'])
            var['sentence']['properties'] = var['workbook']['cache']['sentences']['data'][sid]
            header = self.render_template('HEADER', var)
            body = self.render_template('BODY_SENTENCE', var)
            footer = self.render_template('FOOTER', var)
            html = header + body + footer
            url = os.path.join(var['html']['output'], 'Sentence_%s.html' % sid)
            self._write_page(url, html)
            n += 1
        # ~ self.log.debug(var['workbook']['cache']['sentences']['data'])
        # ~ self.log.debug("Created %d pages for sentences", n)

    def _build_file_pages(self, var: dict):
        workbook = var['workbook']['id']
        n = 0
        for filename in var['workbook']['cache']['filenames']['data']:
            var['html']['index'] = False
            var['html']['title'] = "File: %s" % filename
            var['filename'] = {}
            var['filename']['name'] = filename
            var['filename']['sentences'] = var['workbook']['cache']['filenames']['data'][filename]
            header = self.render_template('HEADER', var)
            body = self.render_template('BODY_FILE', var)
            footer = self.render_template('FOOTER', var)
            html = header + body + footer
            url = os.path.join(var['html']['output'], 'File_%s.html' % filename)
            self._write_page(url, html)
            n += 1
        # ~ self.log.debug(var['workbook']['cache']['sentences']['data'])
        self.log.debug("Created %d pages for workbokk files", n)

    def _build_index(self, var: dict):
        workbook = var['workbook']['id']
        var['html']['title'] = "Workbook %s" % workbook
        var['html']['index'] = True
        url = os.path.join(var['html']['output'], 'index.html')

        files = self.app.workbooks.get_files(workbook)
        var['workbook']['files'] = files
        topics = self.app.dictionary.get_topics(workbook)
        var['workbook']['topics'] = ', '.join(topics)
        header = self.render_template('HEADER', var)
        body = self.render_template('BODY_INDEX', var)
        footer = self.render_template('FOOTER_INDEX', var)
        html = header + body + footer
        self._write_page(url, html)
        self.log.debug("Index page created")
        return url

    def _write_page(self, url: str, html: str):
        basename = os.path.basename(url)
        with open(url, 'w') as fout:
            fout.write(html)
            # ~ self.log.debug("Page '%s' created", basename)

    def update_report(self, workflow, workbook):
        self.build(workbook)
        self.log.debug("Report['%s'] generated" % workbook)
        # ~ self.emit('report-finished', workbook)


# ~ <%! from loro.backend.services.nlp import spacy %>
# ~ <p class="uk-text-lead">
# ~ % for postag in var['workbook']['stats']['postags']:
    # ~ <h3 class="uk-margin-small-bottom" id="${postag}">${spacy.explain_term(postag).title()}</h3>
# ~ % endfor
# ~ </p>