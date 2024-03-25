#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from gi.repository import GObject

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import create_directory, delete_directory
from loro.backend.core.util import get_project_target_build_dir


class Builder(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Builder')
        self.log.debug("Builder initialized")

    def kb(self, workbook: str):

        # Initialize build directory
        source, target = ENV['Projects']['Default']['Languages']
        DIR_BUILD = get_project_target_build_dir(source, target, workbook)
        if os.path.exists(DIR_BUILD):
            delete_directory(DIR_BUILD)
        create_directory(DIR_BUILD)


        cache = self.app.dictionary.get_cache(workbook)


