#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: watcher.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Custom models for working with Columnviews
"""

from gettext import gettext as _

from gi.repository import GObject


class Model(GObject.Object):
    """Custom MiAZ data model to be subclassed"""
    __gtype_name__ = 'Model'
    __title__ = 'Model'

    def __init__(self, id: str, title: str):
        super().__init__()
        self._id = id
        self._title = title

    @GObject.Property
    def id(self):
        return self._id

    @GObject.Property
    def title(self):
        return self._title

class Item(Model):
    """Custom data model"""
    __gtype_name__ = 'Item'
    __title__ = 'Item'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class Token(Item):
    """Custom data model"""
    __gtype_name__ = 'Token'
    __title__ = 'Token'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class TokenTranslation(Item):
    """Custom data model"""
    __gtype_name__ = 'TokenTranslation'
    __title__ = 'TokenTranslation'


    def __init__(self,  id: str,                # Token Id
                        title: str = '',        # Token Name
                        postag: str = '',       # Token Postag
                        translation: str = ''   # Translation
                ):
        super().__init__(id, title)
        self._postag = postag
        self._translation = translation

    @GObject.Property
    def postag(self):
        return self._postag

    @GObject.Property
    def translation(self):
        return self._translation

class Sentence(Item):
    """Custom data model"""
    __gtype_name__ = 'Sentence'
    __title__ = 'Sentence'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class Translation(Item):
    """Custom data model"""
    __gtype_name__ = 'Translation'
    __title__ = 'Translation'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class Topic(Item):
    """Custom data model for topics"""
    __gtype_name__ = 'Topic'
    __title__ = 'Topic'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class Workbook(Item):
    """Custom data model for topics"""
    __gtype_name__ = 'Workbook'
    __title__ = 'Workbook'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class Subtopic(Topic):
    """Custom data model for topics"""
    __gtype_name__ = 'Subtopic'
    __title__ = 'Subtopic'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class POSTag(Item):
    """Custom data model for topics"""
    __gtype_name__ = 'POSTag'
    __title__ = 'POSTag'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)


class Filepath(Item):
    """Custom data model"""
    __gtype_name__ = 'Filepath'
    __title__ = 'Filename'

    def __init__(self,
                    id: str,                 # Filepath
                    title: str = ''         # Basename
                    # ~ topic: str = '',         # Topic
                    # ~ subtopic: str = '',      # Subtopic
                    # ~ suffix: str = '',        # Suffix
                    # ~ belongs: bool = False    # Belong to active workbook
                ):
        super().__init__(id, title)
        # ~ self._topic = topic
        # ~ self._subtopic = subtopic
        # ~ self._suffix = suffix
        # ~ self._belongs = belongs

    # ~ @GObject.Property
    # ~ def topic(self):
        # ~ return self._topic

    # ~ @GObject.Property
    # ~ def subtopic(self):
        # ~ return self._subtopic

    # ~ @GObject.Property
    # ~ def suffix(self):
        # ~ return self._suffix

    # ~ @GObject.Property
    # ~ def belongs(self):
        # ~ return self._belongs

class Analysis(Item):
    """Custom data model sentence analysis"""
    __gtype_name__ = 'Analysis'
    __title__ = 'Analysis'

    def __init__(self,  id: str,                # Token
                        title: str = '',        # Token
                        lemma: str = '',        # Lemma
                        postag: str = '',       # P-O-S Tag
                        count: int = 0,         # Count
                        translation: str = ''   # Translation
                ):
        super().__init__(id, title)
        self._lemma = lemma
        self._postag = postag
        self._count = count
        self._translation = translation

    @GObject.Property
    def lemma(self):
        return self._lemma

    @GObject.Property
    def postag(self):
        return self._postag

    @GObject.Property
    def group(self):
        return self._group

    @GObject.Property
    def count(self):
        return self._count

    @GObject.Property
    def translation(self):
        return self._translation

