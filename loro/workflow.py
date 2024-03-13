#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor as Executor

from gi.repository import GObject, GLib

from rich.progress import Progress
from rich.progress import track

from loro.backend.core.env import ENV
from loro.backend.extractors import whatsapp
from loro.backend.services.nlp.spacy import tokenize_sentence
from loro.backend.services.nlp.spacy import get_glossary_term_explained
from loro.backend.services.nlp.spacy import load_model
from loro.backend.services.nlp.spacy import detect_language
from loro.backend.core.util import is_valid_word
from loro.backend.core.util import get_metadata_from_filepath
from loro.backend.core.util import get_project_input_dir
from loro.backend.core.util import get_hash
from loro.backend.core.log import get_logger
from loro import dictionary
from loro.workbook import Workbook


class Workflow(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Workflow')

        GObject.GObject.__init__(self)
        GObject.signal_new('workflow-finished', Workflow, GObject.SignalFlags.RUN_LAST, None, () )
        GObject.signal_new('model-loaded', Workflow, GObject.SignalFlags.RUN_LAST, None, () )

        source, target = ENV['Projects']['Default']['Languages']
        self.model_type = ENV['Languages'][source]['model']['default']
        self.model_name = ENV['Languages'][source]['model'][self.model_type]
        self.log.info("Workflow configured for source '%s' and target '%s' languages", source, target)
        self.model_loaded = False
        self.connect('model-loaded', self.spacy_model_loaded)
        GLib.idle_add(self.__load_spacy_model)
        self.progress = None

    def spacy_model_loaded(self, *args):
        self.model_loaded = True

    def __load_spacy_model(self):
        """SpaCy model lazy loading"""
        source, target = ENV['Projects']['Default']['Languages']
        self.log.info("Loading model '%s' for language '%s'", self.model_name, source)
        load_model(self.model_name)
        self.emit('model-loaded')
        self.log.info("SpaCy model loaded successfully")

    def start(self, workbook: str, files: []):
        source, target = ENV['Projects']['Default']['Languages']
        self.log.debug("Processing workbook: '%s'", workbook)
        if not self.model_loaded:
            self.log.warning("Spacy model still loading")
            return

        self.app.dictionary.initialize(workbook)

        for filename in files:
            self.log.debug("Processing %s[%s]", workbook, os.path.basename(filename))
            INPUT_DIR = get_project_input_dir(source)
            filepath = os.path.join(INPUT_DIR, filename)

            # Detect language of file and validate
            result = detect_language(open(filepath).read())
            lang = result['language']
            score = int((result['score']*100))
            valid = lang.upper() == source.upper() and score >= 85

            if valid:
                with Progress() as self.progress:
                    topic, subtopic, suffix = get_metadata_from_filepath(filepath)
                    sentences = open(filepath, 'r').readlines()
                    task = self.progress.add_task("[green]%s..." % os.path.basename(filepath), total=len(sentences))
                    self.process_input(workbook, sentences, topic, subtopic, task)
                    self.app.dictionary.save(workbook)
            else:
                self.log.error("File will NOT be processed: '%s'", os.path.basename(filepath))
                if lang.upper() != source.upper():
                    self.log.error("Language detected ('%s') differs from source language ('%s')", lang, source)
                if score < 85:
                    self.log.error("Language '%s' detected with %d%% of confidenciality (< 85%%)", lang, score)
        self.emit('workflow-finished')

    def process_input(self, workbook:str, sentences: [], topic, subtopic, task) -> None:
        jobs = []
        jid = 1
        MAX_WORKERS = 40
        with Executor(max_workers=MAX_WORKERS) as exe:
            for sentence in sentences:
                data = (workbook, sentence, jid, topic, subtopic, task)
                job = exe.submit(self.process_sentence, data)
                job.add_done_callback(self.__sentence_processed)
                jobs.append(job)
                jid += 1

            if jid-1 > 0:
                for job in jobs:
                    jid, task = job.result()

    def __sentence_processed(self, future):
        time.sleep(random.random())
        cur_thread = threading.current_thread().name
        x = future.result()
        jid, task = x
        self.progress.advance(task)
        if cur_thread != x:
            return x

    def process_sentence(self, data: tuple) -> tuple:
        (workbook, sentence, jid, topic, subtopic, task) = data
        sid = get_hash(sentence)
        tokens = tokenize_sentence(sentence)

        sid_tokens = []
        for token in tokens:
            if is_valid_word(token.text):
                thistoken = self.app.dictionary.add_token(workbook, token, sid, topic, subtopic)
                sid_tokens.append(token.text)
        self.app.dictionary.add_sentence(workbook, sid, sentence.strip(), sid_tokens)

        return (jid, task)
