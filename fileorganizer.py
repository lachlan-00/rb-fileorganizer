#!/usr/bin/env python3

""" Fileorganizer

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""

import configparser
import os
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Peas', '1.0')
gi.require_version('PeasGtk', '1.0')
gi.require_version('Notify', '0.7')
gi.require_version('RB', '3.0')

from gi.repository import GObject, Peas, PeasGtk, Gtk, Notify, Gio
from gi.repository import RB

import fileops
import paths
import tools

from configurator import FileorganizerConf
from logops import LogFile

PLUGIN_PATH = 'plugins/fileorganizer/'
CONFIGFILE = 'fo.conf'
UIFILE = 'config.ui'
SCHEMA_ID = 'org.gnome.rhythmbox.plugins.fileorganizer'
MENU_ITEM = 'organize-selection'
C = "conf"

# pre-4.0.0 fo.conf key -> gsettings key
MIGRATE = {'preview_mode': 'preview-mode',
           'cleanup_enabled': 'cleanup-enabled',
           'cleanup_empty_folders': 'cleanup-empty-folders',
           'strip_ntfs': 'strip-ntfs',
           'log_enabled': 'log-enabled',
           'log_path': 'log-path'}

SCHEMA_MISSING = ('fileorganizer: the settings schema %s is not installed.\n'
                  'Install it with setup.py and run glib-compile-schemas.'
                  % SCHEMA_ID)


class Fileorganizer(GObject.Object, Peas.Activatable, PeasGtk.Configurable):
    """ Main class that loads fileorganizer into Rhythmbox """
    __gtype_name = 'fileorganizer'
    object = GObject.property(type=GObject.Object)
    _menu_names = ['browser-popup',
                   'playlist-popup']

    def __init__(self, *args, **kwargs):
        GObject.Object.__init__(self)
        super(Fileorganizer, self).__init__(*args, **kwargs)
        self.configurator = FileorganizerConf()
        self.settings = None
        self.log = None
        self.ui_file = RB.find_user_data_file(PLUGIN_PATH + UIFILE)
        self.shell = None
        self.rbdb = None
        self.action_group = None
        self.action = None
        self.source = None
        self.plugin_info = "fileorganizer"

    # Rhythmbox standard Activate method
    def do_activate(self):
        """ Activate the plugin """
        print("activating Fileorganizer")
        shell = self.object
        self.shell = shell
        self.rbdb = shell.props.db
        if not self.load_settings():
            return
        self.log = LogFile(self.settings)
        self.menu_build(shell)

    # Rhythmbox standard Deactivate method
    def do_deactivate(self):
        """ Deactivate the plugin """
        print("deactivating Fileorganizer")
        app = Gio.Application.get_default()
        for menu_name in Fileorganizer._menu_names:
            app.remove_plugin_menu_item(menu_name, MENU_ITEM)
        app.remove_action(MENU_ITEM)
        self.action_group = None
        self.action = None
        self.log = None
        self.settings = None
        # self.source.delete_thyself()
        self.source = None

    # FUNCTIONS
    def load_settings(self):
        """ Open the plugin settings, once the schema is known to be there

        Gio.Settings aborts the whole process when the schema is missing,
        so an install that never compiled the schema would take Rhythmbox
        down with it. Look it up first and refuse to activate instead.
        """
        source = Gio.SettingsSchemaSource.get_default()
        if source is None or source.lookup(SCHEMA_ID, True) is None:
            print(SCHEMA_MISSING)
            return False
        self.settings = Gio.Settings.new(SCHEMA_ID)
        self.migrate_config()
        return True

    def migrate_config(self):
        """ Carry a pre-4.0.0 fo.conf over to gsettings, once

        The old file kept the booleans as the strings 'True' and 'False'.
        """
        configfile = RB.find_user_data_file(PLUGIN_PATH + CONFIGFILE)
        if not configfile or not os.path.isfile(configfile):
            return
        conf = configparser.RawConfigParser()
        try:
            conf.read(configfile)
            for old, new in MIGRATE.items():
                if not conf.has_option(C, old):
                    continue
                if new == 'log-path':
                    self.settings[new] = conf.get(C, old)
                else:
                    self.settings[new] = conf.get(C, old) == "True"
            os.rename(configfile, configfile + '.migrated')
        except (configparser.Error, OSError) as error:
            print('fileorganizer: could not migrate %s (%s)' % (configfile,
                                                                error))
            return
        print('fileorganizer: migrated %s to gsettings' % configfile)

    # Build menu option
    def menu_build(self, shell):
        """ Add 'Organize Selection' to the Rhythmbox righ-click menu """
        app = Gio.Application.get_default()

        # create action
        action = Gio.SimpleAction(name=MENU_ITEM)
        action.connect("activate", self.organize_selection)
        app.add_action(action)

        # create menu item
        item = Gio.MenuItem()
        item.set_label("Organize Selection")
        item.set_detailed_action("app." + MENU_ITEM)

        # add plugin menu item
        for menu_name in Fileorganizer._menu_names:
            app.add_plugin_menu_item(menu_name, MENU_ITEM, item)

    # Create the Configure window in the rhythmbox plugins menu
    def do_create_configure_widget(self):
        """ Load the glade UI for the config window

        The root object stays a plain GtkBox: modern Rhythmbox embeds this
        widget in its own preferences window.
        """
        build = Gtk.Builder()
        build.add_from_file(self.ui_file)
        window = build.get_object("fileorganizer")
        if self.settings is None and not self.load_settings():
            return window
        for key, name, prop in (('preview-mode', 'previewbutton', 'active'),
                                ('cleanup-enabled', 'cleanupbutton', 'active'),
                                ('cleanup-empty-folders', 'removebutton',
                                 'active'),
                                ('strip-ntfs', 'ntfsbutton', 'active'),
                                ('log-enabled', 'logbutton', 'active'),
                                ('log-path', 'log_path', 'text')):
            self.settings.bind(key, build.get_object(name), prop,
                               Gio.SettingsBindFlags.DEFAULT)
        return window

    # Organize selection
    def organize_selection(self, action, shell):
        """ get your current selection and run process_selection """
        page = self.shell.props.selected_page
        if not hasattr(page, "get_entry_view"):
            return
        selected = page.get_entry_view()
        selection = selected.get_selected_entries()
        self.process_selection(selection)

    # Process selection: Run in Preview Mode or Normal Mode
    def process_selection(self, filelist):
        """ using your selection, run the preview or process from fileops """
        if not filelist:
            return
        if self.settings['preview-mode']:
            self.preview(filelist)
            self.notify('Preview Has Completed')
        else:
            self.organize(filelist)
            self.notify('Your selection is organised')
        return

    # Preview array of files
    def preview(self, filelist):
        """ report what would move, without touching anything """
        prelist = paths.user_file(fileops.PREVIEW_LOG)
        damlist = paths.user_file(fileops.DAMAGED_LOG)
        for report in (prelist, damlist):
            with open(report, "w", encoding='utf-8'):
                pass
        for item in filelist:
            fileops.MusicFile(self, item).preview()
        # Show Results of preview
        tools.results(prelist, damlist)
        return

    # Organize array of files
    def organize(self, filelist):
        """ get fileops to move media files to the correct location """
        for item in filelist:
            fileops.MusicFile(self, item).relocate()
        return

    @staticmethod
    def notify(note):
        """ Tell the user the run has finished """
        Notify.init('Fileorganizer')
        notification = Notify.Notification.new('Fileorganizer', note, None)
        Notify.Notification.show(notification)


class PythonSource(RB.Source):
    """ Register with rhythmbox """

    def __init__(self):
        RB.Source.__init__(self)
        GObject.type_register_dynamic(PythonSource)
