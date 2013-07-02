#!/usr/bin/env python3
# coding: utf-8

""" Fileorganizer file operations

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


import os
import shutil
import urllib
import time
import ConfigParser
import mimetypes

from gi.repository import RB

import tools

from logops import LogFile
from dbops import UrlData

EYED3_SUPPORT = False
try:
    import eyeD3
    EYED3_SUPPORT = True
except ImportError:
    print('Please install python-eyed3 for tag support')
    EYED3_SUPPORT = False


RB_METATYPES = ('at', 'aa', 'aA', 'as', 'aS', 'ay', 'an', 'aN', 'ag', 'aG',
                'tn', 'tN', 'tt', 'ta', 'tA')
RB_COVER_CACHE = '/.cache/rhythmbox/covers/'
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
ART_MOVED = 'Cover art moved to cache folder'
DIR_REMOVED = 'Removing empty directory'
UPDATING = 'Updating Database:'


class MusicFile():
    """ Class that performs all the file operations """
    def __init__(self, fileorganizer, db_entry=None):
        self.conf = ConfigParser.RawConfigParser()
        conffile = (os.getenv('HOME') + '/.local/share/rhythmbox/' +
                         'plugins/fileorganizer/fo.conf')
        self.conf.read(conffile)
        self.rbfo = fileorganizer
        self.rbdb = self.rbfo.db
        self.log = LogFile()
        self.url = UrlData()
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

    # Returns metadata of the music file
    def get_metadata(self, key):
        """ Return metadata of current file """
        for datum in self.metadata:
            if key == datum:
                return self.metadata[datum]

    # Rhythmbox coverart
    def set_rb_coverart(self, source):
        """ Copies cover art from the file location to the RB cache """
        coverart_enabled = self.conf.get('conf', 'cover_enabled')
        coverart_names = self.conf.get('conf', 'cover_names')
        coverart_names = coverart_names.split(',')
        if coverart_enabled == 'True':
            if not os.path.isdir(os.getenv('HOME') + RB_COVER_CACHE):
                try:
                    os.makedirs(os.getenv('HOME') + RB_COVER_CACHE)
                except:
                    print('Create folder Failed')
            artfile = '%ta - %at'
            artfile = (tools.data_filler(self, artfile) + '.jpg')
            artfile = os.getenv('HOME') + RB_COVER_CACHE + artfile
            if not os.path.isfile(artfile):
                print('COVERART MISSING')
                for filenames in coverart_names:
                    test = os.path.dirname(source) + '/' + filenames
                    if os.path.isfile(test):
                        print('COPYING COVERART TO RB CACHE')
                        self.log.log_processing(INFO + ART_MOVED)
                        shutil.copyfile(test, artfile)

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
                            except:
                                self.log.log_processing(ERROR + 'Moving ' +
                                                        files)
                            finally:
                                self.log.log_processing(INFO + 'Moved')
                                self.log.log_processing('    ' + mvdest)
                    if foundmedia == True:
                        self.log.log_processing(INFO + STILL_MEDIA)
                # remove empty folders after moving additional files
                if os.listdir(sourcedir) == [] and remove_folders == 'True':
                    currentdir = sourcedir
                    self.log.log_processing(INFO + DIR_REMOVED)
                    while os.listdir(currentdir) == []:
                        self.log.log_processing('    ' + currentdir)
                        os.rmdir(currentdir)
                        currentdir = os.path.split(currentdir)[0]

    # Get Source and Destination seperately so preview can use the same code
    def get_locations(self, inputstring):
        """ Get file path for other file operations """
        # Get source for comparison
        source = urllib.url2pathname(self.location).replace('file:///', '/')
        if inputstring == 'source':
            return source
        # Set Destination Directory
        targetdir = '/' + self.rbfo.configurator.get_val('layout-path')
        targetdir = tools.data_filler(self, targetdir)
        targetdir = tools.folderize(self.rbfo.configurator, targetdir)
        # Set Destination  Filename
        targetname = self.rbfo.configurator.get_val('layout-filename')
        targetname = tools.data_filler(self, targetname)
        targetname += os.path.splitext(self.location)[1]
        # Join destination
        destin = (os.path.join(targetdir, targetname)).replace('file:///', '/')
        if inputstring == 'destin':
            return destin
        return

    #tag operations
    def update_tags(self, inputfile):
        """ Update file tags (if enabled) """
        update_tags = self.conf.get('conf', 'update_tags')
        if update_tags == 'True' and EYED3_SUPPORT:
            self.log.log_processing('           Updating File Tags')
            tags = eyeD3.Tag()
            if mimetypes.guess_type(inputfile)[0] == 'audio/mpeg':
                print('UPDATING TAGS')
                artist = (self.entry.get_string(RB.RhythmDBPropType.ARTIST)
                                ).decode('utf-8')
                albumartist = (self.entry.get_string(
                                    RB.RhythmDBPropType.ALBUM_ARTIST)
                                    ).decode('utf-8')
                album = (self.entry.get_string(RB.RhythmDBPropType.ALBUM)
                                ).decode('utf-8')
                title = (self.entry.get_string(RB.RhythmDBPropType.TITLE)
                                ).decode('utf-8')
                genre = (self.entry.get_string(RB.RhythmDBPropType.GENRE))
                tags.link(inputfile)
                tags.setVersion(eyeD3.ID3_V2_4)
                tags.setTextEncoding(eyeD3.UTF_8_ENCODING)
                tags.setArtist(artist)
                tags.setArtist(albumartist, 'TPE2')
                tags.setTrackNum([str(self.entry.get_ulong(
                                    RB.RhythmDBPropType.TRACK_NUMBER)), None])
                tags.setDiscNum([str(self.entry.get_ulong(
                                    RB.RhythmDBPropType.DISC_NUMBER)), None])
                #tags.setDate(str(self.entry.get_ulong(
                #                    RB.RhythmDBPropType.YEAR)), 0)
                # Ryan Koesters caught my typo. Cheers!
                tags.setTextFrame('TDRC', str(self.entry.get_ulong(
                                              RB.RhythmDBPropType.YEAR)))
                tags.setTextFrame('TDRL', str(self.entry.get_ulong(
                                              RB.RhythmDBPropType.YEAR)))
                tags.setAlbum(album)
                tags.setTitle(title)
                tags.setGenre(genre)
                tags.update(eyeD3.ID3_V2_4)
        return

    def check_bad_file(self, inputfile):
        """ Check the input file for missing tags. (MP3 files only) """
        # Only check MP3's
        if not mimetypes.guess_type(inputfile)[0] == 'audio/mpeg':
            return True
        tags = eyeD3.Tag()
        tags.link(inputfile)
        #fail on important tags
        if (tags.getArtist() == '' or tags.getTitle() == ''
                or tags.getAlbum() == ''):
            return False
        if str(tags.getYear()) == 'None':
            try:
                if tags.getDate(0)[0].text == '':
                    return False
            except TypeError:
                return False
        return True

    def preview(self):
        """ Running in preview mode does not chage files in any way """
        print('preview')
        previewlist = os.getenv('HOME') + '/.fileorganizer-preview.log'
        damagedlist = os.getenv('HOME') + '/.fileorganizer-damaged.log'
        source = self.get_locations('source')
        destin = self.get_locations('destin')
        if not self.check_bad_file(source):
            logfile = open(damagedlist, "a")
            logfile.write(POSSIBLE_DAMAGE + source + "\n")
            logfile.write("File Size:  " + str(os.stat(source)[6] / 1024)
                            + "kb\n\n")
        elif not source == destin:
            # Write to preview list
            logfile = open(previewlist, "a")
            logfile.write("Change Found:\n" + source + "\n")
            logfile.write(destin + "\n\n")
            logfile.close()

    # Moves the file to a specific location with a specific name
    def relocate(self):
        """Performs the actual moving.
        -Move file to correct place and cover art to RB cache (if enabled)
        -Update file location in RB database. Update tags (if enabled)
        """
        source = self.get_locations('source')
        destin = self.get_locations('destin')
        # Begin Log File
        currenttime = time.strftime("%I:%M:%S %p", time.localtime())
        logheader = '%ta - %at - '
        logheader = (tools.data_filler(self, logheader) + currenttime)
        #self.log = LogFile()
        self.log.log_processing(logheader)
        self.log.log_processing((IN + source))
        # Save cover art if found into Rhythmbox cover cache
        self.set_rb_coverart(source)

        # Relocate, if necessary
        if source == destin:
            print('No need for file relocation')
            self.log.log_processing(INFO + NO_NEED)
        else:
            if os.path.isfile(destin):
                # Copy the existing file to a backup dir
                backupdir = (((self.rbfo.configurator.get_val('locations'))[0]
                               + '/backup/').replace('file:///', '/'))
                backup = os.path.join(backupdir, os.path.basename(destin))
                if os.path.isfile(backup):
                    counter = 0
                    backuptest = backup
                    while os.path.isfile(backup):
                        backup = backuptest
                        counter = counter + 1
                        backup = (backup[:(backup.rfind('.'))] + str(counter)
                                  + backup[(backup.rfind('.')):])
                try:
                    os.makedirs(os.path.dirname(backupdir))
                except OSError:
                    pass
                destin = backup
                self.log.log_processing(CONFLICT + FILE_EXISTS)
            print('source   ' + source)
            print('destin   ' + destin)
            try:
                mvsource = source.decode('utf-8')
                mvdestin = destin.decode('utf-8')
            except TypeError:
                print('TYPEERROR')
                mvsource = source
                mvdestin = destin
            shutil.move(mvsource, mvdestin)
            self.log.log_processing(OUT + mvdestin)

            # Update Rhythmbox database
            #self.url = UrlData()
            self.location = self.url.set_ascii(urllib.pathname2url(destin))
            self.location = ('file://' + self.location)
            print('Relocating file %s to %s' % (source, destin))
            self.log.log_processing(INFO + UPDATING)
            print(self.entry.get_string(RB.RhythmDBPropType.LOCATION))
            print(self.location)
            # Make the change
            self.rbdb.entry_set(self.entry,
                              RB.RhythmDBPropType.LOCATION, self.location)
            self.log.log_processing(OUT + self.location)
            self.update_tags(mvdestin)
            # Non media clean up
            self.file_cleanup(mvsource, mvdestin)
        self.log.log_processing('')

