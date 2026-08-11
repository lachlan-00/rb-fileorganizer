Development Stop
================

Hi everyone, I took over this plugin many years ago and have since moved on to other methods of maintaining my library. If someone wants to fork it and take over i'm happy to let this go as i don't have the need for this plugin anymore.


RHYTHMBOX FILEORGANIZER
=======================

Welcome to version 4.0.0

This update fixes the bug that left files showing as 'missing' after a move,
moves the plugin settings into gsettings, and adds a Flatpak install.

It is a new major version because two of those are breaking changes: fo.conf
is gone (its contents are imported once and the file renamed), and install.py
and uninstall.py have been replaced by setup.py.

The 'missing files' report from 3.91 had two causes, both fixed:

 * When a file of the same name was already at the destination, the plugin
   sent the source to the backup folder. On the first collision for a given
   name it did not actually move anything, but still pointed the database at
   the backup path it had not created. The file stayed where it was and the
   entry went missing. The database is now only ever updated to a path a
   move has just produced.
 * Locations were percent-encoded by hand and then partly un-escaped again
   from a hardcoded list of eighteen characters. One of them turned every
   'è' in a path into a location Rhythmbox could not match. Paths now go
   through GFile, which is what Rhythmbox itself builds locations with.


1.0 Install
2.0 Usage & Main Features
2.1 Other Features
3.0 Configuration and customisation
3.1 Compilation Support
3.2 Plugin Preferences Window
4.0 Flatpak
5.0 Change History
6.0 Contribute
7.0 Links

1.0 INSTALL
-----------

For a per-user install (no root needed, the usual choice):

    python3 ./setup.py install --user-plugin

or the same thing through make:

    make install

That copies the plugin to

 * $HOME/.local/share/rhythmbox/plugins/fileorganizer/

puts the settings schema in $HOME/.local/share/glib-2.0/schemas/ and compiles
it. For a system-wide install instead:

    python3 ./setup.py install

To install without compiling the schemas, add --no-glib-compile-schemas to
any of the above. **The schema has to be compiled somewhere GLib looks or the
plugin will refuse to activate** - it prints a message saying so rather than
starting up without its settings.

To remove it again:

    make uninstall

You can test python dependencies by running:

    python3 -c "import depends_test; depends_test.check()"

Possible extra requirements are:

 * gir1.2-notify-0.7 (Debian name, GObject notify library)
 * dconf-editor (to make changes to the rhythmbox library settings)


2.0 USAGE & MAIN FEATURES
-------------------------

This plugin is pretty simple but it has a few complicated features under the hood.

Once the plugin is installed, simply enable it in Rhythmbox. A restart of rhythmbox will be required to detect the plugin if it was open when you installed.

When the plugin is enabled, you will notice an option in the right-click menu of music items (like songs) that will read 'Organize selection'. Clicking this will organize the selected files following a defined structure (see 3. Configuration and customisation) for both folders and filenames. That's all there is to it.


2.1 OTHER FEATURES

Intelligent duplicate backup:
 * When two songs have the same name, the plugin moves the file to a backup directory. 
 * If you lose a file, you'll probably in a folder named 'backup' in the root of your music library.

Move all non music files with your music:
 * When enabled, Fileorganizer will move files like text files and pictures with that music file.
 * This is great for keeping all files organised, not just music.


Log file for all actions:
 * The log file is an invaluable tool to see what happens when running fileorganizer. 
 * By default this file is hidden in your home folder: $HOME/.fileorganizer.log
 * Under Flatpak it goes to the application's own data folder instead; see 4.0.


3.0 CONFIGURATION AND CUSTOMISATION
-----------------------------------

The output when running 'Organize Selection' is set from dconf-editor using default Rhythmbox settings:
 * org.gnome.rhythmbox.library/layout-filename (Is the filename for your output)
 * org.gnome.rhythmbox.library/layout-path (Is the folder path for your output)
 * org.gnome.rhythmbox.rhythmdb/locations (Is your library path)

Using these, your final output becomes:
 * library + layout-path + layout-filename

The Locations setting can actually be multiple locations. The plugin uses the
one your file is already inside, and the first one otherwise.

The Variables for layout_path and layout_filename follow the same values as rhythmbox:
 * %at -- album title
 * %aa -- album artist (Album artist will use track artist if it does not exist)
 * %aA -- album artist (lowercase)
 * %as -- album artist sortname
 * %aS -- album artist sortname (lowercase)
 * %ay -- album release year
 * %an -- album disc number
 * %aN -- album disc number, zero padded
 * %ag -- album genre
 * %aG -- album genre (lowercase)
 * %tn -- track number (i.e 8)
 * %tN -- track number, zero padded (i.e 08)
 * %tt -- track title
 * %ta -- track artist
 * %tA -- track artist (lowercase)

Variables not ported yet:
 * %ts -- track artist sortname
 * %tS -- track artist sortname (lowercase)


3.1 COMPILATION SUPPORT

Fileorganizer will use the album artist tag which is a part of rhythmbox and replace the artist field. For example:
 * Path: /music/$artist/$year $album/$disc-$track - $title
 * Input: /music/new/spawn soundtrack/01 - filter & the crystal method - trip like i do.mp3
 * Set Album Artist to 'Various' in Rhythmbox.
 * Output: /music/Various/1997 Spawn/1-01 - Can't You (Trip Like I Do).mp3


3.2 PLUGIN PREFERENCES WINDOW

