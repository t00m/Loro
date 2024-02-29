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

class Sentence(Item):
    """Custom data model"""
    __gtype_name__ = 'Sentence'
    __title__ = 'Sentence'

    def __init__(self,  id: str, title: str = ''):
        super().__init__(id, title)

class Topic(Item):
    """Custom data model for topics"""
    __gtype_name__ = 'Topic'
    __title__ = 'Topic'

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
