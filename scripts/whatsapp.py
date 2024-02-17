#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

HOME = os.environ['HOME']
PKGDATADIR = os.path.join(HOME, '.local/share/loro')
sys.path.insert(1, PKGDATADIR)
from loro.extractors import whatsapp

chat = whatsapp.get_messages(sys.argv[1])
whatsapp.save_sentences(sys.argv[2], chat)
