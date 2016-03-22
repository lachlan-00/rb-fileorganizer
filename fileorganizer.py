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
#import rb
import shutil
import gi

gi.require_version('Peas', '1.0')
gi.require_version('PeasGtk', '1.0')
gi.require_version('Notify', '0.7')
gi.require_version('RB', '3.0')

from gi.repository import GObject, Peas, PeasGtk, Gtk, Notify, Gio
from gi.repository import RB

import fileops
import tools

from configurator import FileorganizerConf


PLUGIN_PATH = 'plugins/fileorganizer/'
CONFIGFILE = 'fo.conf'
CONFIGTEMPLATE = 'fo.conf.template'
UIFILE = 'config.ui'
C = "conf"


class Fileorganizer(GObject.Object, Peas.Activatable, PeasGtk.Configurable):
    """ Main class that loads fileorganizer into Rhythmbox """
    __gtype_name = 'fileorganizer'
    object = GObject.property(type=GObject.Object)
    _menu_names = ['browser-popup',
                  'playlist-popup']
    def __init__(self):
        GObject.Object.__init__(self)
        self.configurator = FileorganizerConf()
        self.conf = configparser.RawConfigParser()
        self.configfile = RB.find_user_data_file(PLUGIN_PATH + CONFIGFILE)
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
        self._check_configfile()
        self.menu_build(shell)

    # Rhythmbox standard Deactivate method
    def do_deactivate(self):
        """ Deactivate the plugin """
        print("deactivating Fileorganizer")
        app = Gio.Application.get_default()
        for menu_name in Fileorganizer._menu_names:
            app.remove_plugin_menu_item(menu_name, 'selection-' + 'organize')
        self.action_group = None
        self.action = None
        #self.source.delete_thyself()
        self.source = None

    # FUNCTIONS
    # check if configfile is present, if not copy from template folder
    def _check_configfile(self):
        """ Copy the default config template or load existing config file """
        if not os.path.isfile(self.configfile):
            template = RB.find_user_data_file(PLUGIN_PATH + CONFIGTEMPLATE)
            folder = os.path.split(self.configfile)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
            shutil.copyfile(template, self.configfile)

    # Build menu option
    def menu_build(self, shell):
        """ Add 'Organize Selection' to the Rhythmbox righ-click menu """
        app = Gio.Application.get_default()

        # create action
        action = Gio.SimpleAction(name="organize-selection")
        action.connect("activate", self.organize_selection)
        app.add_action(action)

        # create menu item
        item = Gio.MenuItem()
        item.set_label("Organize Selection")
        item.set_detailed_action("app.organize-selection")

        # add plugin menu item
        for menu_name in Fileorganizer._menu_names:
            app.add_plugin_menu_item(menu_name, "Organize Selection", item)
        app.add_action(action)

    # Create the Configure window in the rhythmbox plugins menu
    def do_create_configure_widget(self):
        """ Load the glade UI for the config window """
        build = Gtk.Builder()
        build.add_from_file(self.ui_file)
        self._check_configfile()
        self.conf.read(self.configfile)
        window = build.get_object("fileorganizer")
        build.get_object("closebutton").connect('clicked',
                                                lambda x:
                                                window.destroy())
        build.get_object("savebutton").connect('clicked', lambda x:
                                               self.save_config(build))
        build.get_object("log_path").set_text(self.conf.get(C, "log_path"))
        build.get_object("cover_names").set_text(self.conf.get(C,
                                                               "cover_names"))
        if self.conf.get(C, "log_enabled") == "True":
            build.get_object("logbutton").set_active(True)
        if self.conf.get(C, "cover_enabled") == "True":
            build.get_object("coverbutton").set_active(True)
        if self.conf.get(C, "cleanup_enabled") == "True":
            build.get_object("cleanupbutton").set_active(True)
        if self.conf.get(C, "cleanup_empty_folders") == "True":
            build.get_object("removebutton").set_active(True)
        if self.conf.get(C, "update_tags") == "True":
            build.get_object("tagsbutton").set_active(True)
        if self.conf.get(C, "preview_mode") == "True":
            build.get_object("previewbutton").set_active(True)
        if self.conf.get(C, "strip_ntfs") == "True":
            build.get_object("ntfsbutton").set_active(True)
        window.show_all()
        return window

    def save_config(self, builder):
        """ Save changes to the plugin config """
        if builder.get_object("logbutton").get_active():
            self.conf.set(C, "log_enabled", "True")
        else:
            self.conf.set(C, "log_enabled", "False")

        if builder.get_object("coverbutton").get_active():
            self.conf.set(C, "cover_enabled", "True")
        else:
            self.conf.set(C, "cover_enabled", "False")

        if builder.get_object("cleanupbutton").get_active():
            self.conf.set(C, "cleanup_enabled", "True")
        else:
            self.conf.set(C, "cleanup_enabled", "False")

        if builder.get_object("removebutton").get_active():
            self.conf.set(C, "cleanup_empty_folders", "True")
        else:
            self.conf.set(C, "cleanup_empty_folders", "False")
        if builder.get_object("tagsbutton").get_active():
            self.conf.set(C, "update_tags", "True")
        else:
            self.conf.set(C, "update_tags", "False")
        if builder.get_object("previewbutton").get_active():
            self.conf.set(C, "preview_mode", "True")
        else:
            self.conf.set(C, "preview_mode", "False")
        if builder.get_object("ntfsbutton").get_active():
            self.conf.set(C, "strip_ntfs", "True")
        else:
            self.conf.set(C, "strip_ntfs", "False")
        self.conf.set(C, "log_path",
                      builder.get_object("log_path").get_text())
        self.conf.set(C, "cover_names",
                      builder.get_object("cover_names").get_text())
        datafile = open(self.configfile, "w")
        self.conf.write(datafile)
        datafile.close()

    # Organize selection
    def organize_selection(self, action, shell):
        """ get your current selection and run process_selection """
        page = self.shell.props.selected_page
        if not hasattr(page, "get_entry_view"):
            return
        selected = page.get_entry_view()

        #source = shell.get_property("selected_page")
        #entry = RB.Source.get_entry_view(source)
        selection = selected.get_selected_entries()
        self.process_selection(selection)
        #self.organize(selection)

    # Process selection: Run in Preview Mode or Normal Mode
    def process_selection(self, filelist):
        """ using your selection, run the preview or process from fileops """
        self.conf.read(self.configfile)
        strip_ntfs = self.conf.get(C, "strip_ntfs") == "True"
        # Run in Preview Modelogops
        if self.conf.get(C, "preview_mode") == "True":
            if filelist != []:
                prelist = os.getenv('HOME') + '/.fileorganizer-preview.log'
                datafile = open(prelist, "w")
                datafile.close()
                damlist = os.getenv('HOME') + '/.fileorganizer-damaged.log'
                datafile = open(damlist, "w")
                datafile.close()
                for item in filelist:
                    item = fileops.MusicFile(self, item, strip_ntfs=strip_ntfs)
                    item.preview()
                Notify.init('Fileorganizer')
                title = 'Fileorganizer'
                note = 'Preview Has Completed'
                notification = Notify.Notification.new(title, note, None)
                Notify.Notification.show(notification)
                # Show Results of preview
                tools.results(prelist, damlist)
        else:
            # Run Normally
            self.organize(filelist, strip_ntfs)
            Notify.init('Fileorganizer')
            title = 'Fileorganizer'
            note = 'Your selection is organised'
            notification = Notify.Notification.new(title, note, None)
            Notify.Notification.show(notification)
        return


    # Organize array of files
    def organize(self, filelist, strip_ntfs=False):
        """ get fileops to move media files to the correct location """
        if filelist != []:
            for item in filelist:
                item = fileops.MusicFile(self, item, strip_ntfs=strip_ntfs)
                item.relocate()
        return


class PythonSource(RB.Source):
    """ Register with rhythmbox """
    def __init__(self):
        RB.Source.__init__(self)
        GObject.type_register_dynamic(PythonSource)
