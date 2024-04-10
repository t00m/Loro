#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint


from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_config_dir
from loro.backend.core.util import get_project_input_dir


class Workbook:
    def __init__(self, app):
        self.log = get_logger('Workbook')
        self.app = app
        self._check()
        # ~ self.log.debug('Workbooks initializated')
        # ~ self.log.debug('Workbooks found: %d', len(self.get_all()))

    def _check(self, *args):
        workbooks_path = os.path.join(get_project_config_dir(), 'workbooks.json')
        if not os.path.exists(workbooks_path):
            self._save({})
            self.log.debug("Created workbooks configuration (empty)")

        for workbook in self.get_all():
            cache_dir = self.app.cache.get_cache_dir(workbook)
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
                self.log.debug("Cache directory created for workbook '%s':", workbook)
                self.log.debug("%s", cache_dir)

    def get_all(self):
        workbooks_path = os.path.join(get_project_config_dir(), 'workbooks.json')
        if not os.path.exists(workbooks_path):
            self.log.warning("Workbooks config path['%s'] do not exist", workbooks_path)
            return {}
        workbooks = json_load(workbooks_path)
        return workbooks

    def get_files(self, wbname):
        valid_files = []
        try:
            filenames = self.get_all()[wbname]
            for filename in filenames:
                filepath = os.path.join(get_project_input_dir(), filename)
                if os.path.exists(filepath):
                    valid_files.append(filename)
                else:
                    self.log.warning("File '%s' skipped. It doesn't exist", filename)
        except KeyError:
            self.log.warning("Workbook['%s'] not found", wbname)

        return valid_files

    def exists(self, name: str) -> bool:
        return name.upper() in self.get_all().keys()

    def add(self, name: str) -> None:
        workbooks = self.get_all()
        workbooks[name.upper()] = []
        self._save(workbooks)
        self.log.debug("Workbook '%s' added", name)
        self._check()

    def rename(self, old_name: str, new_name: str) -> bool:
        if old_name == new_name:
            self.log.debug("Workbook not renamed: identical names")
            return False
        else:
            workbooks = self.get_all()
            workbooks[new_name.upper()] = workbooks[old_name]
            del(workbooks[old_name])
            self._save(workbooks)
            self.log.debug("Workbook '%s' renamed to '%s'", old_name, new_name)
            self._check()
            return True

    def update(self, wbname:str, fname:str, active:bool):
        workbooks = self.get_all()
        try:
            fnames = workbooks[wbname]
        except:
            return

        changes = False
        if active:
            if not fname in fnames:
                fnames.append(fname)
                workbooks[wbname] = fnames
                changes = True
        else:
            if fname in fnames:
                fnames.remove(fname)
                workbooks[wbname] = fnames
                changes = True

        if changes:
            self._save(workbooks)

    def have_file(self, wbname: str, fname: str) -> bool:
        try:
            return fname in self.get_all()[wbname]
        except KeyError:
            return False

    def delete(self, name:str) -> None:
        if self.exists(name):
            workbooks = self.get_all()
            del(workbooks[name])
            self._save(workbooks)
            self.log.debug("Workbook '%s' deleted", name)

    def _save(self, workbooks):
        workbooks_path = os.path.join(get_project_config_dir(), 'workbooks.json')
        json_save(workbooks_path, workbooks)
        # ~ self.log.debug("%d workbooks saved", len(workbooks))
