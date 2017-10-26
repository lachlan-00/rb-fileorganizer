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
import configparser
import gi
import urllib.parse

gi.require_version('RB', '3.0')

from gi.repository import RB

import tools

from logops import LogFile


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

IN = '    IN:    '
OUT = '    OUT:   '
INFO = ' ** INFO:  '
ERROR = ' ** ERROR: '
CONFLICT = ' ** CONFLICT: '
NO_NEED = 'No need for file relocation'
STILL_MEDIA = 'Directory still contains media; keeping:'
FILE_EXISTS = 'File exists, directing to backup folder'
POSSIBLE_DAMAGE = "Source file damaged or missing tag information.\n"
DIR_REMOVED = 'Removing empty directory'
UPDATING = 'Updating Database:'


class MusicFile(object):
    """ Class that performs all the file operations """

    def __init__(self, fileorganizer, db_entry=None, strip_ntfs=False):
        self.conf = configparser.RawConfigParser()
        conffile = (os.getenv('HOME') + '/.local/share/rhythmbox/' +
                    'plugins/fileorganizer/fo.conf')
        self.conf.read(conffile)
        self.rbfo = fileorganizer
        self.rbdb = self.rbfo.rbdb
        self.log = LogFile()
        # self.url = UrlData()
        self.strip_ntfs = strip_ntfs
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
            self.rbdb_rep = ('%28', '%29', '%2B', '%27', '%2C', '%3A', '%21',
                             '%24', '%26', '%2A', '%2C', '%2D', '%2E', '%3D',
                             '%40', '%5F', '%7E', '%C3%A8')
            self.rbdb_itm = ('(', ')', '+', "'", ',', ':', '!',
                             '$', '&', '*', ',', '-', '.', '=',
                             '@', '_', '~', 'è')

    def set_ascii(self, string):
        """ Change unicode codes back to ascii for RhythmDB
        RythmDB doesn't use a full URL for file path
        """
        count = 0
        while count < len(self.rbdb_rep):
            string = string.replace(self.rbdb_rep[count],
                                    self.rbdb_itm[count])
            count += 1

        return string

    # Returns metadata of the music file
    def get_metadata(self, key):
        """ Return metadata of current file """
        for datum in self.metadata:
            if key == datum:
                return self.metadata[datum]

    # Non media clean up
    def file_cleanup(self, source, destin):
        """ Remove empty folders and move non-music files with selection """
        cleanup_enabled = self.conf.get('conf', 'cleanup_enabled')
        remove_folders = self.conf.get('conf', 'cleanup_empty_folders')
        if cleanup_enabled == 'True':
            sourcedir = os.path.dirname(source)
            destindir = os.path.dirname(destin)
            foundmedia = False
            # Remove empty folders, if any
            if os.path.isdir(sourcedir):
                if not os.listdir(sourcedir) == []:
                    for files in os.listdir(sourcedir):
                        filelist = files[(files.rfind('.')):]
                        if filelist in RB_MEDIA_TYPES or os.path.isdir(
                                                sourcedir + '/' + files):
                            foundmedia = True
                        elif not destindir == sourcedir:
                            mvdest = destindir + '/' + os.path.basename(files)
                            mvsrc = sourcedir + '/' + os.path.basename(files)
                            try:
                                shutil.move(mvsrc, mvdest)
                            except FileNotFoundError:
                                self.log.log_processing(ERROR + 'Moving ' +
                                                        files)
                            except PermissionError:
                                self.log.log_processing(ERROR + 'Moving ' +
                                                        files)
                            except Exception as e:
                                self.log.log_processing(ERROR + 'Moving ' +
                                                        files)
                                print(e)
                            finally:
                                self.log.log_processing(INFO + 'Moved')
                                self.log.log_processing('    ' + mvdest)
                    if foundmedia:
                        self.log.log_processing(INFO + STILL_MEDIA)
                # remove empty folders after moving additional files
                if os.listdir(sourcedir) == [] and remove_folders == 'True':
                    currentdir = sourcedir
                    self.log.log_processing(INFO + DIR_REMOVED)
                    while not os.listdir(currentdir):
                        self.log.log_processing('    ' + currentdir)
                        os.rmdir(currentdir)
                        currentdir = os.path.split(currentdir)[0]

    # Get Source and Destination separately so preview can use the same code
    def get_locations(self, inputstring):
        """ Get file path for other file operations """
        # Get source for comparison
        source = self.location.replace('file:///', '/')
        if inputstring == 'source':
            return urllib.parse.unquote(source)
        # Set Destination Directory
        targetdir = '/' + self.rbfo.configurator.get_val('layout-path')
        targetdir = tools.data_filler(self, targetdir,
                                      strip_ntfs=self.strip_ntfs)
        targetloc = self.rbfo.configurator.get_val('locations')[0]
        targetpath = targetloc.replace('file:///', '/')
        targetdir = tools.folderize(targetpath, targetdir)
        # Set Destination  Filename
        targetname = self.rbfo.configurator.get_val('layout-filename')
        targetname = tools.data_filler(self, targetname,
                                       strip_ntfs=self.strip_ntfs)
        targetname += os.path.splitext(self.location)[1]
        # Join destination
        if inputstring == 'destin':
            return urllib.parse.unquote((os.path.join(targetdir, targetname)))
        return

    def preview(self):
        """ Running in preview mode does not change files in any way """
        print('preview')
        previewlist = os.getenv('HOME') + '/.fileorganizer-preview.log'
        damagedlist = os.getenv('HOME') + '/.fileorganizer-damaged.log'
        source = self.get_locations('source')
        destin = urllib.parse.unquote(self.get_locations('destin'))
        if not source == destin:
            # Write to preview list
            logfile = open(previewlist, "a")
            logfile.write("Change Found:\n" + source + "\n")
            logfile.write(destin + "\n\n")
            logfile.close()

    # Moves the file to a specific location with a specific name
    def relocate(self):
        """Performs the actual moving.
        -Move file to correct place
        -Update file location in RB database.
        """
        source = self.get_locations('source')
        destin = urllib.parse.unquote(self.get_locations('destin'))
        # Begin Log File
        tmptime = time.strftime("%I:%M:%S %p", time.localtime())
        logheader = '%ta - %at - '
        logheader = (tools.data_filler(self, logheader,
                                       strip_ntfs=self.strip_ntfs) + tmptime)
        # self.log = LogFile()
        self.log.log_processing(logheader)
        self.log.log_processing((IN + source))

        # Relocate, if necessary
        if source == destin:
            print('No need for file relocation')
            self.log.log_processing(INFO + NO_NEED)
        else:
            if os.path.isfile(destin):
                # Copy the existing file to a backup dir
                tmpdir = (self.rbfo.configurator.get_val('locations'))[0].replace('file:///', '/')
                tmpdir = urllib.parse.unquote(tmpdir)
                backupdir = tools.folderize(tmpdir, 'backup/')
                backup = os.path.join(backupdir, os.path.basename(destin))
                if os.path.isfile(backup):
                    counter = 0
                    backuptest = backup
                    while os.path.isfile(backup):
                        backup = backuptest
                        counter += 1
                        backup = (backup[:(backup.rfind('.'))] + str(counter) +
                                  backup[(backup.rfind('.')):])
                    try:
                        os.makedirs(os.path.dirname(backupdir))
                    except OSError:
                        pass
                    try:
                        shutil.move(source, backup)
                        self.log.log_processing(CONFLICT + FILE_EXISTS)
                        self.log.log_processing(OUT + backup)
                    except FileNotFoundError:
                        # we found a duplicate in the DB
                        pass
                destin = backup
            else:
                # Move the file to desired destination
                shutil.move(source, destin)
                self.log.log_processing(OUT + destin)

            # Update Rhythmbox database
            self.location = urllib.parse.quote(destin)
            self.location = ('file://' + self.location)
            self.location = self.set_ascii(self.location)
            print('Relocating file \n%s to\n%s' % (source, destin))
            self.log.log_processing(INFO + UPDATING)
            print(self.entry.get_string(RB.RhythmDBPropType.LOCATION))
            print(self.location)
            self.log.log_processing(IN + self.entry.get_string(RB.RhythmDBPropType.LOCATION))
            self.log.log_processing(OUT + self.location)
            # Make the change
            self.rbdb.entry_set(self.entry,
                                RB.RhythmDBPropType.LOCATION,
                                self.location)
            # Non media clean up
            self.file_cleanup(source, destin)
        self.log.log_processing('')
