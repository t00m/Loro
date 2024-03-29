# pip3 install spacy --user
# python3 -m spacy download de_core_news_sm
# POS TAGGING (spacy.glossary.GLOSSARY)
# Using properties of token i.e. Part of Speech and Lemmatization
# ~ for token in doc:
    # ~ print(token, " | ",
          # ~ spacy.explain(token.pos_),
          # ~ " | ", token.lemma_)
# ~ nlp.meta["sources"]
# ~ pip3 install -U $(spacy info de_core_news_sm --url) --user --break-system-packages
# ~ https://github.com/explosion/spacy-models/releases?q=german&expanded=true

import spacy
from spacy.lang.de.examples import sentences
from spacy import Language
from spacy.cli import download


def load_spacy(model_name: str, **kwargs) -> Language:
    """Load a spaCy model, download it if it has not been installed yet.
    :param model_name: the model name, e.g., en_core_web_sm
    :param kwargs: options passed to the spaCy loader, such as component exclusion, as you
    would with spacy.load()
    :return: an initialized spaCy Language
    :raises: SystemExit: if the model_name cannot be downloaded

    https://github.com/BramVanroy/spacy_download
    """
    from importlib import import_module
    try:
        model_module = import_module(model_name)
    except ModuleNotFoundError:
        download(model_name)
        model_module = import_module(model_name)

    return model_module.load(**kwargs)

def get_glossary_keys() -> {}.keys():
    # Universal POS tags (https://universaldependencies.org/u/pos/)
    return spacy.glossary.GLOSSARY.keys()

def get_glossary_term_explained(term: str) -> str:
    try:
        return spacy.glossary.GLOSSARY[term]
    except KeyError:
        return ''

def tokenize_sentence(sentence: str) -> []:
    return nlp(sentence)

nlp = load_spacy("de_core_news_sm") # Load German spaCy model

# ~ univ = {}
# ~ for nc in chat:
    # ~ doc = nlp(chat[nc])
    # ~ for token in doc:
        # ~ try:
            # ~ elems = univ[token.pos_]
            # ~ if not token.text in elems:
                # ~ elems.append(token.text)
        # ~ except:
            # ~ elems = []
            # ~ elems.append(token.text)
            # ~ univ[token.pos_] = elems
        # print(token.text, token.pos_, token.dep_)

# ~ pprint.pprint(univ)

