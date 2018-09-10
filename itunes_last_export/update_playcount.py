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

    def __init__(self, force_update=False, use_cache=False, status=None):
        self.username       = ""
        self.input_file     = ""
        self.server         = ""
        self.extract_file   = ""
        self.startpage      = 1
        self.force_update   = force_update
        self.use_cache      = use_cache
        self.status         = status

    def set_infos(self, username, server, extract_file):
        """
        Method called to set the class infos
        """
        self.username     = username
        self.server       = server
        self.extract_file = extract_file


    def run(self):
        """
        Main part of the class, called run as it was a thread
        """
        if self.status:
            self.status.progress_value.set(0)
            self.status.progress_bar.update()

        print("No input file given, extracting directly from {0} servers".format(self.server))
        lastexporter(self.server, self.username, self.startpage, self.extract_file,
                     tracktype='recenttracks', use_cache=self.use_cache, status=self.status)

        if self.status:
            self.status.progress_value.set(50)
            self.status.progress_bar.update()

        itunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")

        print("Reading extract file and updating database")
        matched, not_matched, already_ok = update_db(itunes, self.extract_file, self.force_update, updated_part="playcount", status=self.status)
        print("%d have been updated, %d had the correct playcount, no match was found for %d"
              %(len(matched), len(already_ok), len(not_matched)))

        if self.status:
            self.status.progress_value.set(100)
            self.status.progress_bar.update()


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
    PARSER.add_argument("-i", "--use-cache", dest="use_cache", default=False, action="store_true",
                        help="use the already extracted file as cache")
    PARSER.add_argument("-f", "--force-update", dest="force_update", default=False,
                        action="store_true",
                        help="force the update, do not use the current playcount in the library")

    ARGS = PARSER.parse_args()

    THREAD = UpdatePlaycount(force_update=ARGS.force_update, use_cache=ARGS.use_cache)
    THREAD.set_infos(ARGS.username, ARGS.server, ARGS.extract_file)
    THREAD.run()
