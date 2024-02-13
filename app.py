import sys
import whatsapp
from nlp.ll_spacy import tokenize_sentence

chat = whatsapp.get_messages(sys.argv[1])
for n in chat:
    sentence = chat[n]
    tokens = tokenize_sentence(sentence)
    print(tokens)
    # ~ print("[%5d] > %s" % (n, chat[n]))
