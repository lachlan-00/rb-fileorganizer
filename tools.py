#!/usr/bin/env python3

""" Fileorganizer tools

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""

import os
import subprocess

import fileops


class LibraryLocationError(Exception):
    """To be raised when a file:// library location could not be found"""


# Returns the library location for a file,
# or the default location if the file is not inside any library location
# Raises an error if there are no file:// locations in the library
def library_location(files, library_locations):
    file_locations = list(l for l in library_locations if l.startswith('file://'))
    if not file_locations:
        raise LibraryLocationError('No file:// locations could be found in the library')
    return next((l for l in file_locations if files.location.startswith(l)),
                file_locations[0])


# Create a folder inside a library path if non-existent, and return it
def folderize(library_path, folder):
    """ Create folders for file operations """
    dirpath = library_path + '/'
    # Strip full stops from paths
    folder = folder.replace('/.', '/_')
    if not os.path.exists(dirpath + folder):
        os.makedirs(dirpath + folder)
    return os.path.normpath(dirpath + folder)


# Replace the placeholders with the correct values
def data_filler(files, string, strip_ntfs=False):
    """ replace string data with metadata from current item """
    string = str(string)
    for key in fileops.RB_METATYPES:
        if '%' + key in string:
            if key == 'aa':
                artisttest = files.get_metadata('aa')
                if artisttest == '':
                    string = string.replace(('%' + key),
                                            process(files.get_metadata('ta'),
                                                    strip_ntfs))
                    print(string + ' ALBUM ARTIST NOT FOUND')
                else:
                    string = string.replace(('%' + key),
                                            process(files.get_metadata(key),
                                                    strip_ntfs))
                    print(string + ' ALBUM ARTIST FOUND')
            else:
                string = string.replace(('%' + key),
                                        process(files.get_metadata(key),
                                                strip_ntfs))
    return string


# Process names and replace any undesired characters
def process(string, strip_ntfs=False):
    """ Prevent / character to avoid creating folders """
    string = string.replace('/', '_')  # if present
    if strip_ntfs:
        string = ''.join(c for c in string if c not in '<>:"\\|?*')
        while string.endswith('.'):
            string = string[:-1]
    return string


def results(prelist, damlist):
    """ Show the results of your preview run """
    if not os.stat(prelist)[6] == 0:
        print('fileorganizer: open preview list')
        subprocess.Popen(['/usr/bin/xdg-open', prelist])
    if not os.stat(damlist)[6] == 0:
        print('fileorganizer: open damaged file list')
        subprocess.Popen(['/usr/bin/xdg-open', damlist])
    return

