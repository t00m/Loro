# pip3 install spacy --user
# python3 -m spacy download de_core_news_sm
# POS TAGGING (spacy.glossary.GLOSSARY)
# Using properties of token i.e. Part of Speech and Lemmatization
# ~ for token in doc:
    # ~ print(token, " | ",
          # ~ spacy.explain(token.pos_),
          # ~ " | ", token.lemma_)
# ~ nlp.meta["sources"]

import spacy
nlp = spacy.load("de_core_news_sm") # Load German spaCy model

def get_glossary_keys() -> {}.keys():
    # Universal POS tags (https://universaldependencies.org/u/pos/)
    return spacy.glossary.GLOSSARY.keys()

def get_glossary_term_explained(term: str) -> str:
    try:
        return spacy.glossary.GLOSSARY[term]
    except KeyError:
        return ''


