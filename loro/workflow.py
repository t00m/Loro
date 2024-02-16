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

log = get_logger('workflow')

def init(model_name: str):
    load_model(model_name)

def sentence_processed(future):
    time.sleep(random.random())
    cur_thread = threading.current_thread().name
    x = future.result()
    if cur_thread != x:
        # ~ log.debug(x)
        return x

def process_sentence(data):
    (sentence, num) = data
    # ~ log.debug("Job[%d] started", num)
    metadata = {}
    metadata['sid'] = get_hash(sentence)
    metadata['tokens'] = set()
    metadata['entities'] = set()

    # Tokenize sentence
    result = tokenize_sentence(sentence.lower())

    # Named Entity Recognition (NER):
    for ent in result.ents:
        metadata['entities'].add(ent)

    # Tokens
    for token in result:
        if token.text not in metadata['tokens']:
            if is_valid_word(token.text):
                metadata['tokens'].add(token)

    return (num, metadata)

def process_input(sentences: []) -> []:
    jobs = []
    jobcount = 0
    num = 1
    all_tokens = set()
    all_tokens_text = set()
    all_entities = set()
    all_entities_text = set()

    log.info("Created %d jobs", len(sentences))
    with Executor(max_workers=40) as exe:
        for sentence in sentences:
            data = (sentence, num)
            job = exe.submit(process_sentence, data)
            # ~ job.add_done_callback(sentence_processed) # Not needed
            jobs.append(job)
            num = num + 1

        if num-1 > 0:
            for job in jobs:
                jobid, metadata = job.result()
                log.debug("Job[%d] finished: %d tokens processed", jobid, len(metadata['tokens']))
                for token in metadata['tokens']:
                    if token.text not in all_tokens_text:
                        all_tokens_text.add(token.text)
                        all_tokens.add(token)
                for entity in metadata['entities']:
                    if entity.text not in all_entities_text:
                        all_entities_text.add(entity.text)
                        all_entities.add(entity)
                jobcount += 1
    log.info("Tokens generated: %d", len(all_tokens))
    # ~ for token in all_tokens:
        # ~ pos = get_glossary_term_explained(token.pos_)
        # ~ print("%s > Lemma [%s] POS [%s (%s)]" % (token.text, token.lemma_, pos, token.pos_))
    return all_tokens

def process(workspace: str, source: str, filepath: str):
    topics, subtopics = get_metadata_from_filepath(filepath)
    sentences = open(filepath, 'r').readlines()
    process_input(sentences)
