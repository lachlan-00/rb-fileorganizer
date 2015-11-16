#!/usr/bin/env python3

""" FileOrganizer Uninstall Script

    Remove files from the plugin folder

"""

import os
import shutil

INSTALLPATH = os.path.join(os.getenv('HOME'),
                           ".local/share/rhythmbox/plugins/fileorganizer")
TEMPLATEPATH = os.path.join(INSTALLPATH, 'template')

if os.path.isdir(INSTALLPATH):
    shutil.rmtree(INSTALLPATH)
    print('\nFileOrganizer is uninstalled\n')
else:
    print('\nFileOrganizer is not installed\n')
