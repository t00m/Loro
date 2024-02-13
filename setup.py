#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
# File: setup.py.
# Author: Tomás Vírseda
# License: GPL v3
# Description: Setup Loro project
"""

import os
import glob
from setuptools import setup

from Loro.backend.env import ENV

with open('README.adoc', 'r') as f:
    LONG_DESCRIPTION = f.read()


def add_data(root_data):
    """Add data files from a given directory."""
    dir_files = []
    resdirs = set()
    for root, dirs, files in os.walk(root_data):
        resdirs.add(os.path.realpath(root))

    resdirs.remove(os.path.realpath(root_data))

    for directory in resdirs:
        files = glob.glob(os.path.join(directory, '*'))
        relfiles = []
        for thisfile in files:
            if not os.path.isdir(thisfile):
                relfiles.append(os.path.relpath(thisfile))

        num_files = len(files)
        if num_files > 0:
            dir_files.append((os.path.relpath(directory), relfiles))

    return dir_files

DATA_FILES = add_data('Loro/data')
DATA_FILES += ['README.adoc']
DATA_FILES +=[('share/applications', ['Loro/data/resources/com.github.t00m.Loro.desktop'])]
DATA_FILES +=[('share/icons/hicolor/48x48/apps/', ['Loro/data/icons/com.github.t00m.Loro.svg'])]

setup(
    name=ENV['APP']['shortname'],
    version=open('Loro/data/docs/VERSION', 'r').read().strip(),
    author=ENV['APP']['author'],
    author_email=ENV['APP']['author_email'],
    url=ENV['APP']['website'],
    description='A personal document organizer',
    long_description=LONG_DESCRIPTION,
    download_url='https://github.com/t00m/Loro/archive/master.zip',
    license=ENV['APP']['license'],
    packages=[
                'Loro',
                'Loro.backend',
                'Loro.frontend',
                'Loro.frontend.console',
                'Loro.frontend.desktop',
                'Loro.frontend.desktop.widgets'
            ],
    # distutils does not support install_requires, but pip needs it to be
    # able to automatically install dependencies
    install_requires=[],
    include_package_data=True,
    data_files=DATA_FILES,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: X11 Applications :: GTK',
        'Environment :: X11 Applications :: Gnome',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Utilities',
        'Topic :: Desktop Environment :: Gnome',
        'Topic :: Office/Business'
    ],
    entry_points={
        'console_scripts': [
            'loro = Loro.main:main',
            ],
        },
)
