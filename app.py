import os
import re
import json
import pprint
import hashlib

text = 'Nach dem Spiel ist vor dem Spiel. Am Samstag geht es schon weiter. Die E3 spielt zu Hause gegen die jsg riol. Hier würden wir gerne auch Kuchen/ Muffins und vielleicht 2 Portionen laugengebäck anbieten. Außerdem bräuchten wir 2 Verkäufer die es an den Mann bringen.'
print("Original sentence: %s" % text)
process_sentence(sentence=text)

