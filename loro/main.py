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
from loro.core.util import get_user_documents_dir
from loro.core.util import setup_project_dirs
from loro.core.env import LORO_USER_PROJECTS_DIR
from loro.core.env import ENV

def sentence_processed(future):
        time.sleep(random.random())
        cur_thread = threading.current_thread().name
        x = future.result()
        if cur_thread != x:
            # ~ num = x
            # ~ print(x)
            return x

def tokenize(data):
        (sentence, num) = data
        tokens = set()
        entities = set()
        result = tokenize_sentence(sentence.lower())
        # Named Entity Recognition (NER):
        # Identifying named entities like persons, organizations, or locations.
        for ent in result.ents:
            entities.add(ent.text)
            # ~ print(ent.text, ent.label_)

        # Sentence Boundary Detection:
        # Splitting text into sentences.
        # Not useful as sentences are parsed individually.
        # ~ for sent in result.sents:
            # ~ print(sent.text)

        for token in result:
            if token.text not in entities:
                is_valid = is_valid_word(token.text)
                if is_valid:
                    tokens.add(token)
            # ~ else:
                # ~ print("Token '%s' is an entity. Skipped" % token.text)

        return (num, tokens)

def process_sentences(sentences: list) -> None:
    jobs = []
    jobcount = 0
    num = 1
    all_tokens_text = set()
    all_tokens = set()
    with Executor(max_workers=40) as exe:
        for sentence in sentences:
            data = (sentence, num)
            job = exe.submit(tokenize, data)
            job.add_done_callback(sentence_processed)
            jobs.append(job)
            num = num + 1

        if num-1 > 0:
            print("Created %d jobs" % (num - 1))
            for job in jobs:
                jobid, tokens = job.result()
                # ~ print("Job[%d/%d]: %d tokens processed" % (jobid, num - 1, len(tokens)))
                for token in tokens:
                    if token.text not in all_tokens_text:
                        all_tokens_text.add(token.text)
                        all_tokens.add(token)
                jobcount += 1
    print("Tokens")
    for token in all_tokens:
        pos = get_glossary_term_explained(token.pos_)
        print("%s > Lemma [%s] POS [%s (%s)]" % (token.text, token.lemma_, pos, token.pos_))

def main(version):
    workspace = LORO_USER_PROJECTS_DIR
    source, target = ENV['Projects']['Default']['Languages']
    model_type = ENV['Languages'][source]['model']['default']
    model_name = ENV['Languages'][source]['model'][model_type]
    print("Loro %s" % version)
    print("User workspace: %s" % workspace)
    print("Loading model '%s' for language '%s'" % (model_name, source))
    load_model(model_name)
    setup_project_dirs(workspace, source, target)

    try:
        filepath = sys.argv[1]
    except IndexError:
        print("Error: input file not found")
        exit(-1)

    chat = whatsapp.get_messages(sys.argv[1])
    sentences = (chat.values())
    process_sentences(sentences)


    # ~ for n in chat:
        # ~ sentence = chat[n]
        # ~ tokens = tokenize_sentence(sentence)
        # ~ print(tokens)
        # ~ print("[%5d] > %s" % (n, chat[n]))
