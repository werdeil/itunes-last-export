#!/usr/bin/python
# -*- coding: utf-8 -*-

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

"""Script which allows to update the playcount in the itunes database from a last.fm extract"""

import argparse

# from PyQt4 import QtCore

from Foundation import *
from ScriptingBridge import *

from server_management import lastexporter
from db_management import update_db

class UpdatePlaycount():
    """
    Class called to update the playcount, a class is used as it used to be a thread
    """

    def __init__(self, force_update=False, use_cache=False):
        self.username     = ""
        self.input_file   = ""
        self.server       = ""
        self.extract_file = ""
        self.startpage    = 1
        self.force_update = force_update
        self.use_cache    = use_cache

    def set_infos(self, username, input_file, server, extract_file):
        """
        Method called to set the class infos
        """
        self.username     = username
        self.input_file   = input_file
        self.server       = server
        self.extract_file = extract_file


    def run(self):
        """
        Main part of the class, called run as it was a thread
        """

        if not self.input_file:
            print("No input file given, extracting directly from {0} servers".format(self.server))
            lastexporter(self.server, self.username, self.startpage, self.extract_file,
                         tracktype='recenttracks', use_cache=self.use_cache)

        itunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")

        print("Reading extract file and updating database")
        matched, not_matched, already_ok = update_db(itunes, self.extract_file, self.force_update,
                                                     updated_part="playcount")
        print("%d have been updated, %d had the correct playcount, no match was found for %d"
              %(len(matched), len(already_ok), len(not_matched)))
        # self.partDone.emit(100)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.usage = """Usage: %prog <username> [options]
    
    Script which will extract data from the server and update itunes database
    <username> .......... Username used in the server
    """

    PARSER.add_argument("username")
    PARSER.add_argument("-e", "--extract-file", dest="extract_file", default="extract_last_fm.txt",
                        help="extract file name, default is extract_last_fm.txt")
    PARSER.add_argument("-s", "--server", dest="server", default="last.fm",
                        help="server to fetch track info from, default is last.fm")
    PARSER.add_argument("-b", "--backup", dest="backup", default=False, action="store_true",
                        help="backup db first")
    PARSER.add_argument("-i", "--input-file", dest="input_file", default=False, action="store_true",
                        help="use the already extracted file as input")
    PARSER.add_argument("-f", "--force-update", dest="force_update", default=False,
                        action="store_true",
                        help="force the update, do not use the current playcount in the library")

    ARGS = PARSER.parse_args()

    THREAD = UpdatePlaycount(force_update=ARGS.force_update, use_cache=True)
    THREAD.set_infos(ARGS.username, ARGS.input_file, ARGS.server, ARGS.extract_file)
    THREAD.run()
