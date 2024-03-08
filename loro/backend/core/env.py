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
    ENV['Languages']['DE'] = {}
    ENV['Languages']['DE']['model'] = {}
    ENV['Languages']['DE']['model']['sm'] = 'de_core_news_sm'
    ENV['Languages']['DE']['model']['lg'] = 'de_core_news_lg'
    ENV['Languages']['DE']['model']['default'] = 'lg'
    ENV['Projects'] = {}
    ENV['Projects']['Default'] = {}
    ENV['Projects']['Default']['Languages'] = ('DE', 'EN')
    ENV['Projects']['Available'] = {}
    ENV['Projects']['Available']['Languages'] = [('DE', 'EN')]
