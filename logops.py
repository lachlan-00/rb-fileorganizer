#!/usr/bin/env python3

""" Fileorganizer log operations

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


import os

import paths


MAX_SIZE = 1076072


class LogFile(object):
    """ Log file actions. Open, create and edit log files """

    def __init__(self, settings):
        self.settings = settings

    # Write to log file
    def log_processing(self, logmessage):
        """ Perform log operations """
        if not self.settings['log-enabled']:
            return
        log_filename = paths.user_file(self.settings['log-path'])
        try:
            # Create if missing, and start over once it gets too big
            if (not os.path.exists(log_filename) or
                    os.path.getsize(log_filename) >= MAX_SIZE):
                with open(log_filename, 'w', encoding='utf-8'):
                    pass
            with open(log_filename, 'a', encoding='utf-8') as logfile:
                logfile.write(logmessage + '\n')
        except OSError as error:
            print('fileorganizer: cannot write %s (%s)' % (log_filename,
                                                           error))
