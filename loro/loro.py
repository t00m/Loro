#!@PYTHON@

# Copyright 2024 Tomás Vírseda
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import math
import signal
import locale
import gettext
import argparse
import multiprocessing

import gi
from gi.repository import Gio
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw
from gi.repository import Gtk

from rich.traceback import install
# ~ install(show_locals=True)

sys.path.insert(1, '@pkgdatadir@')

from loro.backend.core.env import ENV

ENV['APP'] = {}
ENV['APP']['ID'] = '@APP_ID@'
ENV['APP']['VERSION'] = '@VERSION@'
ENV['APP']['PGKDATADIR'] = '@pkgdatadir@'
ENV['APP']['LOCALEDIR'] = '@localedir@'

signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.install('loro', ENV['APP']['LOCALEDIR'])

try:
  locale.bindtextdomain('loro', ENV['APP']['LOCALEDIR'])
  locale.textdomain('loro')
except:
  print('Cannot set locale.')
try:
  gettext.bindtextdomain('loro', ENV['APP']['LOCALEDIR'])
  gettext.textdomain('loro')
except:
  print('Cannot load translations.')

def get_default_workers():
    """Calculate default number or workers.
    Workers = Number of CPU / 2
    Minimum workers = 1
    """
    ncpu = multiprocessing.cpu_count()
    workers = ncpu/2
    return math.ceil(workers)

def main() -> None:
    resource = Gio.Resource.load(os.path.join(ENV['APP']['PGKDATADIR'], 'loro.gresource'))
    resource._register()
    sys.exit(Application().run(sys.argv))

class Application(Adw.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=ENV['APP']['ID'],
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.set_resource_base_path("/com/github/t00m/Loro/")

    def do_activate(self) -> None:
        from loro.frontend.gui.widgets.window import Window

        Window(application=self)

        # ~ # Run tests
        # ~ if PROFILE == "development":
            # ~ from loro.tests.tests import run_tests

            # ~ run_tests()

if __name__ == "__main__":
    # Loro arguments
    # ~ """Set up application arguments and execute."""
    extra_usage = """"""
    # ~ formatter_class=argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        prog='loro',
        description='%s v%s\nApplication for helping to study another language' % (ENV['APP']['ID'], ENV['APP']['VERSION']),
        epilog=extra_usage,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    WORKERS = get_default_workers()
    parser = argparse.ArgumentParser(add_help=False)
    loro_options = parser.add_argument_group('Loro Options')
    loro_options.add_argument('-s', '--source', help='Source language (2 letters)', action='store', dest='SOURCE')
    loro_options.add_argument('-t', '--target', help='Target language (2 letters)', action='store', dest='TARGET')
    loro_options.add_argument('-w', '--workers', help='Number of workers. Default is CPUs available/2. Default number of workers in this machine: %d' % WORKERS, type=int, action='store', dest='WORKERS', default=int(WORKERS))
    loro_options.add_argument('-L', '--log', help='Control output verbosity. Default set to INFO', dest='LOGLEVEL', action='store', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO')
    loro_options.add_argument('-v', '--version', help='Show current version', action='version', version='%s %s' % (ENV['APP']['ID'], ENV['APP']['VERSION']))
    loro_options.add_argument('-r', '--reset', help="Warning! Delete configuration for source/target languages", action='store_true', dest='RESET', default=False)
    params = parser.parse_args()
    from loro.main import main
    main(params)




