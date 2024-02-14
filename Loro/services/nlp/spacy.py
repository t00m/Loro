import spacy
from spacy.lang.de.examples import sentences
# ~ pip3 install -U $(spacy info de_core_news_sm --url) --user --break-system-packages
nlp = spacy.load("de_core_news_sm")
doc = nlp(sentences[0])
print(doc.text)
for token in doc:
    print(token.text, token.pos_, token.dep_)
