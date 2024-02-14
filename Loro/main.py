import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor as Executor

from Loro.extractors import whatsapp
from Loro.services.nlp.spacy import tokenize_sentence
from Loro.core.util import validate_word

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
        result = tokenize_sentence(sentence)
        for word in result:
            valid = validate_word(word.text)
            if valid:
                tokens.add(word)
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
                print("Job[%d/%d]: %d tokens processed" % (jobid, num - 1, len(tokens)))
                for token in tokens:
                    if token.text not in all_tokens_text:
                        all_tokens_text.add(token.text)
                        all_tokens.add(token)
                jobcount += 1
    for token in all_tokens:
        print("%s > Lemma [%s]" % (token.text, token.lemma_))

def main():
    chat = whatsapp.get_messages(sys.argv[1])
    sentences = (chat.values())
    process_sentences(sentences)

    # ~ for n in chat:
        # ~ sentence = chat[n]
        # ~ tokens = tokenize_sentence(sentence)
        # ~ print(tokens)
        # ~ print("[%5d] > %s" % (n, chat[n]))
