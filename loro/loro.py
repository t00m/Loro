#!@PYTHON@

# Copyright 2024 Tomás Vírseda
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import signal
import locale
import gettext

from rich.traceback import install
install(show_locals=True)

sys.path.insert(1, '@pkgdatadir@')

from loro.core.env import ENV

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



if __name__ == '__main__':
    import gi
    from gi.repository import Gio
    resource = Gio.Resource.load(os.path.join(ENV['APP']['PGKDATADIR'], 'loro.gresource'))
    resource._register()

    from loro import main
    sys.exit(main.main())
