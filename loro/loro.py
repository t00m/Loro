#!@PYTHON@

# Copyright 2024 Tomás Vírseda
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import signal
import locale
import gettext

APP_DATA = {}
APP_DATA['APP_ID'] = '@APP_ID@'
APP_DATA['VERSION'] = '@VERSION@'
APP_DATA['pkgdatadir'] = '@pkgdatadir@'
APP_DATA['localedir'] = '@localedir@'

sys.path.insert(1, APP_DATA['pkgdatadir'])
signal.signal(signal.SIGINT, signal.SIG_DFL)
gettext.install('loro', APP_DATA['localedir'])

try:
  locale.bindtextdomain('loro', APP_DATA['localedir'])
  locale.textdomain('loro')
except:
  print('Cannot set locale.')
try:
  gettext.bindtextdomain('loro', APP_DATA['localedir'])
  gettext.textdomain('loro')
except:
  print('Cannot load translations.')

if __name__ == '__main__':
    import gi
    from gi.repository import Gio
    resource = Gio.Resource.load(os.path.join(APP_DATA['pkgdatadir'], 'loro.gresource'))
    resource._register()

    from loro import main
    sys.exit(main.main(APP_DATA))
