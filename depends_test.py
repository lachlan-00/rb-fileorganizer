#!/usr/bin/env python3

""" Fileorganizer: test your dependencies

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
        import configparser
        import shutil
        import time
        import gi

        gi.require_version('Gtk', '3.0')
        gi.require_version('Peas', '1.0')
        gi.require_version('PeasGtk', '1.0')
        gi.require_version('Notify', '0.7')
        gi.require_version('RB', '3.0')

        from gi.repository import GObject, Peas, PeasGtk, Gtk, Notify, Gio
        from gi.repository import GLib
        from gi.repository import RB

        clear = True
    except ImportError as errormsg:
        print('\nDependency Problem\n\n' + str(errormsg))
    except ValueError as errormsg:
        # gi.require_version raises this for a typelib it cannot find
        print('\nDependency Problem\n\n' + str(errormsg))

    if clear:
        print('\nAll FileOrganizer dependencies are satisfied\n')
        return True
    else:
        return False
