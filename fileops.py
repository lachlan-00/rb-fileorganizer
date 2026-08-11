#!/usr/bin/env python3

""" Fileorganizer file operations

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""

import os
import shutil
import time
import gi

gi.require_version('RB', '3.0')

from gi.repository import Gio
from gi.repository import RB

import paths
import tools


RB_METATYPES = ('at', 'aa', 'aA', 'as', 'aS', 'ay', 'an', 'aN', 'ag', 'aG',
                'tn', 'tN', 'tt', 'ta', 'tA')
RB_MEDIA_TYPES = ['.m4a', '.flac', '.ogg', '.mp2', '.mp3', '.wav', '.spx']

PROP = [RB.RhythmDBPropType.ALBUM, RB.RhythmDBPropType.ALBUM_ARTIST,
        RB.RhythmDBPropType.ALBUM_ARTIST_FOLDED,
        RB.RhythmDBPropType.ALBUM_ARTIST_SORTNAME,
        RB.RhythmDBPropType.ALBUM_ARTIST_SORTNAME_FOLDED,
        RB.RhythmDBPropType.YEAR, RB.RhythmDBPropType.DISC_NUMBER,
        RB.RhythmDBPropType.GENRE, RB.RhythmDBPropType.GENRE_FOLDED,
        RB.RhythmDBPropType.TRACK_NUMBER, RB.RhythmDBPropType.TITLE,
        RB.RhythmDBPropType.ARTIST, RB.RhythmDBPropType.ARTIST_FOLDED]

PREVIEW_LOG = '.fileorganizer-preview.log'
DAMAGED_LOG = '.fileorganizer-damaged.log'
BACKUP_FOLDER = 'backup'

IN = '    IN:    '
OUT = '    OUT:   '
INFO = ' ** INFO:  '
ERROR = ' ** ERROR: '
CONFLICT = ' ** CONFLICT: '
NO_NEED = 'No need for file relocation'
STILL_MEDIA = 'Directory still contains media; keeping:'
FILE_EXISTS = 'File exists, directing to backup folder'
POSSIBLE_DAMAGE = 'Source file damaged or missing tag information.'
DIR_REMOVED = 'Removing empty directory'
UPDATING = 'Updating Database:'


def uri_to_path(uri):
    """ Filesystem path for a location as RhythmDB stores it

    None when the location is not a local file, an http stream say.
    """
    return Gio.File.new_for_uri(uri).get_path()


def path_to_uri(path):
    """ Location for a filesystem path

    Rhythmbox builds the locations it stores with g_file_get_uri, so going
    back through GFile is what makes the two match. Escaping the path by
    hand cannot: the plugin used to percent-encode with urllib and then
    undo eighteen characters one at a time to get close enough, and any
    path it did not get exactly right left the entry pointing at nothing.
    """
    return Gio.File.new_for_path(path).get_uri()


def unique_path(path):
    """ The path itself, or the first free '<name>N<.ext>' beside it """
    if not os.path.exists(path):
        return path
    stem, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists('%s%d%s' % (stem, counter, extension)):
        counter += 1
    return '%s%d%s' % (stem, counter, extension)


class MusicFile(object):
    """ Class that performs all the file operations """

    def __init__(self, fileorganizer, db_entry=None):
        self.rbfo = fileorganizer
        self.rbdb = self.rbfo.rbdb
        self.settings = self.rbfo.settings
        self.log = self.rbfo.log
        self.strip_ntfs = self.settings['strip-ntfs']
        self.library = None
        self.metadata = {}
        self.location = None
        self.entry = None
        if db_entry:
            # Track and disc digits from gconf
            padded = '%s' % ('%0' + str(2) + '.d')
            single = '%s' % ('%0' + str(1) + '.d')
            self.metadata = {
                RB_METATYPES[0]: db_entry.get_string(PROP[0]),
                RB_METATYPES[1]: db_entry.get_string(PROP[1]),
                RB_METATYPES[2]: db_entry.get_string(PROP[2]),
                RB_METATYPES[3]: db_entry.get_string(PROP[3]),
                RB_METATYPES[4]: db_entry.get_string(PROP[4]),
                RB_METATYPES[5]: str(db_entry.get_ulong(PROP[5])),
                RB_METATYPES[6]: str(single % (db_entry.get_ulong(PROP[6]))),
                RB_METATYPES[7]: str(padded % (db_entry.get_ulong(PROP[6]))),
                RB_METATYPES[8]: db_entry.get_string(PROP[7]),
                RB_METATYPES[9]: db_entry.get_string(PROP[8]),
                RB_METATYPES[10]: str(single % (db_entry.get_ulong(PROP[9]))),
                RB_METATYPES[11]: str(padded % (db_entry.get_ulong(PROP[9]))),
                RB_METATYPES[12]: db_entry.get_string(PROP[10]),
                RB_METATYPES[13]: db_entry.get_string(PROP[11]),
                RB_METATYPES[14]: db_entry.get_string(PROP[12])
            }
            self.location = db_entry.get_string(RB.RhythmDBPropType.LOCATION)
            self.entry = db_entry
            self.library = self.find_library()

    def find_library(self):
        """ Local path of the library location holding this file

        Worked out once, from the location the file started at: the backup
        folder and the empty folder cleanup both have to stay inside the
        library the file came from.
        """
        locations = self.rbfo.configurator.get_val('locations')
        try:
            library = tools.library_location(self, locations)
        except tools.LibraryLocationError:
            return None
        return uri_to_path(library)

    # Returns metadata of the music file
    def get_metadata(self, key):
        """ Return metadata of current file """
        for datum in self.metadata:
            if key == datum:
                return self.metadata[datum]

    def source_path(self):
        """ Filesystem path the database entry points at """
        return uri_to_path(self.location)

    def target_path(self, create=True):
        """ Filesystem path the Rhythmbox layout settings ask for

        Pass create=False to work it out without making the folders, which
        is what preview mode needs.
        """
        if not self.library:
            raise tools.LibraryLocationError(
                'No local library location for ' + str(self.location))
        layout = tools.data_filler(self,
                                   self.rbfo.configurator.get_val(
                                       'layout-path'),
                                   strip_ntfs=self.strip_ntfs)
        targetdir = tools.folderize(self.library, layout, create=create)
        targetname = tools.data_filler(self,
                                       self.rbfo.configurator.get_val(
                                           'layout-filename'),
                                       strip_ntfs=self.strip_ntfs)
        targetname += os.path.splitext(self.source_path())[1]
        return os.path.join(targetdir, targetname)

    def backup_path(self, destin):
        """ Free path under <library>/backup/ for a name already in use """
        folder = tools.folderize(self.library, BACKUP_FOLDER)
        return unique_path(os.path.join(folder, os.path.basename(destin)))

    def log_header(self):
        """ First line of a log entry: the track, then the time """
        stamp = time.strftime("%I:%M:%S %p", time.localtime())
        return tools.data_filler(self, '%ta - %at - ',
                                 strip_ntfs=self.strip_ntfs) + stamp

    def preview(self):
        """ Running in preview mode does not change files in any way """
        source = self.source_path()
        try:
            destin = self.target_path(create=False)
        except (tools.LibraryLocationError, OSError) as error:
            self.report(DAMAGED_LOG, POSSIBLE_DAMAGE + '\n' +
                        str(source) + '\n' + str(error) + '\n')
            return
        if source == destin:
            return
        self.report(PREVIEW_LOG, 'Change Found:\n' + source + '\n' +
                    destin + '\n')

    @staticmethod
    def report(name, text):
        """ Append a paragraph to one of the preview reports """
        with open(paths.user_file(name), 'a', encoding='utf-8') as report:
            report.write(text + '\n')

    # Moves the file to a specific location with a specific name
    def relocate(self):
        """ Performs the actual moving.
        -Move file to correct place
        -Update file location in RB database.

        The database is only ever pointed at a path a move has just
        produced. Updating it for a move that did not happen is what left
        entries showing as missing while the file sat where it started.
        """
        source = self.source_path()
        self.log.log_processing(self.log_header())
        self.log.log_processing(IN + str(source))
        try:
            destin = self.target_path()
        except (tools.LibraryLocationError, OSError) as error:
            self.log.log_processing(ERROR + str(error))
            self.log.log_processing('')
            return
        # Relocate, if necessary
        if source == destin:
            print(NO_NEED)
            self.log.log_processing(INFO + NO_NEED)
            self.log.log_processing('')
            return
        try:
            if os.path.exists(destin):
                # Send this file to the backup dir rather than overwrite
                destin = self.backup_path(destin)
                self.log.log_processing(CONFLICT + FILE_EXISTS)
            shutil.move(source, destin)
        except (OSError, shutil.Error) as error:
            # leave the entry alone; it still points at the file
            self.log.log_processing(ERROR + str(error))
            self.log.log_processing('')
            return
        self.log.log_processing(OUT + destin)
        # Update Rhythmbox database
        location = path_to_uri(destin)
        print('Relocating file \n%s to\n%s' % (source, destin))
        self.log.log_processing(INFO + UPDATING)
        self.log.log_processing(IN + self.location)
        self.log.log_processing(OUT + location)
        # Make the change
        self.rbdb.entry_set(self.entry,
                            RB.RhythmDBPropType.LOCATION,
                            location)
        # Non media clean up
        self.file_cleanup(source, destin)
        self.location = location
        self.log.log_processing('')

    # Non media clean up
    def file_cleanup(self, source, destin):
        """ Remove empty folders and move non-music files with selection """
        if not self.settings['cleanup-enabled']:
            return
        sourcedir = os.path.dirname(source)
        destindir = os.path.dirname(destin)
        if not os.path.isdir(sourcedir):
            return
        foundmedia = False
        for name in os.listdir(sourcedir):
            current = os.path.join(sourcedir, name)
            extension = os.path.splitext(name)[1].lower()
            if extension in RB_MEDIA_TYPES or os.path.isdir(current):
                foundmedia = True
            elif not destindir == sourcedir:
                target = os.path.join(destindir, name)
                try:
                    shutil.move(current, target)
                except (OSError, shutil.Error) as error:
                    self.log.log_processing(ERROR + 'Moving ' + name)
                    self.log.log_processing('    ' + str(error))
                else:
                    self.log.log_processing(INFO + 'Moved')
                    self.log.log_processing('    ' + target)
        if foundmedia:
            self.log.log_processing(INFO + STILL_MEDIA)
        if self.settings['cleanup-empty-folders']:
            self.remove_empty_folders(sourcedir)

    def remove_empty_folders(self, folder):
        """ Drop the emptied folder, then its parents while they are empty

        The walk stops below the library location. Without that guard an
        emptied library root is removed too and the walk carries on up
        towards the home folder.
        """
        if not self.library:
            return
        library = os.path.normpath(self.library)
        current = os.path.normpath(folder)
        while (current.startswith(library + os.sep) and
               os.path.isdir(current) and not os.listdir(current)):
            try:
                os.rmdir(current)
            except OSError as error:
                self.log.log_processing(ERROR + str(error))
                return
            self.log.log_processing(INFO + DIR_REMOVED)
            self.log.log_processing('    ' + current)
            current = os.path.dirname(current)
