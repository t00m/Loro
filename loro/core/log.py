#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# File: log.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: log module
"""

import logging

def get_logger(name):
    """Returns a new logger with a custom pattern.
    @param name: logger name
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)7s | %(lineno)4d  |%(name)10s | %(asctime)s | %(message)s")
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log
