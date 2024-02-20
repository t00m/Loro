import os
import sys
import signal
import locale
import gettext

from loro.core.log import get_logger
from loro.core.env import ENV
from loro.core.util import setup_project_dirs
from loro.core.util import get_inputs
from loro.workflow import Workflow

APP_ID = "@APP_ID@"
VERSION = "@VERSION@"
PREFIX = "@PREFIX@"
PROFILE = "@PROFILE@"
pkgdatadir = "@pkgdatadir@"
localedir = "@localedir@"

# ~ sys.path.insert(1, pkgdatadir)
# ~ signal.signal(signal.SIGINT, signal.SIG_DFL)
# ~ gettext.install("errands", localedir)
# ~ locale.bindtextdomain("errands", localedir)
# ~ locale.textdomain("errands")
# ~ print(APP_ID)


def main(APP_ID, VERSION):
    log = get_logger('main')
    log.info("%s %s", APP_ID, VERSION)
    # ~ log.info("Prefix: %s", PREFIX)
    # ~ log.info("Profile: %s", PROFILE)
    source, target = ENV['Projects']['Default']['Languages']
    model_type = ENV['Languages'][source]['model']['default']
    model_name = ENV['Languages'][source]['model'][model_type]
    setup_project_dirs(source, target)
    # ~ log.info("Loading model '%s' for language '%s'", model_name, source)
    workflow = Workflow(model_name)
    # ~ workflow.init(model_name)

    for filepath in get_inputs(source):
        workflow.start(filepath)

