#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

Module containing the GUI of the itunes_last_export tool

"""

from Tkinter import *
import ttk

import os
import os.path as osp

from ConfigParser import ConfigParser, NoSectionError

from update_playcount import UpdatePlaycount

class Interface(Frame):
    """
    Initialisation of the UI, called during the creation of an instance of the class, to create the main window and its elements
    """

    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.thread = None
        self.server = "last.fm"
        self.extract_file = osp.abspath(osp.expanduser("~/.config/itunes-last-export/extract_last_fm.txt"))
        self.config_path = osp.abspath(osp.expanduser("~/.config/itunes-last-export/itunes-last-export.cfg"))
        self.username = ''
        self.use_cache = False
        self.force_update = False
        self.load_config()
        self.status = Status()

        # Création de nos widgets
        self.message = Label(self, text="Please enter your last.fm username")
        self.message.grid(column=1, row=1, columnspan=3)

        self.username_label = Label(self, text="Username")
        self.username_label.grid(column=1, row=2)
        self.username_entry = Entry(self)
        self.username_entry.insert(0, self.username)
        self.username_entry.grid(column=2, row=2, columnspan=2)

        self.options_label = Label(self, text="Options")
        self.options_label.grid(column=1, row=3)
        self.use_cache_var = IntVar()
        self.use_cache_case = Checkbutton(self, text="Use cache file", variable=self.use_cache_var)
        if self.use_cache:
            self.use_cache_case.select()
        self.use_cache_case.grid(row=3, column=2, columnspan=2, sticky=W)
        self.force_update_var = IntVar()
        self.force_update_case = Checkbutton(self, text="Force the update", variable=self.force_update_var)
        if self.force_update:
            self.force_update_case.select()
        self.force_update_case.grid(row=4, column=2, columnspan=2, sticky=W)

        self.bouton_quitter = Button(self, text="Quit", command=self.quit)
        self.bouton_quitter.grid(row=5, column=1)

        self.bouton_cliquer = Button(self, text="Launch", command=self.cliquer)
        self.bouton_cliquer.grid(row=5, column=3)

        progress_bar = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate', variable=self.status.progress_value)
        self.status.init_progress_bar(progress_bar)
        self.status.progress_bar.grid(row=6, column=1, columnspan=3)

        status_bar = Label(fenetre, textvariable=self.status.status_text, bd=1, relief=SUNKEN, anchor=W, width=30)
        self.status.init_status_bar(status_bar)
        self.status.status_bar.pack(side=BOTTOM, fill=X)

        self.pack(fill=BOTH)

    def cliquer(self):
        """
        Function called when pressing the "Run" button on the UI
        """
        self.status.start()
        self.username = self.username_entry.get()
        self.use_cache = self.use_cache_var.get()
        self.force_update = self.force_update_var.get()
        print(self.username, self.force_update, self.use_cache)
        self.store_config()
        self.thread = UpdatePlaycount(force_update=self.force_update, use_cache=self.use_cache, status=self.status)
        self.thread.set_infos(self.username, self.server, self.extract_file)
        self.thread.run()
        self.status.finish()

    def load_config(self):
        """
        Loads the config store in the .config/itunes-last-export folder
        """
        self.parser = ConfigParser()
        self.parser.read(self.config_path)
        try:
            self.username = self.parser.get('Account','username')
            self.use_cache = self.parser.getboolean('Options','use_cache')
            self.force_update = self.parser.getboolean('Options','force_update')
        except NoSectionError:
            pass

    def store_config(self):
        """
        Store the config in the .config/itunes-last-export folder
        """
        if not osp.exists(osp.abspath(osp.expanduser("~/.config/itunes-last-export/"))):
            os.makedirs(osp.abspath(osp.expanduser("~/.config/itunes-last-export/")))
        if 'Account' not in self.parser.sections():
            self.parser.add_section('Account')
        self.parser.set('Account', 'username', self.username)
        if 'Options' not in self.parser.sections():
            self.parser.add_section("Options")
        self.parser.set('Options','use_cache', self.use_cache)
        self.parser.set('Options','force_update', self.force_update)


        # Writing our configuration file to 'example.ini'
        with open(self.config_path, 'wb') as configfile:
            self.parser.write(configfile)


class Status(object):
    """
    Class containing the status objects (progress bar and status bar)
    """

    def __init__(self):
        self.progress_bar   = None
        self.progress_value = IntVar()
        self.statusbar      = None
        self.status_text    = StringVar()


    def init_status_bar(self, status_bar):
        self.status_bar  = status_bar
        self.status_text.set("Idle")

    def init_progress_bar(self, progress_bar):
        self.progress_bar   = progress_bar

    def start(self):
        self.progress_value.set(0)
        self.status_text.set("Processing")

    def finish(self):
        self.status_text.set("Finished")




def main():
    """
    Gui function, to be called by the launcher
    """
    window = Tk()
    window.title("iTunes Last Export")
    interface = Interface(window)
    interface.pack_propagate(0)
    interface.mainloop()


if __name__ == '__main__':
    main()
