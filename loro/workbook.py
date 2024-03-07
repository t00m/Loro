#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pprint

from spacy.tokens import Token

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import json_load, json_save
from loro.backend.core.util import get_project_config_dir


class Workbook:
    def __init__(self):
        self.log = get_logger('Workbook')


    def get_workbooks(self):
        source, target = ENV['Projects']['Default']['Languages']
        config_dir = get_project_config_dir(source)
        workbooks_path = os.path.join(config_dir, 'workbooks.json')
        if not os.path.exists(workbooks_path):
            return {}
        return json_load(workbooks_path)

    def get_workbook_entries(self, wbname):
        return self.get_workbooks()[wbname]

    def exists_workbook(self, name: str) -> bool:
        return name.upper() in self.get_workbooks().keys()

    def add_workbook(self, name: str) -> None:
        workbooks = self.get_workbooks()
        workbooks[name.upper()] = []
        self._save_workbooks(workbooks)
        self.log.debug("Workbook '%s' added", name)

    def rename_workbook(self, old_name: str, new_name: str) -> bool:
        workbooks = self.get_workbooks()
        workbooks[new_name.upper()] = workbooks[old_name]
        del(workbooks[old_name])
        self._save_workbooks(workbooks)
        self.log.debug("Workbook '%s' renamed to '%s'", old_name, new_name)

    def update_workbook(self, wbname:str, fname:str, active:bool):
        workbooks = self.get_workbooks()
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
            self._save_workbooks(workbooks)

    def filename_in_workbook(self, wbname: str, fname: str) -> bool:
        return fname in self.get_workbooks()[wbname]

    def delete_workbook(self, name:str) -> None:
        if self.exists_workbook(name):
            workbooks = self.get_workbooks()
            del(workbooks[name])
            self._save_workbooks(workbooks)
            self.log.debug("Workbook '%s' deleted", name)

    def _save_workbooks(self, workbooks):
        source, target = ENV['Projects']['Default']['Languages']
        config_dir = get_project_config_dir(source)
        workbooks_path = os.path.join(config_dir, 'workbooks.json')
        json_save(workbooks_path, workbooks)
        self.log.debug("%d workbooks saved", len(workbooks))
