import sys
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor as Executor

from Loro.extractors import whatsapp
from Loro.services.nlp.spacy import tokenize_sentence

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
        tokens = tokenize_sentence(sentence)
        return (num, tokens)

def process_sentences(sentences: list) -> None:
    jobs = []
    jobcount = 0
    num = 1
    with Executor(max_workers=10) as exe:
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
                jobcount += 1

def main():
    chat = whatsapp.get_messages(sys.argv[1])
    sentences = (chat.values())
    process_sentences(sentences)

    # ~ for n in chat:
        # ~ sentence = chat[n]
        # ~ tokens = tokenize_sentence(sentence)
        # ~ print(tokens)
        # ~ print("[%5d] > %s" % (n, chat[n]))
