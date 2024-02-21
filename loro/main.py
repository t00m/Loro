import os
import sys
import signal
import locale
import gettext

from loro.core.env import ENV
from loro.core.log import get_logger
from loro.core.util import setup_project_dirs
from loro.core.util import get_inputs

def main():
    log = get_logger('main')
    source, target = ENV['Projects']['Default']['Languages']
    model_type = ENV['Languages'][source]['model']['default']
    model_name = ENV['Languages'][source]['model'][model_type]
    log.info("%s %s", ENV['APP']['ID'], ENV['APP']['VERSION'])
    log.info("Source language: %s", source)
    log.info("Target language: %s", target)
    setup_project_dirs(source, target)
    log.info("Loading model '%s' for language '%s'", model_name, source)

    inputs = get_inputs(source, target)
    if len(inputs) > 0:
        from loro.workflow import Workflow
        workflow = Workflow(model_name)
        log.info("Processing %d files", len(inputs))
        for filepath in sorted(inputs):
            workflow.start(filepath)

