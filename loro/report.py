#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from gi.repository import GObject

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger

# UIKIT (getuikit.com)
DIR_UIKIT = os.path.join(ENV['APP']['PGKDATADIR'], 'resources', 'web', 'uikit')
DIR_UIKIT_CSS = os.path.join(DIR_UIKIT, 'css')
UIKIT_CSS = os.path.join(DIR_UIKIT_CSS, 'uikit.min.css')
DIR_UIKIT_JS = os.path.join(DIR_UIKIT, 'js')
UIKIT_MIN_JS = os.path.join(DIR_UIKIT_JS, 'uikit.min.js')
UIKIT_ICON_MIN_JS = os.path.join(DIR_UIKIT_JS, 'uikit-icons.min.js')

# Loro UIKit based templates
DIR_TPL = os.path.join(DIR_UIKIT, 'tpl')
TPL_HEADER = os.path.join(DIR_TPL, 'HTML_HEADER.tpl')
TPL_BODY = os.path.join(DIR_TPL, 'HTML_BODY.tpl')
TPL_FOOTER = os.path.join(DIR_TPL, 'HTML_FOOTER.tpl')



class Report(GObject.GObject):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.log = get_logger('Report')
        GObject.GObject.__init__(self)
        GObject.signal_new('report-finished', Report, GObject.SignalFlags.RUN_LAST, None, () )
        self.log.debug("Reporting initialized")
        # ~ a = tpl.format(workbook = 'A1', uikit_css = 'a', uikit_min_js = 'b', uikit_icons_min_js = 'c')

    def build(self, workbook: str) -> str:
        header = open(TPL_HEADER).read()
        body = open(TPL_BODY).read()
        footer = open(TPL_FOOTER).read()
        html = header.format(   workbook=workbook,
                                uikit_css=UIKIT_CSS,
                                uikit_min_js=UIKIT_MIN_JS,
                                uikit_icons_min_js=UIKIT_ICON_MIN_JS
                            )
        html += body.format(    workbook=workbook
                            )
        html += footer
        with open('/tmp/test.html', 'w') as fhtml:
            fhtml.write(html)
        self.log.info("Workbook Report['%s'] built successfully", workbook)
        return '/tmp/test.html'


