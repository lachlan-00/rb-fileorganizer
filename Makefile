INSTALLPATH="$(HOME)/.local/share/rhythmbox/plugins/fileorganizer/"
INSTALLTEXT="The Fileorganizer plugin has been installed. You may now restart Rhythmbox and enable the 'Fileorganizer' plugin."
UNINSTALLTEXT="The Fileorganizer plugin had been removed. The next time you restart Rhythmbox it will dissappear from the plugins list."
PLUGINFILE="fileorganizer.plugin"

install-req:
	# Make environment
	mkdir -p $(INSTALLPATH)
	# Copy files, forcefully
	cp $(PLUGINFILE) $(INSTALLPATH) -f
	cp *.py $(INSTALLPATH) -f
	cp config.ui $(INSTALLPATH) -f
	cp fo.conf.template $(INSTALLPATH) -f
	cp README.md $(INSTALLPATH) -f
	cp LICENSE $(INSTALLPATH) -f
	cp AUTHORS $(INSTALLPATH) -f

install: install-req
	@echo
	@echo $(INSTALLTEXT)

install-gui: install-req
	# Notify graphically
	zenity --info --title='Installation complete' --text=$(INSTALLTEXT)

uninstall-req:
	# Simply remove the installation path folder
	rm -rf $(INSTALLPATH)

uninstall: uninstall-req
	@echo
	@echo $(UNINSTALLTEXT)

uninstall-gui: uninstall-req
	# Notify graphically
	zenity --info --title='Uninstall complete' --text=$(UNINSTALLTEXT)

