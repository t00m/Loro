#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint

from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_config_dir
from loro.backend.services.nlp.spacy import get_glossary_keys
from loro.backend.services.nlp.spacy import get_glossary_term_explained
from loro.backend.builders.excel import create_excel


class Dictionary:
    def __init__(self):
        self.log = get_logger('Dictionary')
        self.source, self.target = ENV['Projects']['Default']['Languages']
        configdir = get_project_config_dir(self.source, self.target)

         # Dictionary in-memory dicts
        self.sentences = {}
        self.tokens = {}

        # Initialize stats
        self.stats = {}
        self.posset = set()
        for key in get_glossary_keys():
            self.stats[key] = {}

        # Dictionary configuration files
        self.ftokens = os.path.join(get_project_config_dir(self.source, self.target), 'tokens_%s_%s.json' % (self.source, self.target))
        self.fsents = os.path.join(get_project_config_dir(self.source, self.target), 'sentences.json')

        # Load (or create) personal dictionary for current project
        self.__load_dictionary()

    def __load_dictionary(self):
        for thisfile, thisdict in [
                                    (self.fsents, self.sentences),
                                    (self.ftokens, self.tokens)
                                ]:
            if os.path.exists(thisfile):
                thisdict = json_load(thisfile)
                self.log.info("Loading %s (%d entries)", os.path.basename(thisfile), len(thisdict))
            else:
                json_save(thisfile, thisdict)
                self.log.info("Creating new config file '%s' with %d", os.path.basename(thisfile), len(thisdict))

    def __save_dictionary(self):
        for thisfile, thisdict in [
                                    (self.fsents, self.sentences),
                                    (self.ftokens, self.tokens),
                                ]:
            json_save(thisfile, thisdict)
            self.log.info("Dictionary '%s' saved with %d entries", os.path.basename(thisfile), len(thisdict))

    def get_file_tokens(self):
        return self.ftokens

    def add_sentence(self, sid: str, sentence:str) -> bool:
        added = False
        if not sid in self.sentences:
            self.sentences[sid] = {}
            self.sentences[sid][self.source] = sentence
            added = True
        return added

    def get_token(name: str) -> {}:
        try:
            return self.tokens[name]
        except KeyError:
            return {}

    def add_token(self, token: Token, sid: str, topic: str, subtopic: str):
        try:
            metadata = self.tokens[token.text]

            if not sid in metadata['sentences']:
                metadata['sentences'].extend([sid])
            if not token.lemma_ in metadata['lemmas']:
                metadata['lemmas'].extend([token.lemma_])
            if not token.pos_ in metadata['postags']:
                metadata['postags'].extend([token.pos_])
            if not topic in metadata['topics']:
                metadata['topics'].extend([topic])
            if not subtopic in metadata['subtopics']:
                metadata['subtopics'].extend([subtopic])
            metadata['count'] += 1
        except KeyError:
            metadata = {}
            metadata['sentences']= [sid]
            metadata['lemmas'] = [token.lemma_]
            metadata['postags'] = [token.pos_]
            metadata['topics'] = [topic]
            metadata['subtopics'] = [subtopic]
            metadata['count'] = 1
        finally:
            self.tokens[token.text] = metadata
        # ~ self.tokens[token.text]['gender'] = token.morph.get('gender')

    def __del__(self):
        self.__save_dictionary()

        # ~ try:
            # ~ tokens = self.lemmas[token.lemma_]
            # ~ if token.text not in tokens:
                # ~ tokens.append(token.text)
                # ~ self.lemmas[token.lemma_] = tokens
        # ~ except:
            # ~ self.lemmas[token.lemma_] = [token.text]

        # P-O-S (Part Of Speech) tagging and stats
        ## Stats
        # ~ try:
            # ~ num = self.stats[token.pos_][token.lemma_]
            # ~ self.stats[token.pos_][token.lemma_] = num + 1
        # ~ except:
            # ~ self.stats[token.pos_][token.lemma_] = 1
        # ~ self.posset.add(token.pos_)

        # ~ try:
            # ~ tokens = self.pos[token.pos_]
            # ~ if token.text not in tokens:
                # ~ tokens.append(token.text)
            # ~ self.pos[token.pos_] = tokens
        # ~ except:
            # ~ self.pos[token.pos_] = [token.text]

            # ~ if key == 'PROPN':
                # ~ self.log.info(self.stats[key])

        # ~ create_excel(self.stats, self.posset)
        # ~ for key in self.posset:
            # ~ print("POS TAG: %s" % key)
            # ~ pprint.pprint(sorted(self.stats[key].items(), key=lambda p:p[1], reverse=True))
        # ~ pprint.pprint(self.stats)

        # ~ for key in self.posset:
            # ~ postag = get_glossary_term_explained(key).title()
            # ~ self.log.info("%s: %d", postag, len(self.stats[key]))
