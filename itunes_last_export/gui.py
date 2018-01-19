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

from update_playcount import UpdatePlaycount

class Interface(Frame):
    """
    Initialisation of the UI, called during the creation of an instance of the class, to create the main window and its elements
    """

    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.thread = None
        self.username = ""
        self.server = "last.fm"
        self.extract_file = "extract_last_fm.txt"
        self.use_cache = False
        self.force_update = False
        self.progress_value = IntVar()

        # Création de nos widgets
        self.message = Label(self, text="Please enter your last.fm username")
        self.message.grid(column=1, row=1, columnspan=2)

        self.username_label = Label(self, text="Username")
        self.username_label.grid(column=1, row=2)
        self.username_entry = Entry(self)
        self.username_entry.grid(column=2, row=2)

        self.use_cache_var = IntVar()
        self.use_cache_case = Checkbutton(self, text="Use cache file", variable=self.use_cache_var)
        self.use_cache_case.grid(row=3, column=1, columnspan=2)
        self.force_update_var = IntVar()
        self.force_update_case = Checkbutton(self, text="Force the update", variable=self.force_update_var)
        self.force_update_case.grid(row=4, column=1, columnspan=2)

        self.bouton_quitter = Button(self, text="Quit", command=self.quit)
        self.bouton_quitter.grid(row=5, column=1)

        self.bouton_cliquer = Button(self, text="Launch", command=self.cliquer)
        self.bouton_cliquer.grid(row=5, column=2)

        self.progressbar = ttk.Progressbar(self, orient=HORIZONTAL, length=300, mode='determinate', variable=self.progress_value)
        self.progressbar.grid(row=6, column=1, columnspan=2)

        self.pack(fill=BOTH)


    def cliquer(self):
        """
        Function called when pressing the "Run" button on the UI
        """
        self.progress_value.set(0)
        self.username = self.username_entry.get()
        self.use_cache = self.use_cache_var.get()
        self.force_update = self.force_update_var.get()
        print(self.username, self.force_update, self.use_cache)
        self.thread = UpdatePlaycount(force_update=self.force_update, use_cache=self.use_cache, progress_bar=self.progressbar, progress_value=self.progress_value)
        self.thread.set_infos(self.username, self.server, self.extract_file)
        self.thread.run()


if __name__ == '__main__':
    WINDOW = Tk()
    WINDOW.title("iTunes Last Export")
    INTERFACE = Interface(WINDOW)

    INTERFACE.mainloop()
