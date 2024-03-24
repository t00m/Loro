#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

from mako.template import Template
from gi.repository import GObject

from loro.backend.core.env import ENV
from loro.backend.core.log import get_logger
from loro.backend.core.util import get_project_target_workbook_dir

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
        GObject.signal_new('report-finished', Report, GObject.SignalFlags.RUN_LAST, GObject.TYPE_PYOBJECT, (GObject.TYPE_PYOBJECT,) )
        self.templates = {}
        self._add_templates()
        # ~ self.log.debug("Reporting initialized")
        self.app.workflow.connect('workflow-finished', self.update_report)


    def _add_templates(self):
        self.templates['HEADER'] = Template(filename=TPL_HEADER)
        self.templates['BODY'] = Template(filename=TPL_BODY)
        self.templates['FOOTER'] = Template(filename=TPL_FOOTER)
        # ~ self.log.debug("Basic templates added")

    # ~ def build(self, workbook: str) -> str:
        # ~ header = open(TPL_HEADER).read()
        # ~ body = open(TPL_BODY).read()
        # ~ footer = open(TPL_FOOTER).read()
        # ~ html = header.format(   workbook=workbook,
                                # ~ uikit_css=UIKIT_CSS,
                                # ~ uikit_min_js=UIKIT_MIN_JS,
                                # ~ uikit_icons_min_js=UIKIT_ICON_MIN_JS
                            # ~ )
        # ~ html += body.format(    workbook=workbook
                            # ~ )
        # ~ html += footer
        # ~ with open('/tmp/test.html', 'w') as fhtml:
            # ~ fhtml.write(html)
        # ~ self.log.info("Workbook Report['%s'] built successfully", workbook)
        # ~ return '/tmp/test.html'

    def template(self, name: str):
        return self.templates[name]

    def render_template(self, name, var={}):
        tpl = self.template(name)
        return tpl.render(var=var)

    def build(self, workbook: str) -> str:
        source, target = ENV['Projects']['Default']['Languages']
        DIR_OUTPUT = get_project_target_workbook_dir(source, target, workbook)
        REPORT = os.path.join(DIR_OUTPUT, '%s.html' % workbook)
        var = {}
        var['workbook'] = {}
        var['workbook']['id'] = workbook
        var['workbook']['cache'] = self.app.workbooks.get_dictionary(workbook)
        var['workbook']['stats'] = self.app.stats.get(workbook)
        var['html'] = {}
        var['html']['uikit'] = {}
        var['html']['uikit']['css'] = UIKIT_CSS
        var['html']['uikit']['icon'] = UIKIT_ICON_MIN_JS
        var['html']['uikit']['js'] = UIKIT_MIN_JS

        header = self.render_template('HEADER', var)
        body = self.render_template('BODY', var)
        footer = self.render_template('FOOTER', var)
        html = header + body + footer
        with open(REPORT, 'w') as fout:
            fout.write(html)
            # ~ self.log.debug("Report saved to: %s", REPORT)
        # ~ self.log.debug("Report['%s'] built" % workbook)
        return html

    def update_report(self, workflow, workbook):
        self.build(workbook)
        # ~ self.emit('report-finished', workbook)
