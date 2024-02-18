import os
import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor as Executor

from loro.extractors import whatsapp
from loro.services.nlp.spacy import tokenize_sentence
from loro.services.nlp.spacy import get_glossary_term_explained
from loro.services.nlp.spacy import load_model
from loro.core.util import is_valid_word
from loro.core.util import get_metadata_from_filepath
from loro.core.util import get_hash
from loro.core.log import get_logger
from loro import dictionary
from loro.dictionary import Dictionary

class Workflow:
    def __init__(self, model_name: str):
        self.log = get_logger('Workflow')
        load_model(model_name)
        self.log.info("Model '%s' loaded", model_name)
        self.dictionary = Dictionary()

    def __del__(self):
      self.log.info("Workflow class destroyed")

    def start(self, filepath: str):
        self.log.info("Processing input file '%s'", os.path.basename(filepath))
        topic, subtopic = get_metadata_from_filepath(filepath)
        sentences = open(filepath, 'r').readlines()
        workbook = self.process_input(sentences)
        self.log.info("\tUseful sentences: %d", len(workbook.keys()))
        self.process_workbook(topic, subtopic, workbook)
        self.log.info("End processing input file '%s'", os.path.basename(filepath))

    def process_input(self, sentences: []) -> {}:
        workbook = {}
        jobs = []
        jid = 1
        self.log.info("\tGot %d sentences", len(sentences))
        with Executor(max_workers=40) as exe:
            for sentence in sentences:
                data = (sentence, jid)
                job = exe.submit(self.process_sentence, data)
                # ~ job.add_done_callback(self.__sentence_processed) # Not needed
                jobs.append(job)
                jid += 1

            if jid-1 > 0:
                for job in jobs:
                    jid, metadata = job.result()
                    self.log.debug("\tJob[%d] finished: %d tokens processed", jid, len(metadata['tokens']))
                    sid = metadata['sid']
                    workbook[sid] = {}
                    workbook[sid]['sentence'] = metadata['sentence']
                    workbook[sid]['tokens'] = list(metadata['tokens'])
                    workbook[sid]['entities'] = list(metadata['entities'])
        return workbook

    def process_sentence(self, data: tuple) -> tuple:
        (sentence, jid) = data
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

        return (jid, metadata)

    def process_workbook(self, topic: str, subtopic: str, workbook: {}):
        self.log.info("\tProcessing workbook")
        self.log.info("\t\tTopic: %s", topic)
        self.log.info("\t\tSubtopic: %s", subtopic)
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


        self.log.info("\t\tSaved %d sentences", nsents)
        self.log.info("\tWorkbook processed")


    def __sentence_processed(self, future):
        time.sleep(random.random())
        cur_thread = threading.current_thread().name
        x = future.result()
        if cur_thread != x:
            return x



