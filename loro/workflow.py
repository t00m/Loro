#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor as Executor

from gi.repository import GObject, GLib

from rich.progress import Progress
from rich.progress import track

from loro.backend.core.env import ENV
from loro.backend.extractors import whatsapp
# ~ from loro.backend.services.nlp.spacy import tokenize_sentence
# ~ from loro.backend.services.nlp.spacy import render_sentence
# ~ from loro.backend.services.nlp.spacy import load_model
# ~ from loro.backend.services.nlp.spacy import detect_language
from loro.backend.core.util import is_valid_word
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.util import get_hash
from loro.backend.core.log import get_logger
from loro.workbook import Workbook
from loro.backend.core.run_async import RunAsync


class Workflow(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Workflow')

        GObject.GObject.__init__(self)
        GObject.signal_new('workflow-finished', Workflow, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        GObject.signal_new('model-loaded', Workflow, GObject.SignalFlags.RUN_LAST, None, () )

        source, target = ENV['Projects']['Default']['Languages']
        self.model_type = ENV['Languages'][source]['model']['default']
        self.model_name = ENV['Languages'][source]['model'][self.model_type]
        self.log.debug("Workflow configured for source '%s' and target '%s' languages", source, target)
        self.model_loaded = False
        if not self.model_loaded:
            # ~ self.__load_spacy_model()
            RunAsync(self.__load_spacy_model)
        self.connect('model-loaded', self.spacy_model_loaded)
        self.current_filename = ''
        self.fraction = 0.0
        self.running = False

    def spacy_model_loaded(self, *args):
        self.model_loaded = True

    def __load_spacy_model(self):
        """SpaCy model lazy loading"""
        source, target = ENV['Projects']['Default']['Languages']
        self.log.debug("Loading model '%s' for language '%s'", self.model_name, source)
        self.app.nlp.load_model(self.model_name)
        self.emit('model-loaded')
        self.log.debug("SpaCy model loaded successfully")

    def start(self, workbook: str, files: []):
        self.log.debug("Processing workbook: '%s'", workbook)
        if self.running:
            self.log.warning("Another workflow is already running? %s", self.running)
            return

        if len(files) == 0:
            self.log.warning("Workbook '%s' doesn't contain any file", workbook)
            return

        while not self.model_loaded:
            pass

        self.running = True
        self.current_filename = ''
        self.fraction = 0.0
        source, target = ENV['Projects']['Default']['Languages']
        if not self.model_loaded:
            self.log.warning("Spacy model still loading")
            return

        self.app.cache.initialize(workbook)

        nf = 0
        for filename in files:
            nf += 1
            INPUT_DIR = get_project_input_dir(source)
            filepath = os.path.join(INPUT_DIR, filename)
            self.current_filename = os.path.basename(filepath)

            # Detect language of file and validate
            result = self.app.nlp.detect_language(open(filepath).read())
            lang = result['language']
            score = int((result['score']*100))
            valid = lang.upper() == source.upper() and score >= 85

            if valid:
                topic, subtopic, suffix = get_metadata_from_filepath(filepath)
                sentences = open(filepath, 'r').readlines()
                self.process_input(workbook, filename, sentences, topic, subtopic) #, task)
                self.app.cache.save(workbook)
                self.fraction = 0.0
                self.log.debug("[%d/%d] %s processed", nf, len(files), filename)
            else:
                self.log.error("[%d/%d] '%s' was not processed processed", nf, len(files), os.path.basename(filepath))
                if lang.upper() != source.upper():
                    self.log.error("Language detected ('%s') differs from source language ('%s')", lang, source)
                if score < 85:
                    self.log.error("Language '%s' detected with %d%% of confidenciality (< 85%%)", lang, score)


        # ~ self.log.debug("Workflow finished for Workbook '%s'", workbook)
        self.emit('workflow-finished', workbook)
        self.running = False
        # ~ RunAsync(self.end(workbook))

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
                self.emit('workflow-finished')

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
        # ~ self.progress.advance(task)
        if cur_thread != x:
            return x

    def process_sentence(self, data: tuple) -> tuple:
        (workbook, filename, sentence, jid, topic, subtopic) = data
        sid = get_hash(sentence)
        tokens = self.app.nlp.tokenize_sentence(sentence)
        # ~ svg = self.app.nlp.render_sentence(tokens)
        # ~ with open('/tmp/%s' % sid, 'w') as fimg:
            # ~ fimg.write(svg)
        # ~ output_path = Path("/tmp/%s.svg" % sid) # you can keep there only "dependency_plot.svg" if you want to save it in the same folder where you run the script
        # ~ output_path.open("w", encoding="utf-8").write(svg)
        sid_tokens = []
        for token in tokens:
            if is_valid_word(token.text):
                thistoken = self.app.cache.add_token(workbook, token, sid, topic, subtopic)
                sid_tokens.append(token.text)
        self.app.cache.add_sentence(workbook, filename, sid, sentence.strip(), sid_tokens)

        return jid
