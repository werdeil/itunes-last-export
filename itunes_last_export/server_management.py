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

"""Module for exporting tracks through audioscrobbler API."""

import time
import re
import os
import io
import requests

def connect_server(server, username, startpage, sleep_func=time.sleep, tracktype='recenttracks'):
    """Connect to server and get a XML page.

    :param server: Server on which the information will be extracted
    :param username: Username to use on the server
    :param startpage: Page of the server where to start the importation
    :param sleep_func: Function to be called to wait when the server is not responding
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks'
    :return: response from the request the server
    """
    if server == "libre.fm":
        baseurl = 'http://alpha.libre.fm/2.0/?'
        urlvars = dict(method='user.get%s' % tracktype,
                       api_key=('itunes_last_export').ljust(32, '-'),
                       user=username,
                       page=startpage,
                       limit=200,
                       format='json')

    elif server == "last.fm":
        baseurl = 'http://ws.audioscrobbler.com/2.0/?'
        urlvars = dict(method='user.get%s' % tracktype,
                       api_key='e38cc7822bd7476fe4083e36ee69748e',
                       user=username,
                       page=startpage,
                       limit=200,
                       format='json')
    else:
        if server[:7] != 'http://':
            server = 'http://%s' % server
        baseurl = server + '/2.0/?'
        urlvars = dict(method='user.get%s' % tracktype,
                       api_key=('itunes_last_export').ljust(32, '-'),
                       user=username,
                       page=startpage,
                       limit=200,
                       format='json')

    for interval in (1, 5, 10, 62):
        try:
            response = requests.get(baseurl, urlvars)
            break
        except Exception as e:
            last_exc = e
            print("Exception occurred, retrying in %d s: %s" % (interval, e))
            sleep_func(interval)
    else:
        print("Failed to open page %s" % urlvars['page'])
        raise last_exc

    return response.json()

def get_pageinfo(response, tracktype='recenttracks'):
    """Check how many pages of tracks the user have.

    :param response: json page given by the server
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks'
    :return: Number of total pages to import
    """
    totalpages = response[tracktype]['@attr']['totalPages']
    return int(totalpages)

def get_tracklist(response, tracktype='recenttracks'):
    """Read JSON page and get a list of tracks and their info.

    :param response: Response from a request to the server (JSON page of the server)
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks'
    :return: list of tracks in the page
    """
    tracklist = response[tracktype]['track']
    return tracklist

def parse_track(trackelement):
    """Extract info from every track entry and output to list.

    :param trackelement: json element representing a track
    :return: List containing the date, title, artist and albumname corresponding to the track
    """

    # if trackelement.find('artist').getchildren():
    #     #artist info is nested in loved/banned tracks xml
    #     artistname = trackelement['artist']['#text']
    # else:
    artistname = trackelement['artist']['#text']

    # if trackelement.find('album') is None:
    #     #no album info for loved/banned tracks
    #     albumname = ''
    albumname = trackelement['album']['#text']

    trackname = trackelement['name']
    date = trackelement['date']['uts']

    output = [date, trackname, artistname, albumname]

    for i, v in enumerate(output):
        if v is None:
            output[i] = ''

    return output

def write_tracks(tracks, outfileobj):
    """Write tracks to an open file

    :param tracks: list of tracks, containing the fields to be written
    :param outfileobj: File object in which the tracks will be written
    :return: None
    """
    for fields in tracks:
        outfileobj.write(unicode("\t".join(fields) + "\n"))

