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
from os.path import abspath
import sys
from gettext import gettext as _

from loro.core.util import get_user_documents_dir
from loro.core.util import json_load, json_save

LORO_USER_DIR = os.path.join(get_user_documents_dir(), 'Loro')
LORO_USER_PROJECTS_DIR = os.path.join(get_user_documents_dir(), 'Loro', 'Projects')
LORO_USER_CONFIG_DIR = os.path.join(get_user_documents_dir(), 'Loro', '.config')
LORO_USER_CNF = os.path.join(LORO_USER_CONFIG_DIR, 'loro.conf')

for directory in [  LORO_USER_DIR,
                    LORO_USER_PROJECTS_DIR,
                    LORO_USER_CONFIG_DIR
                 ]:
    if not os.path.exists(directory):
        os.makedirs(directory)

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
    ENV['Projects']['Available']['Languages'] = [('de', 'es'), ('en', 'es')]

    json_save(LORO_USER_CNF, ENV)

