#!/usr/bin/env python3

""" FileOrganizer install script

    setuptools rather than distutils: distutils was removed in Python 3.12

    ----------------Authors----------------
    Lachlan de Waard <lachlan.00@gmail.com>
    ----------------Licence----------------
    Creative Commons - Attribution Share Alike v3.0

"""

from setuptools import setup
from setuptools.command.install import install
import os
import shutil
import subprocess
import sys
import sysconfig

import depends_test

PLUGIN_NAME = "fileorganizer"
FLATPAK_APP = "org.gnome.Rhythmbox3"
SCHEMA = "org.gnome.rhythmbox.plugins.fileorganizer.gschema.xml"

PLUGIN_FILES = [
    "fileorganizer.plugin",
    "fileorganizer.py",
    "configurator.py",
    "depends_test.py",
    "fileops.py",
    "logops.py",
    "paths.py",
    "tools.py",
    ]

PLUGIN_DATA = [
    "config.ui",
    "README.md",
    "LICENSE",
    "AUTHORS",
    ]

# optionally compile glib schemas
glib_compile_schemas = True

if "--no-glib-compile-schemas" in sys.argv:
    glib_compile_schemas = False
    sys.argv.remove("--no-glib-compile-schemas")

# install into a flatpak rhythmbox, or into the per-user plugin directory,
# instead of the system one
flatpak_app = None
user_plugin = False

for argument in list(sys.argv):
    if argument == "--flatpak":
        flatpak_app = FLATPAK_APP
        sys.argv.remove(argument)
    elif argument.startswith("--flatpak="):
        flatpak_app = argument.split("=", 1)[1]
        sys.argv.remove(argument)
    elif argument == "--user-plugin":
        user_plugin = True
        sys.argv.remove(argument)


class post_install(install):
    def run(self):
        # Call parent
        install.run(self)

        if glib_compile_schemas:
            # Execute commands after copying
            schema_dir = os.path.join(self.install_data, "share", "glib-2.0",
                                      "schemas")
            os.system("glib-compile-schemas %s" % schema_dir)


def lib_dir():
    """Directory holding rhythmbox's plugins, relative to the prefix.

    Debian and friends use a multiarch path, most rpm distributions use lib64
    and everything else uses lib, so prefer whichever one already holds a
    rhythmbox directory before falling back to the architecture guess.
    """
    candidates = []
    multiarch = sysconfig.get_config_var("MULTIARCH")
    if multiarch:
        candidates.append(os.path.join("lib", multiarch))
    if os.uname()[4].find("64") != -1 or os.uname()[4].find("s390x") != -1:
        candidates.append("lib64")
    candidates.append("lib")

    for prefix in (sys.prefix, "/usr"):
        for candidate in candidates:
            if os.path.isdir(os.path.join(prefix, candidate, "rhythmbox",
                                          "plugins")):
                return candidate

    return candidates[0]


def direct_install(plugin_dir, schema_dir, compile_commands):
    """Copy the plugin to an absolute location, outside any prefix.

    Both the per-user and the flatpak installs land in one directory that
    setuptools has no say over, so they bypass it entirely. Everything goes
    in the single plugin directory, which is where RB.find_user_data_file
    looks for the ui file.
    """
    for directory in (plugin_dir, schema_dir):
        os.makedirs(directory, exist_ok=True)

    for name in PLUGIN_FILES + PLUGIN_DATA:
        shutil.copy(name, plugin_dir)
        print("copying %s -> %s" % (name, plugin_dir))
    shutil.copy(SCHEMA, schema_dir)
    print("copying %s -> %s" % (SCHEMA, schema_dir))

    if not glib_compile_schemas:
        return

    for command in compile_commands:
        try:
            if subprocess.call(command + [schema_dir]) == 0:
                print("compiled schemas in %s" % schema_dir)
                return
        except OSError:
            continue

    print("WARNING: could not compile the schemas in %s" % schema_dir)


def user_install():
    """Install into the per-user rhythmbox plugin directory.

    Not setuptools' own --user: that resolves to ~/.local/lib/rhythmbox,
    which rhythmbox never looks in, so it would appear to work and do
    nothing.
    """
    data_dir = os.path.join(os.path.expanduser("~"), ".local", "share")
    direct_install(
        os.path.join(data_dir, "rhythmbox", "plugins", PLUGIN_NAME),
        os.path.join(data_dir, "glib-2.0", "schemas"),
        [["glib-compile-schemas"]])


def flatpak_install(app_id):
    """Install into a flatpak rhythmbox's own data directory.

    A flatpak cannot see the system or the user plugin directory: it has its
    own XDG_DATA_HOME under ~/.var/app. GLib does search that for schemas,
    so no GSETTINGS_SCHEMA_DIR is needed.
    """
    data_dir = os.path.join(
        os.path.expanduser("~"), ".var", "app", app_id, "data")
    if not os.path.isdir(os.path.dirname(data_dir)):
        sys.exit("%s has no data directory (%s).\n"
                 "Install the flatpak and run it once first, or pass "
                 "--flatpak=<app id>." % (app_id, os.path.dirname(data_dir)))

    # compile with the runtime's own glib where possible, the host's otherwise
    direct_install(
        os.path.join(data_dir, "rhythmbox", "plugins", PLUGIN_NAME),
        os.path.join(data_dir, "glib-2.0", "schemas"),
        [["flatpak", "run", "--command=glib-compile-schemas", app_id],
         ["glib-compile-schemas"]])


if flatpak_app or user_plugin:
    if "install" not in sys.argv:
        sys.exit("--flatpak and --user-plugin only apply to 'setup.py "
                 "install'")
    if not depends_test.check():
        sys.exit("please check your OS for missing packages")
    if flatpak_app:
        flatpak_install(flatpak_app)
    else:
        user_install()
    sys.exit(0)


setup(name=PLUGIN_NAME,
      cmdclass={"install": post_install},
      version="4.0.0",
      description="A Rhythmbox plugin to organize your music files",
      author="Lachlan de Waard",
      author_email="lachlan.00@gmail.com",
      url="https://github.com/lachlan-00/rb-fileorganizer",
      packages=[],
      data_files=[
          (os.path.join(lib_dir(), "rhythmbox/plugins", PLUGIN_NAME),
           PLUGIN_FILES),
          (os.path.join("share/rhythmbox/plugins", PLUGIN_NAME),
           PLUGIN_DATA),
          ("share/glib-2.0/schemas", [SCHEMA]),
          ],
      )
