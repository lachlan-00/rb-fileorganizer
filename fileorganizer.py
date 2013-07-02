#!/usr/bin/env python3

""" Fileorganizer

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    Wolter Hellmund <wolterh6@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""


import ConfigParser
import os
import rb
import shutil

from gi.repository import GObject, Peas, PeasGtk, Gtk, Notify, Gio
from gi.repository import RB

import fileops

from configurator import FileorganizerConf


PLUGIN_PATH = 'plugins/fileorganizer/'
CONFIG_FILE = 'fo.conf'
c = "conf"


class Fileorganizer(GObject.Object, Peas.Activatable, PeasGtk.Configurable):
    __gtype_name = 'fileorganizer'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)
        self.configurator = FileorganizerConf()
        self.conf = ConfigParser.RawConfigParser()

    # Rhythmbox standard Activate method
    def do_activate(self):
        print("activating Fileorganizer")
        shell = self.object
        self.shell = shell
        self.db = shell.props.db
        self._check_configfile()
        self.menu_build(shell)

    # Rhythmbox standard Deactivate method
    def do_deactivate(self):
        print("deactivating Fileorganizer")
        Gio.Application.get_default().remove_plugin_menu_item('browser-popup', 'selection-organize')
        self.action_group = None
        self.action = None
        #self.source.delete_thyself()
        self.source = None

    # FUNCTIONS
    # check if configfile is present, if not copy from template folder
    def _check_configfile(self):
        self.configfile = RB.find_user_data_file(PLUGIN_PATH + CONFIG_FILE)
        if not os.path.isfile(self.configfile):
            template = rb.find_plugin_file(self, 'template/' + CONFIG_FILE)
            folder = os.path.split(self.configfile)[0]
            if not os.path.exists(folder):
                os.makedirs(folder)
            shutil.copyfile(template, self.configfile)
    
    # Build menu option
    def menu_build(self, shell):
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
        app.add_plugin_menu_item('browser-popup', "Organize Selection", item)
        app.add_action(action)

    # Create the Configure window in the rhythmbox plugins menu
    def do_create_configure_widget(self):
        self.ui_file = rb.find_plugin_file(self, 'config.ui')
        b = Gtk.Builder()
        b.add_from_file(self.ui_file)
        self._check_configfile()
        self.conf.read(self.configfile)
        window = b.get_object("fileorganizer")
        b.get_object("closebutton").connect('clicked', lambda x:
                                                  window.destroy())
        b.get_object("savebutton").connect('clicked', lambda x:
                                                 self.save_config(b))
        b.get_object("log_path").set_text(self.conf.get(c, "log_path"))
        b.get_object("cover_names").set_text(self.conf.get(c, "cover_names"))
        if self.conf.get(c, "log_enabled") == "True":
            b.get_object("logbutton").set_active(True)
        if self.conf.get(c, "cover_enabled") == "True":
            b.get_object("coverbutton").set_active(True)
        if self.conf.get(c, "cleanup_enabled") == "True":
            b.get_object("cleanupbutton").set_active(True)
        if self.conf.get(c, "cleanup_empty_folders") == "True":
            b.get_object("removebutton").set_active(True)
        if self.conf.get(c, "update_tags") == "True":
            b.get_object("tagsbutton").set_active(True)
        if self.conf.get(c, "preview_mode") == "True":
            b.get_object("previewbutton").set_active(True)
        window.show_all()
        return window

    def save_config(self, builder):
        if builder.get_object("logbutton").get_active():
            self.conf.set(c, "log_enabled", "True")
        else:
            self.conf.set(c, "log_enabled", "False")

        if builder.get_object("coverbutton").get_active():
            self.conf.set(c, "cover_enabled", "True")
        else:
            self.conf.set(c, "cover_enabled", "False")

        if builder.get_object("cleanupbutton").get_active():
            self.conf.set(c, "cleanup_enabled", "True")
        else:
            self.conf.set(c, "cleanup_enabled", "False")

        if builder.get_object("removebutton").get_active():
            self.conf.set(c, "cleanup_empty_folders", "True")
        else:
            self.conf.set(c, "cleanup_empty_folders", "False")
        if builder.get_object("tagsbutton").get_active():
            self.conf.set(c, "update_tags", "True")
        else:
            self.conf.set(c, "update_tags", "False")
        if builder.get_object("previewbutton").get_active():
            self.conf.set(c, "preview_mode", "True")
        else:
            self.conf.set(c, "preview_mode", "False")
        self.conf.set(c, "log_path",
                      builder.get_object("log_path").get_text())
        self.conf.set(c, "cover_names",
                      builder.get_object("cover_names").get_text())
        FILE = open(self.configfile, "w")
        self.conf.write(FILE)
        FILE.close()

    # Organize selection
    def organize_selection(self, action, shell):
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
        self.conf.read(self.configfile)
        # Run in Preview Mode
        if self.conf.get(c, "preview_mode") == "True":
            if filelist != []:
                prelist = os.getenv('HOME') + '/.fileorganizer-preview.log'
                FILE = open(prelist, "w")
                FILE.close()
                damlist = os.getenv('HOME') + '/.fileorganizer-damaged.log'
                FILE = open(damlist, "w")
                FILE.close()
                for item in filelist:
                    item = fileops.MusicFile(self, item)
                    item.preview()
                Notify.init('Fileorganizer')
                title = 'Fileorganizer'
                note = 'Preview Has Completed'
                notification = Notify.Notification.new(title, note, None)
                Notify.Notification.show(notification)
                # Show Results of preview
                self.results(prelist, damlist)
        else:
            # Run Normally
            self.organize(filelist)
            Notify.init('Fileorganizer')
            title = 'Fileorganizer'
            note = 'Your selection is organised'
            notification = Notify.Notification.new(title, note, None)
            Notify.Notification.show(notification)

    def results(self, prelist, damlist):
        if not os.stat(prelist)[6] == 0:
            os.system('/usr/bin/xdg-open ' + prelist)
        if not os.stat(damlist)[6] == 0:
            os.system('/usr/bin/xdg-open ' + damlist)

    # Organize array of files
    def organize(self, filelist):
        if filelist != []:
            for item in filelist:
                item = fileops.MusicFile(self, item)
                item.relocate()


class PythonSource(RB.Source):
    def __init__(self):
        RB.Source.__init__(self)
        GObject.type_register_dynamic(PythonSource)
