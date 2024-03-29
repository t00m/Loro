#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
# File: log.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: log module
"""

import logging
from rich.logging import RichHandler

def get_logger(name):
    """Returns a new logger with a custom pattern.
    @param name: logger name
    """
    logging.basicConfig(level='NOTSET', format="%(message)s", handlers=[RichHandler()])
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log
