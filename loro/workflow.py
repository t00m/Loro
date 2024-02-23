import os
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor as Executor
from rich.progress import Progress
from rich.progress import track

from loro.extractors import whatsapp
from loro.services.nlp.spacy import tokenize_sentence
from loro.services.nlp.spacy import get_glossary_term_explained
from loro.services.nlp.spacy import load_model
from loro.services.nlp.spacy import detect_language
from loro.core.util import is_valid_word
from loro.core.util import get_metadata_from_filepath
from loro.core.util import get_hash
from loro.core.log import get_logger
from loro import dictionary
from loro.dictionary import Dictionary
from loro.core.env import ENV

class Workflow:
    def __init__(self):
        self.log = get_logger('Workflow')
        self.source, self.target = ENV['Projects']['Default']['Languages']
        self.model_type = ENV['Languages'][self.source]['model']['default']
        self.model_name = ENV['Languages'][self.source]['model'][self.model_type]
        self.log.info("Source language: '%s'", self.source)
        self.log.info("Target language: '%s'", self.target)
        self.log.info("Loading model '%s' for language '%s'", self.model_name, self.source)
        load_model(self.model_name)
        self.log.info("Model '%s' loaded", self.model_name)
        self.dictionary = Dictionary()
        self.progress = None

    def __del__(self):
        pass

    def start(self, filepath: str):
        result = detect_language(open(filepath).read())
        lang = result['language']
        score = int((result['score']*100))
        if lang == self.source and score > 85:
            with Progress() as self.progress:
                topic, subtopic = get_metadata_from_filepath(filepath)
                sentences = open(filepath, 'r').readlines()
                task = self.progress.add_task("[green]%s..." % os.path.basename(filepath), total=len(sentences))
                workbook = self.process_input(sentences, task)
                self.process_workbook(topic, subtopic, workbook)
        else:
            self.log.error("File will NOT be processed: '%s'", os.path.basename(filepath))
            self.log.error("Language '%s' detected with %d%% of confidenciality", lang, score)
            if lang != self.source:
                self.log.error("Language detected ('%s') differs from source language ('%s')", lang, self.source)
            else:
                self.log.error("Score detection for detected language is less than 85%", score)

    def process_input(self, sentences: [], task) -> {}:
        workbook = {}
        jobs = []
        jid = 1
        MAX_WORKERS = 40
        with Executor(max_workers=MAX_WORKERS) as exe:
            for sentence in sentences:
                data = (sentence, jid, task)
                job = exe.submit(self.process_sentence, data)
                job.add_done_callback(self.__sentence_processed)
                jobs.append(job)
                jid += 1

            if jid-1 > 0:
                for job in jobs:
                    jid, metadata, task = job.result()
                    # ~ self.log.debug("\tJob[%d] finished: %d tokens processed", jid, len(metadata['tokens']))
                    sid = metadata['sid']
                    workbook[sid] = {}
                    workbook[sid]['sentence'] = metadata['sentence']
                    workbook[sid]['tokens'] = list(metadata['tokens'])
                    workbook[sid]['entities'] = list(metadata['entities'])
        return workbook

    def __sentence_processed(self, future):
        time.sleep(random.random())
        cur_thread = threading.current_thread().name
        x = future.result()
        jid, metadata, task = x
        self.progress.advance(task)
        if cur_thread != x:
            return x

    def process_sentence(self, data: tuple) -> tuple:
        (sentence, jid, task) = data
        # ~ log.debug("Job[%d] started", jid)
        metadata = {}
        metadata['sid'] = get_hash(sentence)
        metadata['sentence'] = sentence.strip()
        metadata['tokens'] = set()
        metadata['entities'] = set()

        # Tokenize sentence
        result = tokenize_sentence(sentence.lower())

        # Named Entity Recognition (NER):
        for ent in result.ents:
            metadata['entities'].add(ent.text)

        # Tokens
        for token in result:
            if token.text not in metadata['tokens']:
                if is_valid_word(token.text):
                    metadata['tokens'].add(token)
                    # ~ self.log.debug("Token: %s (%s)", token.text, type(token))

        return (jid, metadata, task)

    def process_workbook(self, topic: str, subtopic: str, workbook: {}):
        # ~ self.log.info("\tProcessing workbook")
        # ~ self.log.info("\t\tTopic: %s", topic)
        # ~ self.log.info("\t\tSubtopic: %s", subtopic)
        # Save topic
        self.dictionary.add_topic(topic, workbook)

        # Save subtopic
        self.dictionary.add_subtopic(subtopic, workbook)

        # Save sentences
        nsents = 0
        for sid in workbook:
            saved = self.dictionary.add_sentence(sid, workbook[sid]['sentence'])
            if saved:
                nsents += 1
                # Save tokens, lemmas and pos tags
                for token in workbook[sid]['tokens']:
                    self.dictionary.add_token(token, sid, workbook)





