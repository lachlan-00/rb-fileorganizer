#!/usr/bin/env python3

""" Fileorganizer path helpers

    Where the plugin's own files (the log and the preview reports) live.
    This module imports nothing else from the plugin on purpose: fileops,
    tools and logops all need it, and they already import each other.

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""

import os

from gi.repository import GLib


FLATPAK_MARKER = '/.flatpak-info'
DATA_FOLDER = 'rhythmbox/fileorganizer'

_FOLDER = None


def is_flatpak():
    """ Are we running inside a flatpak sandbox """
    return os.path.exists(FLATPAK_MARKER)


def user_folder():
    """ Folder to write the log and the preview reports into

    On a normal install that is the home folder, where the log has always
    lived. A flatpak cannot see the real home: $HOME is an empty tmpfs that
    accepts writes and discards them when the app exits, so anything put
    there is lost without an error. Use the sandbox's own data directory,
    which the host can still read, instead.
    """
    global _FOLDER
    if _FOLDER:
        return _FOLDER
    if not is_flatpak():
        _FOLDER = os.path.expanduser('~')
        return _FOLDER
    folder = os.path.join(GLib.get_user_data_dir(), DATA_FOLDER)
    # worked out once: this is called for every line written to the log
    os.makedirs(folder, exist_ok=True)
    _FOLDER = folder
    return _FOLDER


def user_file(name):
    """ Full path for one of the plugin's own files

    An absolute name is used as given, so a log path pointing somewhere
    specific keeps working.
    """
    if os.path.isabs(name):
        return name
    return os.path.join(user_folder(), name)
