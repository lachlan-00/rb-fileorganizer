#!/usr/bin/env python3

""" Configuration (gsettings) handler for Fileorganizer

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


from gi.repository import Gio

# Gsettings locations for library and output paths
RHYTHMBOX_RHYTHMDB = 'locations'
RHYTHMBOX_LIBRARY = {'layout-path', 'layout-filename'}


class FileorganizerConf(object):
    """ Class to read RB values using dconf/gsettings """
    def __init__(self):
        self.rhythmdbsettings = Gio.Settings("org.gnome.rhythmbox.rhythmdb")
        self.librarysettings = Gio.Settings("org.gnome.rhythmbox.library")

    # Request value
    def get_val(self, key):
        """ Fill values according to the current value in gsettings """
        keypath = None
        if key == RHYTHMBOX_RHYTHMDB:
            return self.rhythmdbsettings[key]
        elif key in RHYTHMBOX_LIBRARY:
            return self.librarysettings[key]
        else:
            print('Invalid key requested')
            return keypath