The preferences window gives you the ability to switch features on or off.
They are stored in gsettings under

   org.gnome.rhythmbox.plugins.fileorganizer

so dconf-editor can reach them too, and there is no longer a fo.conf file. An
fo.conf left over from an older version is imported the first time the plugin
starts and then renamed to fo.conf.migrated.

Preview Mode
 * If enabled, 'Organize Selection' will only check for changes and open a text report after completion.
 * Nothing is moved and no folders are created.

File/Folder Cleanup
 * If enabled, files within the same folder that aren't music files are moved as well

Remove Empty Folders
 * If the source folder is empty after moving, delete the folder
 * Empty parent folders go too, stopping below your library location.

Log File:
 * Set the filename of the log file (the base path is your home folder)
 * An absolute path is used as given.

Strip NTFS Chars
 * Strip out characters that Windows can't handle.
   (NTFS actually supports more characters than Windows allows)


4.0 FLATPAK
-----------

A Flatpak Rhythmbox cannot see the folders above; it has its own data
directory under ~/.var/app. Install into it with

    python3 ./setup.py install --flatpak

or

    make install-flatpak

which copies the plugin to

   ~/.var/app/org.gnome.Rhythmbox3/data/rhythmbox/plugins/fileorganizer/

and the schema to

   ~/.var/app/org.gnome.Rhythmbox3/data/glib-2.0/schemas/

then compiles it with the runtime's own glib-compile-schemas, falling back to
the host's. It needs no root. For a differently named flatpak, name it:

    python3 ./setup.py install --flatpak=org.gnome.Rhythmbox3.Devel

**The sandbox can only see the folders it has been given.** org.gnome.Rhythmbox3
ships with `--filesystem=xdg-music`, so out of the box the plugin can only
organize files under ~/Music. If your library lives anywhere else, Rhythmbox
cannot read it and neither can this plugin. Grant it with

    flatpak override --user --filesystem=/path/to/your/music org.gnome.Rhythmbox3

or tick the folder in Flatseal. Without that a move fails with a permission
error, which is written to the log rather than being allowed to update the
database.

The log and the preview reports do **not** go to your home folder under
Flatpak. $HOME inside the sandbox is an empty temporary filesystem that
accepts writes and throws them away when the app closes, so they would be
lost silently. They go to

   ~/.var/app/org.gnome.Rhythmbox3/data/rhythmbox/fileorganizer/

which you can still read from outside the sandbox. The preview report is
opened through the desktop portal.


5.0 CHANGE HISTORY
------------------

4.0.0
 * Fixed the database being updated for a move that did not happen, which is
   what left entries showing as missing.
 * Locations are built with GFile instead of by hand; the hardcoded escape
   list is gone.
 * Plugin settings moved from fo.conf to gsettings, with a one-time import.
 * Added a Flatpak install, and log/report paths that survive the sandbox.
 * Preview mode no longer creates the destination folders.
 * Empty folder cleanup stops at the library location instead of walking up
   past it.
 * A failed move is logged and skipped rather than raising.
 * The right-click item is now removed again when the plugin is disabled.
 * install.py and uninstall.py replaced by setup.py.

3.99*-dev-*
 * Removed tag update options and code
 * Removed cover art import, the naming/format has changed
 * Using urllib.parse to encode DB imports

3.*-dev-*
 * Added python script install.py to check all imports.
   (Also added uninstall.py)
 * Removed older v2.99 zip file
 * Removed INSTALL & UNINSTALL (these were just calls to make anyway)
 * Ongoing pylint/refactor changes.
 * Update config window to remove depreciated widgets. (requires GTK+ 3.0)
 * Move conf template into base plugin dir

Update 2015/05/05:
 * added strip_ntfs option (Care of @sirfz)
   [https://github.com/lachlan-00/rb-fileorganizer/commit/d8cf611f969a1fc250e7348b4e53285d13f950f3]

3.2013.09.16:
Currently running on RB 3.0
 * Tag Library python-eyed3 not available for python 3.

2.0.1-2 features include:
Preview Mode
 * Files are not moved or changed in any way while in preview mode.
 * When completed up to two text files will open showing changes or possibly damaged files.
 * To enable preview mode, set enable it in the preferences window.
Update Tags After Relocation
 * The plugin now uses python-eyeD3 for checking tag values.
 * After organising the selected files, fileorganizer will update the mp3 tags for you to 

2.0 features include:
 * GTK3 Rhythmbox 3/GIT support
 * Moved settings from Gconf to Gsettings
 * Random bug fixes
 * New code base [1]

1.1 features include:
 * UI Implemented
 * Configuration File
 * Import cover art from the source folder to the RB cache if found.
 * Ability to disable file/folder cleanup and other features.

1.0.3-2 features include:
 * Fixes to backup support.
 * UTF-8 encoding support.
 * Fixed move folder contents with files.
 * Notification on completion using pynotify.
 * More code cleanup and additions.

1.0.3 features include:
 * File management of non music files.
 * A physical log file stored in the home folder.
 * Moved the backup folder to the root of the music library.
 * Compilation support using rhythmbox's album artist field.

1.0.2 features include:
 * Support for Rhythmbox > 0.13.1
 * Added $disc and $year support.


6.0 CONTRIBUTE
--------------

To contribute, please refer to our github page [2]


7.0 LINKS
---------

[1] http://code.launchpad.net/~lachlan-00/rb-fileorganizer/legacy
[2] https://github.com/lachlan-00/rb-fileorganizer
