#!/usr/bin/env python3

""" FileOrganizer Safe Install Script

    Install if dependancies are satisfied

"""

import os
import shutil

import depends_test


INSTALLPATH = os.path.join(os.getenv('HOME'),
                           ".local/share/rhythmbox/plugins/fileorganizer")
TEMPLATEPATH = os.path.join(INSTALLPATH, 'template')

# The depends test will check for required modules
if(depends_test.check()):
    # check plugin directory
    if not os.path.exists(INSTALLPATH):
        os.makedirs(INSTALLPATH)
    # check template directory
    if not os.path.exists(TEMPLATEPATH):
        os.makedirs(TEMPLATEPATH)
    # copy the base template
    shutil.copy('template/fo.conf', TEMPLATEPATH)
    # copy the rest of the plugin
    for i in os.listdir('./'):
        if os.path.isfile(i):
            shutil.copy(i, INSTALLPATH)
    print('\nFileOrganizer is now installed\n')
else:
    print('please check your OS for missing packages')
