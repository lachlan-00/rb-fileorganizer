#!/usr/bin/env python3

""" Fileorganizer: test your dependancies

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""

def check():
    """ Importing all libraries used by FileOrganizer """
    clear = False
    try:
        import os
        import codecs
        import configparser
        import shutil
        import subprocess
        import time

        from gi.repository import GObject, Peas, PeasGtk, Gtk, Notify, Gio

        from gi.repository import RB

        from urllib.request import url2pathname
        from urllib.request import pathname2url
        clear = True
    except ImportError as errormsg:
        print('\nDependancy Problem\n\n' + str(errormsg))

    if clear:
        print('\nAll FileOrganizer dependancies are satisfied\n')
        return True
    else:
        return False
