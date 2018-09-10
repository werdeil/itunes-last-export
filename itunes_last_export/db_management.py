#!/usr/bin/env python
#-*- coding: utf-8 -*-

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

"""Module gathering all the functions for the management of the database"""

import codecs
import datetime

from server_management import parse_line

#########################################################################
#    Functions
#########################################################################

def backup_db(db_path):
    """Create a backup of the database file by copying it into clementine_backup.db file

    :param db_path: Path to the database
    :type db_path: string
    :return: None
    """
    print("Backing up database into {0}".format(db_path))
    raise NotImplementedError
    # shutil.copy(os.path.expanduser("%s/clementine.db" %db_path),
    #             os.path.expanduser("%s/clementine_backup.db" %db_path))

def update_db(itunes, extract, force_update=True, updated_part="None", status=None):
    """Update the ratings or the playcounts of a database according to an extract file

    :param itunes: Applescript itunes application
    :param extract: Path the extract file
    :param force_update: Option to update the database fields independently to their previous values
    :param updated_part: Either "playcount" or "rating", define the field to update in the database
    :return: 3 lists: updated tracks, not matched tracks and tracks that were already up to date
    """

    extract_file = codecs.open(extract, encoding='utf-8')
    biblio = {}
    matched = []
    not_matched = []
    already_ok = []

    if updated_part == "rating":
        raise NotImplementedError

    #Loop which will read the extract and store each play to a dictionary
    for line in extract_file.readlines():
        playing_time, title, artist = parse_line(line)
        titre = title.lower().encode('utf-8')
        artiste = artist.lower().encode('utf-8')
        if artiste in biblio:
            if titre in biblio[artiste]:
                biblio[artiste][titre]["playcount"] = biblio[artiste][titre]["playcount"] + 1
                biblio[artiste][titre]["time"] = max(biblio[artiste][titre]["time"], playing_time)
            else:
                biblio[artiste][titre]={}
                biblio[artiste][titre]["playcount"] = 1
                biblio[artiste][titre]["time"] = playing_time
        elif artiste is None or titre is None:
            pass
        else:
            biblio[artiste] = {}
            biblio[artiste][titre] = {}
            biblio[artiste][titre]["playcount"] = 1
            biblio[artiste][titre]["time"] = playing_time

    biblio = biblio_hooks(biblio)

    nbtracks = len(itunes.tracks())
    track_count = 0

    for track in itunes.tracks():
        if track.duration() > 30:
            artist = track.artist().lower().encode('utf-8')
            title  = track.name().lower().encode('utf-8')
            if artist in biblio:
                if title in biblio[artist]:
                    lastfm_playcount = biblio[artist][title]["playcount"]
                    current_playcount = track.playedCount()
                    if lastfm_playcount > current_playcount or (lastfm_playcount < current_playcount and force_update):
                        track.setPlayedCount_(lastfm_playcount)
                        track.setPlayedDate_(datetime.datetime.fromtimestamp(biblio[artist][title]["time"]))
                        print("Updating playcount for {0} from artist {1} to {2} (previous {3})".format(title, artist, lastfm_playcount, current_playcount))
                        matched.append("{0} {1}".format(artiste, title))
                    elif lastfm_playcount < current_playcount:
                        print("Playcount higher than on last.fm {0} (on itunes {1}) for {2}\t{3}\t{4}\t{5}\t{6}\tL\t{7}".format(lastfm_playcount, current_playcount, 
                            artist, track.album().lower().encode('utf-8'), title, track.trackNumber(), int(track.duration()), int(track.playedDate().timeIntervalSince1970())))
                    else:
                        already_ok.append("{0} {1}".format(artiste, title))
                else:
                    not_matched.append("{0} {1}".format(artiste, title))
                    print("No info found for title '{1}' and artist '{0}'".format(artist, title))
            else:
                not_matched.append("{0} {1}".format(artiste, title))
                print("No info found for artist '{0}' and title '{1}'".format(artist, title))

        else:
            pass
            # print("Track '{0}' from artist '{1}' is too short".format(title, artist))
        track_count +=1
        if status:
            status.progress_value.set(50+(50*track_count)/(nbtracks))
            status.progress_bar.update()
            text = "{0} - {1}".format(track.artist().encode('utf-8'), track.name().encode('utf-8'))
            status.status_text.set(text)
            status.status_bar.update()

    extract_file.close()

    return matched, not_matched, already_ok

def biblio_hooks(biblio):
    """
    Part to correct part of the scrobbled tracks for example some with a wrong artist or title
    This part is really specific to my library but can be adapted if needed
    """
    #Ugly Hack for -M-
    for titre in biblio["-m-"]:
        if titre in biblio["m"]:
            biblio["m"][titre]["playcount"] += biblio["-m-"][titre]["playcount"]
        else:
            biblio["m"][titre] = {}
            biblio["m"][titre]["playcount"] = biblio["-m-"][titre]["playcount"]
            biblio["m"][titre]["time"] = biblio["-m-"][titre]["time"]

    for titre in biblio["arthur h"]:
        if titre == "mystic rhumba":
            biblio["arthur h"]["mystic rumba"] = biblio["arthur h"][titre]
            break

    return biblio
