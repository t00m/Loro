import os
import sys

HOME = os.environ['HOME']
PKGDATADIR = os.path.join(HOME, '.local/share/loro')
sys.path.insert(1, PKGDATADIR)
from loro.extractors import whatsapp

