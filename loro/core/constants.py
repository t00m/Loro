#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess


def get_user_documents_dir():
    return subprocess.check_output(["xdg-user-dir", "DOCUMENTS"], universal_newlines=True).strip()

LORO_USER_DIR = os.path.join(get_user_documents_dir(), 'Loro')
LORO_USER_PROJECTS_DIR = os.path.join(get_user_documents_dir(), 'Loro', 'Projects')
LORO_USER_CONFIG_DIR = os.path.join(get_user_documents_dir(), 'Loro', '.config')
LORO_USER_CNF = os.path.join(LORO_USER_CONFIG_DIR, 'loro.conf')
