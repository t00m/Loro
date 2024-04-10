#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from gi.repository import GObject

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import create_directory, delete_directory
from loro.backend.core.util import get_project_target_workbook_build_dir
from loro.backend.core.util import get_metadata_from_filename
from kb4it.core.env import ENV as KB4ITENV

EOHMARK = KB4ITENV['CONF']['EOHMARK']


class Builder(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Builder')
        self.log.debug("Builder initialized")

    def kb(self, workbook: str):

        # Initialize build directory
        source, target = ENV['Projects']['Default']['Languages']
        DIR_BUILD = get_project_target_workbook_build_dir(workbook)
        if os.path.exists(DIR_BUILD):
            delete_directory(DIR_BUILD)
        create_directory(DIR_BUILD)

        topics = set()
        subtopics = set()
        suffixes = set()
        filenames = self.app.workbooks.get_files(workbook)
        for filename in filenames:
            contents = ''
            topic, subtopic, suffix = get_metadata_from_filename(filename)
            topics.add(topic)
            subtopics.add(subtopic)
            suffixes.add(suffix)
            kbname = filename.replace('.txt', '.adoc')
            self.log.debug(kbname)
            title = "= %s: %s (%s)\n" % (topic, subtopic, suffix)
            contents += title
            contents += ":Workbook: %s\n" % workbook
            contents += ":Topic:    %s\n" % topic
            contents += ":Subtopic:    %s\n" % subtopic
            contents += ":Suffix:    %s\n" % suffix
            contents += "%s\n\n" % EOHMARK
            contents += "== %s: %s\n" % (workbook, filename)
            contents += "Something here"

            kbtarget = os.path.join(DIR_BUILD, kbname)
            with open(kbtarget, 'w') as fkb:
                fkb.write(contents)
                self.log.debug("KB %s written to %s", kbname, kbtarget)

        kbname = 'Workbook_%s.adoc' % workbook
        kbtarget = os.path.join(DIR_BUILD, kbname)
        contents = "= Workbook %s\n" % workbook
        contents += ":Topic: %s\n" % ', '.join(topics)
        contents += ":Subtopic: %s\n" % ', '.join(subtopics)
        contents += ":Suffix: %s\n" % ', '.join(suffixes)
        contents += "%s\n\n" % EOHMARK
        contents += "== Workbook %s\n" % (workbook)
        contents += ', '.join(filenames)

        with open(kbtarget, 'w') as fkb:
            fkb.write(contents)
        self.log.debug("KB %s written to %s", kbname, kbtarget)

        cache = self.app.cache.get_cache(workbook)
        # ~ self.log.debug(cache)





# ~ from kb4it.kb4it import KB4IT
# ~ from argparse import Namespace
# ~ params = Namespace(
                    # ~ RESET=False, \
                    # ~ FORCE=True, \
                    # ~ LOGLEVEL='INFO', \
                    # ~ SORT_ATTRIBUTE=None, \
                    # ~ SOURCE_PATH='/tmp/sources', \
                    # ~ TARGET_PATH='/tmp/output', \
                    # ~ THEME='techdoc'
                # ~ )
# ~ kb = KB4IT(params)
# ~ kb.run()
