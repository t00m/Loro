#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor as Executor

from gi.repository import GObject

from loro.backend.core.env import ENV
from loro.backend.core.util import is_valid_word
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.util import get_hash
from loro.backend.core.log import get_logger
from loro.workbook import Workbook
from loro.backend.core.run_async import RunAsync
from loro.backend.core.util import get_project_target_workbook_html_dir
from loro.backend.core.util import get_default_languages


class Workflow(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Workflow')

        GObject.GObject.__init__(self)
        GObject.signal_new('workflow-finished', Workflow, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        GObject.signal_new('model-loaded', Workflow, GObject.SignalFlags.RUN_LAST, None, () )

        source, target = get_default_languages()
        self.model_type = ENV['Languages'][source]['model']['default']
        self.model_name = ENV['Languages'][source]['model'][self.model_type]
        self.log.debug("Workflow configured for source '%s' and target '%s' languages", source, target)
        self.model_loaded = False
        self.docbin = {}
        if not self.model_loaded:
            # ~ self.__load_spacy_model()
            RunAsync(self.__load_spacy_model)
        self.connect('model-loaded', self.spacy_model_loaded)
        self.current_filename = ''
        self.fraction = 0.0
        self.running = False

    def spacy_model_loaded(self, *args):
        self.model_loaded = True

    def __load_spacy_model(self, *args):
        """SpaCy model lazy loading"""
        source, target = get_default_languages()
        self.log.debug("Loading model '%s' for language '%s'", self.model_name, source)
        self.app.nlp.load_model(self.model_name)
        self.log.debug("SpaCy model loaded successfully")
        self.emit('model-loaded')

    def start(self, workbook: str, files: []):
        self.log.debug("Processing workbook: '%s'", workbook)
        if self.running:
            self.log.warning("Another workflow is already running? %s", self.running)
            return

        if len(files) == 0:
            self.log.warning("Workbook '%s' doesn't contain any file", workbook)
            self.emit('workflow-finished', workbook)
            return

        while not self.model_loaded:
            pass

        self.running = True
        self.docbin = {}
        self.current_filename = ''
        self.fraction = 0.0
        source, target = get_default_languages()
        if not self.model_loaded:
            self.log.warning("Spacy model still loading")
            return

        self.app.cache.initialize(workbook)

        nf = 0
        for filename in files:
            nf += 1
            INPUT_DIR = get_project_input_dir()
            filepath = os.path.join(INPUT_DIR, filename)
            self.current_filename = os.path.basename(filepath)

            topic, subtopic, suffix = get_metadata_from_filepath(filepath)
            sentences = open(filepath, 'r').readlines()
            self.process_input(workbook, filename, sentences, topic, subtopic) #, task)
            self.app.cache.save(workbook)
            self.fraction = 0.0
            self.log.debug("[%d/%d] %s processed", nf, len(files), filename)

        self.log.debug("Rendering sentences")
        html_dir = get_project_target_workbook_html_dir(workbook)
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)
        self.log.debug("Saving SVG files to '%s'", html_dir)
        for sid in self.docbin:
            doc = self.docbin[sid]
            svg = self.app.nlp.render_sentence(doc)
            # ~ self.log.debug(svg)
            output_path = os.path.join(html_dir, '%s.svg' % sid)
            with open(output_path, 'w') as fsvg:
                fsvg.write(svg)
                # ~ self.log.debug(output_path)
        self.log.debug("Workflow finished for Workbook '%s'", workbook)
        self.running = False
        self.emit('workflow-finished', workbook)

    def process_input(self, workbook:str, filename: str, sentences: [], topic, subtopic) -> None:
        jobs = []
        jid = 1
        MAX_WORKERS = 10
        with Executor(max_workers=MAX_WORKERS) as exe:
            for sentence in sentences:
                data = (workbook, filename, sentence, jid, topic, subtopic)
                job = exe.submit(self.process_sentence, data)
                job.add_done_callback(self.__sentence_processed)
                jobs.append(job)
                jid += 1

            if jid-1 > 0:
                for job in jobs:
                    jid = job.result()
                    self.set_progress(jid/len(jobs)*1.0)

            if jid == 0:
                self.set_progress(1.0)
                # ~ self.emit('workflow-finished')

    def set_progress(self, fraction):
        self.fraction = fraction
        # ~ self.log.debug("%s > %f", self.current_filename, fraction)

    def get_progress(self):
        return self.current_filename, self.fraction

    def __sentence_processed(self, future):
        time.sleep(0.5)
        cur_thread = threading.current_thread().name
        x = future.result()
        jid = x
        if cur_thread != x:
            return x

    def process_sentence(self, data: tuple) -> tuple:
        (workbook, filename, sentence, jid, topic, subtopic) = data
        sentence = sentence.strip()
        sid = get_hash(sentence)
        doc = self.app.nlp.tokenize_sentence(sentence)
        doc.user_data["title"] = sentence
        sid_tokens = []
        for token in doc:
            if is_valid_word(token.text):
                tid = self.app.cache.add_token(workbook, token, sid, topic, subtopic)
                sid_tokens.append(tid)
        self.app.cache.add_sentence(workbook, filename, sid, sentence.strip(), sid_tokens)
        self.docbin[sid] = doc
        return jid
