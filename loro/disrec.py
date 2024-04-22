#!/usr/bin/python
# -*- coding: utf-8 -*-
# File: disrec.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Disaster Recovery (backup/restore)

import zipfile

from loro.backend.core.log import get_logger

class DisasterRecovery:
    def __init__(self, app):
        self.app = app
        self.log = get_logger('DisasterRecovery')
        self.log.debug('Disaster Recovery initialited')

    def backup_translations(self, *args):
        tr_tokens = self.app.translate.get_cache_path_tokens()
        tr_sents = self.app.translate.get_cache_path_sentences()

    def zip(self, filename: str, directory: str):
        """ Zip directory into a file """
        self.log.debug("Target: %s", filename)
        sourcename = os.path.basename(filename)
        dot = sourcename.find('.')
        if dot == -1:
            basename = sourcename
        else:
            basename = sourcename[:dot]
        sourcedir = os.path.dirname(filename)
        source = os.path.join(sourcedir, basename)
        zipfile = shutil.make_archive(source, 'zip', directory)
        target = source + '.zip'
        shutil.move(zipfile, target)
        return target

    def unzip(self, target: str, install_dir):
        """
        Unzip file to a given dir
        """
        zip_archive = zipfile.ZipFile(target, "r")
        zip_archive.extractall(path=install_dir)
        zip_archive.close()
