import sys
from Loro.extractors import whatsapp
from Loro.services.nlp.spacy import tokenize_sentence

def main():
    chat = whatsapp.get_messages(sys.argv[1])
    for n in chat:
        sentence = chat[n]
        tokens = tokenize_sentence(sentence)
        print(tokens)
        # ~ print("[%5d] > %s" % (n, chat[n]))
