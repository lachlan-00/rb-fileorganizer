#!/usr/bin/env python3

""" Fileorganizer tools

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


import os

import fileops


# Create a folder if non-existant, and return it
def folderize(configurator, folder):
    """ Create folders for file operations """
    dirpath = ((configurator.get_val('locations'))[0]
                                 + '/').replace('file:///', '/')
    if not os.path.exists(dirpath + folder):
        os.makedirs(dirpath + folder)
    return os.path.normpath(dirpath + folder)


# Replace the placeholders with the correct values
def data_filler(files, string):
    """ replace string data with metadata from current item """
    string = str(string)
    for key in fileops.RB_METATYPES:
        if ('%' + key) in string:
            if key == 'aa':
                artisttest = files.get_metadata('aa')
                if artisttest == '':
                    string = string.replace(('%' + key),
                                            process(files.get_metadata('ta')))
                    print(string + ' ALBUM ARTIST NOT FOUND')
                else:
                    string = string.replace(('%' + key),
                                            process(files.get_metadata(key)))
                    print(string + ' ALBUM ARTIST FOUND')
            else:
                string = string.replace(('%' + key),
                                        process(files.get_metadata(key)))
    return string


# Process names and replace any undesired characters
def process(string):
    """ Prevent / character to avoid creating folders """
    string = string.replace('/', '_')  # if present
    return string
