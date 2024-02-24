#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Environment module.

# File: env.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Environment variables module
"""

import os

from loro.backend.core.constants import LORO_USER_CNF
from loro.backend.core.util import json_load, json_save

try:
    # Load user config
    ENV = json_load(LORO_USER_CNF)
except:
    ENV = {}
    ENV['Languages'] = {}
    ENV['Languages']['de'] = {}
    ENV['Languages']['de']['model'] = {}
    ENV['Languages']['de']['model']['sm'] = 'de_core_news_sm'
    ENV['Languages']['de']['model']['lg'] = 'de_core_news_lg'
    ENV['Languages']['de']['model']['default'] = 'lg'
    ENV['Projects'] = {}
    ENV['Projects']['Default'] = {}
    ENV['Projects']['Default']['Languages'] = ('de', 'en')
    ENV['Projects']['Available'] = {}
    ENV['Projects']['Available']['Languages'] = [('de', 'en'), ('de', 'es'), ('en', 'es')]

    # ~ json_save(LORO_USER_CNF, ENV)

