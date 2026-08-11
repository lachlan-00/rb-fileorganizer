INSTALLPATH="$(HOME)/.local/share/rhythmbox/plugins/fileorganizer/"
SCHEMAPATH="$(HOME)/.local/share/glib-2.0/schemas"
FLATPAKAPP=org.gnome.Rhythmbox3
FLATPAKPATH="$(HOME)/.var/app/$(FLATPAKAPP)/data/rhythmbox/plugins/fileorganizer/"
FLATPAKSCHEMAS="$(HOME)/.var/app/$(FLATPAKAPP)/data/glib-2.0/schemas"
SCHEMA="org.gnome.rhythmbox.plugins.fileorganizer.gschema.xml"
INSTALLTEXT="The Fileorganizer plugin has been installed. You may now restart Rhythmbox and enable the 'Fileorganizer' plugin."
UNINSTALLTEXT="The Fileorganizer plugin had been removed. The next time you restart Rhythmbox it will dissappear from the plugins list."

install-req:
	# Copy the plugin and compile the settings schema
	python3 ./setup.py install --user-plugin

install: install-req
	@echo
	@echo $(INSTALLTEXT)

install-gui: install-req
	# Notify graphically
	zenity --info --title='Installation complete' --text=$(INSTALLTEXT)

install-flatpak:
	# Install into the flatpak rhythmbox's own data directory
	python3 ./setup.py install --flatpak=$(FLATPAKAPP)
	@echo
	@echo $(INSTALLTEXT)

uninstall-req:
	# Simply remove the installation path folder
	rm -rf $(INSTALLPATH)
	rm -f $(SCHEMAPATH)/$(SCHEMA)
	-glib-compile-schemas $(SCHEMAPATH)

uninstall: uninstall-req
	@echo
	@echo $(UNINSTALLTEXT)

uninstall-gui: uninstall-req
	# Notify graphically
	zenity --info --title='Uninstall complete' --text=$(UNINSTALLTEXT)

uninstall-flatpak:
	rm -rf $(FLATPAKPATH)
	rm -f $(FLATPAKSCHEMAS)/$(SCHEMA)
	-flatpak run --command=glib-compile-schemas $(FLATPAKAPP) $(FLATPAKSCHEMAS) || glib-compile-schemas $(FLATPAKSCHEMAS)
	@echo
	@echo $(UNINSTALLTEXT)
