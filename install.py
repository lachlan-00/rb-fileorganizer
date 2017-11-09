#!/usr/bin/env python3

""" FileOrganizer Safe Install Script

    Install if dependencies are satisfied

"""

import os
import shutil

import depends_test

INSTALLPATH = os.path.join(os.getenv('HOME'),
                           ".local/share/rhythmbox/plugins/fileorganizer")

# The depends test will check for required modules
if depends_test.check():
    # check plugin directory
    if not os.path.exists(INSTALLPATH):
        os.makedirs(INSTALLPATH)
    # copy the contents of the plugin directory
    for i in os.listdir('./'):
        if os.path.isfile(i):
            print('Copying... ' + i)
            shutil.copy(i, INSTALLPATH)
    print('\nFileOrganizer is now installed\n')
else:
    print('please check your OS for missing packages')
