#!/usr/bin/env python

""" Fileorganizer log operations

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


import os
import codecs
import ConfigParser


class LogFile():
    """ Log file actions. Open, create and edit log files """
    def __init__(self):
        self.conf = ConfigParser.RawConfigParser()
        conffile = (os.getenv('HOME') + '/.local/share/rhythmbox/' +
                         'plugins/fileorganizer/fo.conf')
        self.conf.read(conffile)

    # Write to log file
    def log_processing(self, logmessage):
        """ Perform log operations """
        log_enabled = self.conf.get('conf', 'log_enabled')
        log_filename = self.conf.get('conf', 'log_path')
        log_filename = os.getenv('HOME') + '/' + log_filename
        # Log if Enabled
        if log_enabled == 'True':
            # Create if missing
            if not os.path.exists(log_filename) or (
                os.path.getsize(log_filename) >= 1076072):
                files = codecs.open(log_filename, "w", "utf8")
                files.close()
            files = codecs.open(log_filename, "a", "utf8")
            try:
                logline = []
                logline.append(logmessage)
                files.write((u"".join(logline)) + u"\n")
            except UnicodeDecodeError:
                print 'LOG UNICODE ERROR'
                logline = []
                logline.append(logmessage.decode('utf-8'))
                files.write((u"".join(logline)) + u"\n")
            files.close()