def get_tracks(server, username, startpage=1, sleep_func=time.sleep, tracktype='recenttracks', firsttrack=None):
    """Get tracks from a server

    :param server: Server on which the information will be extracted
    :param username: Username to use on the server
    :param startpage: Page of the server where to start the importation
    :param sleep_func: Function to be called to wait when the server is not responding
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks'
    :param firsttrack: track information corresponding the the last track imported in the previous import
    """
    page = startpage
    response = connect_server(server, username, page, sleep_func, tracktype)
    totalpages = get_pageinfo(response, tracktype)
    import_finished = False

    if startpage > totalpages:
        raise ValueError("First page ({0}) is higher than total pages ({1}).".format(startpage, totalpages))

    while page <= totalpages:
        #Skip connect if on first page, already have that one stored.
        if page > startpage:
            response =  connect_server(server, username, page, sleep_func, tracktype)

        tracklist = get_tracklist(response)
        tracks = []
        for trackelement in tracklist:
            if trackelement.has_key('@attr') and trackelement['@attr'][u'nowplaying']:
                # Do not export the currently playing track.
                pass
            else:
                track = parse_track(trackelement)

                if track == firsttrack:
                    import_finished = True
                    break
                else:
                    tracks.append(track)

        yield page, totalpages, tracks

        page += 1
        sleep_func(.1)

        if import_finished:
            break

def parse_line(ligne):
    """Read an extracted line and return the artist and song part

    :param ligne: Line from the server to parse
    :return: The title and the artist included in the line in a tuple
    """
    regexp = re.compile("""(.*?)\t(.*?)\t(.*?)\t.*""")
    if regexp.match(ligne):
        playing_date, title, artist = regexp.findall(ligne)[0]
    else:
        playing_date, title, artist = None, None, None
        print("The following line cannot be parsed: {0}".format(ligne[:-1]))
    return int(playing_date), title, artist

def lastexporter(server, username, startpage, outfile, tracktype='recenttracks', use_cache=False, status=None):
    """Function called to import the information from the server and store it in a dedicated file

    :param server: Server on which the information will be extracted
    :param username: Username to use on the server
    :param startpage: Page of the server where to start the importation
    :param outfile: Path to the file where the information will be stored
    :param tracktype: Type of information to download from the server, can be either 'recentracks' or 'lovedtracks'
    :param use_cache: Option to use the previously downloaded information
    :param thread_signal: Thread signal given from the GUI
    :return: None
    """
    track_regexp = re.compile("(.*?)\t(.*?)\t(.*?)\t(.*)")
    #read the already existing file (if it exists) and use_cache option
    if os.path.exists(outfile) and use_cache:
        print("{0} is already present, it will be used as reference to speed up the import".format(outfile))

        old_file = io.open(outfile, mode="r", encoding="utf-8")


        # old_file = open(outfile, "r")
        already_imported_lines = old_file.readlines()
        old_file.close()
        firstline = already_imported_lines[0]
        date, title, artist, album = track_regexp.findall(firstline)[0]
        firsttrack = [date , title, artist, album]
    else:
        firsttrack = None
        already_imported_lines = []

    trackdict = dict()
    page = startpage  # for case of exception
    totalpages = -1  # ditto
    n = 0
    try:
        for page, totalpages, tracks in get_tracks(server, username, startpage, tracktype=tracktype, firsttrack=firsttrack):
            print("Got page %s of %s..." % (page, totalpages))
            if status:
                status.progress_value.set(50*page/totalpages)
                status.progress_bar.update() #the import takes 50% of the progress bar
                status.status_text.set("Processing page %s of %s..." % (page, totalpages))
                status.status_bar.update()
            for track in tracks:
                if tracktype == 'recenttracks':
                    trackdict.setdefault(track[0], track)
                else:
                    #Can not use timestamp as key for loved/banned tracks as it's not unique
                    n += 1
                    trackdict.setdefault(n, track)


    except ValueError as exception:
        exit(exception)
    except Exception:
        raise
    finally:
        with io.open(outfile, mode='w', encoding="utf-8") as outfileobj:
            tracks = sorted(trackdict.values(), reverse=True)
            write_tracks(tracks, outfileobj)
            print("Wrote page {0}-{1} of {2} to file {3}".format(startpage, page, totalpages, outfile))

            for line in already_imported_lines:
                outfileobj.write(line)
            if already_imported_lines != []:
                print("Completed with already imported informations")
            outfileobj.close()
