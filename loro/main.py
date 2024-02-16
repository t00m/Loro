import os

from MiAZ.backend.log import get_logger
from loro.core.env import ENV
from loro.core.env import LORO_USER_PROJECTS_DIR
from loro.core.util import setup_project_dirs
from loro.core.util import get_inputs
from loro import workflow

def main(version):
    log = get_logger('main')
    log.info("Loro %s", version)
    workspace = LORO_USER_PROJECTS_DIR
    source, target = ENV['Projects']['Default']['Languages']
    model_type = ENV['Languages'][source]['model']['default']
    model_name = ENV['Languages'][source]['model'][model_type]
    setup_project_dirs(workspace, source, target)
    log.info("User workspace: %s", workspace)
    log.info("Loading model '%s' for language '%s'", model_name, source)
    workflow.init(model_name)

    for filepath in get_inputs(workspace, source):
        log.info("Language '%s' > Processing input file '%s'", source, os.path.basename(filepath))
        workflow.process(workspace, source, filepath)

