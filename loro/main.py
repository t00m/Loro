#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger

def main(params: argparse.Namespace):
    log = get_logger('main')
    log.debug("%s %s", ENV['APP']['ID'], ENV['APP']['VERSION'])
    from loro.backend.core.util import setup_project_dirs
    from loro.backend.core.util import get_default_languages
    source, target = get_default_languages()
    setup_project_dirs(source, target)
    from loro.frontend.gui import app
    app.start()
