# pip3 install spacy --user
# python3 -m spacy download de_core_news_sm
# POS TAGGING (spacy.glossary.GLOSSARY)
# Using properties of token i.e. Part of Speech and Lemmatization
# ~ Text: The original word text.
# ~ Lemma: The base form of the word.
# ~ POS: The simple UPOS part-of-speech tag.
# ~ Tag: The detailed part-of-speech tag.
# ~ Dep: Syntactic dependency, i.e. the relation between tokens.
# ~ Shape: The word shape – capitalization, punctuation, digits.
# ~ is alpha: Is the token an alpha character?
# ~ is stop: Is the token part of a stop list, i.e. the most common words of the language?
# ~ https://github.com/explosion/spacy-models/releases?q=german&expanded=true

import spacy
from spacy.lang.de.examples import sentences
from spacy import Language
from spacy import displacy
from spacy.cli import download
from spacy_langdetect import LanguageDetector

from loro.backend.core.log import get_logger


class NLP:
    def __init__(self, app):
        self.log = get_logger("SpaCy")
        self.nlp = None
        self.log.debug("SpaCy initialited")

    def load_spacy(self, model_name: str, **kwargs) -> Language:
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

    @Language.factory("language_detector")
    def get_lang_detector(self, nlp, name):
       return LanguageDetector()

    def load_model(self, model: str) -> None:
        self.nlp = self.load_spacy(model)
        # ~ self.nlp.add_pipe(name='language_detector', last=True)

    def explain_term(self, term: str) -> str:
        try:
            return spacy.glossary.GLOSSARY[term]
        except KeyError:
            return ''

    def get_glossary_keys(self) -> {}.keys():
        # Universal POS tags (https://universaldependencies.org/u/pos/)
        return spacy.glossary.GLOSSARY.keys()

    def tokenize_sentence(self, sentence: str) -> []:
        return self.nlp(sentence)

    def render_sentence(self, doc):
        options = {
            "compact": False,
            "fine_grained": True,
            "add_lemma": False,
            "color": "blue",
            "jupyter": True
        }
        return displacy.render(doc, style="dep", page=False, jupyter=False, options=options)

    def detect_language(self, text):
        return self.nlp(text)._.language
