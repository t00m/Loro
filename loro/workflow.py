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

log = get_logger('workflow')

def init(model_name: str):
    load_model(model_name)

# ~ def sentence_processed(future):
    # ~ time.sleep(random.random())
    # ~ cur_thread = threading.current_thread().name
    # ~ x = future.result()
    # ~ if cur_thread != x:
        # ~ return x

def process_sentence(data):
    (sentence, num) = data
    # ~ log.debug("Job[%d] started", num)
    metadata = {}
    metadata['sid'] = get_hash(sentence)
    metadata['sentence'] = sentence.strip()
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
    workbook = {}
    jobs = []
    jid = 1
    log.info("\tGot %d sentences", len(sentences))
    with Executor(max_workers=40) as exe:
        for sentence in sentences:
            data = (sentence, jid)
            job = exe.submit(process_sentence, data)
            # ~ job.add_done_callback(sentence_processed) # Not needed
            jobs.append(job)
            jid += 1

        if jid-1 > 0:
            for job in jobs:
                jid, metadata = job.result()
                log.debug("\tJob[%d] finished: %d tokens processed", jid, len(metadata['tokens']))
                sid = metadata['sid']
                workbook[sid] = {}
                workbook[sid]['sentence'] = metadata['sentence']
                workbook[sid]['tokens'] = list(metadata['tokens'])
                workbook[sid]['entities'] = list(metadata['entities'])
    return workbook

def process_workbook(topic: str, subtopic: str, workbook: {}):
    log.info("\tProcessing workbook")
    log.info("\t\tTopic: %s", topic)
    log.info("\t\tSubtopic: %s", subtopic)
    # Save topic
    dictionary.save_topic(topic, workbook)

    # Sabe subtopic
    dictionary.save_subtopic(subtopic, workbook)

    # Save sentences
    nsents = 0
    for sid in workbook:
        saved = dictionary.save_sentence(sid, workbook[sid]['sentence'])
        if saved:
            nsents += 1
            # ~ log.info(workbook[sid]['sentence'])
            # Save tokens, lemmas and pos tags
            # ~ for token in workbook[sid]['tokens']:
                # ~ log.info("\t%s", token.text)
    log.info("\t\tSaved %d sentences", nsents)
    log.info("\tWorkbook processed")


        # ~ for token in sentence:
            # ~ save_token_and_reference_to_sentence
    # ~ log.info("Tokens generated: %d", len(all_tokens))
    # ~ for token in all_tokens:
        # ~ pos = get_glossary_term_explained(token.pos_)
        # ~ print("%s > Lemma [%s] POS [%s (%s)]" % (token.text, token.lemma_, pos, token.pos_))
    # ~ print(workbook)
    pass

def start(filepath: str):
    log.info("Processing input file '%s'", os.path.basename(filepath))
    topic, subtopic = get_metadata_from_filepath(filepath)
    sentences = open(filepath, 'r').readlines()
    workbook = process_input(sentences)
    # ~ log.info("Useful sentences: %d", len(workbook.keys()))
    process_workbook(topic, subtopic, workbook)
    log.info("End processing input file '%s'", os.path.basename(filepath))
