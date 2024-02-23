import os
import sys
import signal
import locale
import gettext
import argparse

from loro.core.env import ENV
from loro.core.log import get_logger
from loro.core.util import setup_project_dirs
from loro.core.util import get_project_input_dir
from loro.core.util import get_inputs

def main(params: argparse.Namespace):
    log = get_logger('main')
    log.info("%s %s", ENV['APP']['ID'], ENV['APP']['VERSION'])
    source = params.SOURCE
    target = params.TARGET
    if source is None or target is None:
        source, target = ENV['Projects']['Default']['Languages']
    else:
        ENV['Projects']['Default']['Languages'] = (source, target)
    log.info("Source language: '%s'", source)
    log.info("Target language: '%s'", target)

    if source == target:
        log.error("Source and target languages can't be the same")
        sys.exit(-1)

    setup_project_dirs(source, target)
    inputs = get_inputs(source, target)

    if len(inputs) > 0:
        from loro.workflow import Workflow
        try:
            workflow = Workflow()
            log.info("Processing %d files", len(inputs))
            for filepath in sorted(inputs):
                workflow.start(filepath)
        except KeyError as error:
            log.error("Source language '%s' not supported yet", source)
    else:
        log.warning("No input files found for source language '%s' and target language '%s'", source, target)
        log.info("Based on the current configuration, you should place some text files in the following directory:")
        directory = get_project_input_dir(source, target)
        log.info("file://%s", directory)
