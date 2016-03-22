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


# Create a folder inside a library path if non-existant, and return it
def folderize(library_path, folder):
    """ Create folders for file operations """
    dirpath = library_path + '/'
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

#tag operations
def update_tags(inputfile):
    """ Update file tags (if enabled) """
    ##TAG SUPPORT NOT AVAILABLE IN PYTHON3
    ##update_tags = self.conf.get('conf', 'update_tags')
    #update_tags = 'False'
    ##if update_tags == 'True' and EYED3_SUPPORT:
    ##    self.log.log_processing('           Updating File Tags')
    ##    tags = eyeD3.Tag()
    ##    if mimetypes.guess_type(inputfile)[0] == 'audio/mpeg':
    ##        print('UPDATING TAGS')
    ##        artist = (self.entry.get_string(RB.RhythmDBPropType.ARTIST)
    ##                        ).decode('utf-8')
    ##        albumartist = (self.entry.get_string(
    ##                            RB.RhythmDBPropType.ALBUM_ARTIST)
    ##                            ).decode('utf-8')
    ##        album = (self.entry.get_string(RB.RhythmDBPropType.ALBUM)
    ##                        ).decode('utf-8')
    ##        title = (self.entry.get_string(RB.RhythmDBPropType.TITLE)
    ##                        ).decode('utf-8')
    ##        genre = (self.entry.get_string(RB.RhythmDBPropType.GENRE))
    ##        tags.link(inputfile)
    ##        tags.setVersion(eyeD3.ID3_V2_4)
    ##        tags.setTextEncoding(eyeD3.UTF_8_ENCODING)
    ##        tags.setArtist(artist)
    ##        tags.setArtist(albumartist, 'TPE2')
    ##        tags.setTrackNum([str(self.entry.get_ulong(
    ##                            RB.RhythmDBPropType.TRACK_NUMBER)), None])
    ##        tags.setDiscNum([str(self.entry.get_ulong(
    ##                            RB.RhythmDBPropType.DISC_NUMBER)), None])
    ##        #tags.setDate(str(self.entry.get_ulong(
    ##        #                    RB.RhythmDBPropType.YEAR)), 0)
    ##        # Ryan Koesters caught my typo. Cheers!
    ##        tags.setTextFrame('TDRC', str(self.entry.get_ulong(
    ##                                      RB.RhythmDBPropType.YEAR)))
    ##        tags.setTextFrame('TDRL', str(self.entry.get_ulong(
    ##                                      RB.RhythmDBPropType.YEAR)))
    ##        tags.setAlbum(album)
    ##        tags.setTitle(title)
    ##        tags.setGenre(genre)
    ##        tags.update(eyeD3.ID3_V2_4)
    return

def check_bad_file(inputfile):
    """ Check the input file for missing tags. (MP3 files only) """
    ###TAG SUPPORT NOT AVAILABLE IN PYTHON3???\
    # Only check MP3's
    ###if not mimetypes.guess_type(inputfile)[0] == 'audio/mpeg':
    ###    return True
    ###tags = eyeD3.Tag()
    ###tags.link(inputfile)
    #fail on important tags
    ###if (tags.getArtist() == '' or tags.getTitle() == ''
    ###        or tags.getAlbum() == ''):
    ###    return False
    ###if str(tags.getYear()) == 'None':
    ###    try:
    ###        if tags.getDate(0)[0].text == '':
    ###            return False
    ###    except TypeError:
    ###        return False
    return True
