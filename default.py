'''
Created on Sep 4, 2010
@author: Zsolt Török

Copyright (C) 2010 Zsolt Török
 
This file is part of XBMC SoundCloud Plugin.

XBMC SoundCloud Plugin is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

XBMC SoundCloud Plugin is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with XBMC SoundCloud Plugin.  If not, see <http://www.gnu.org/licenses/>.

'''
import sys
import xbmc, xbmcgui, xbmcplugin
import xbmcsc.client as client
import urllib
from xbmcsc.client import SoundCloudClient

# plugin related constants
PLUGIN_URL = 'plugin://music/SoundCloud/'

# XBMC plugin modes
MODE_GROUPS = 0
MODE_TRACKS = 1
MODE_ARTISTS = 2
MODE_TRACKS_MENU = 3
MODE_TRACKS_FAVORITES = 4
MODE_TRACKS_SEARCH = 5
MODE_TRACKS_HOTTEST = 6
MODE_GROUPS_MENU = 7
MODE_GROUPS_FAVORITES = 8
MODE_GROUPS_SEARCH = 9
MODE_GROUPS_HOTTEST = 10
MODE_GROUPS_TRACKS = 11
MODE_TRACK_PLAY = 12

# Parameter keys
PARAMETER_KEY_OFFSET = u'offset'
PARAMETER_KEY_LIMIT = u'limit'
PARAMETER_KEY_MODE = u'mode'
PARAMETER_KEY_URL = u'url'
PARAMETER_KEY_PERMALINK = u'permalink'

REMOTE_DBG = False
handle = int(sys.argv[1])
soundcloud_client = SoundCloudClient()

# append pydev remote debugger
def init_debugger():
    if REMOTE_DBG:
        # Make pydev debugger works for auto reload.
        # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
        try:
            import pysrc.pydevd as pydevd
        # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
            pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
        except ImportError:
            sys.stderr.write("Error: " +
                "You must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
            sys.exit(1)

# Actual XBMC code
def addDirectoryItem(name, label2='', infoType="Music", infoLabels={}, isFolder=True, parameters={}):
    liz = xbmcgui.ListItem(name, label2)
    if not infoLabels:
        infoLabels = {"Title": name }

    liz.setInfo(infoType, infoLabels)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=isFolder)

def show_tracks_menu():
    addDirectoryItem(name="Hottest", parameters={PARAMETER_KEY_URL: PLUGIN_URL + "tracks/hottest", PARAMETER_KEY_MODE: MODE_TRACKS_HOTTEST}, isFolder=True)
    addDirectoryItem(name="Search", parameters={PARAMETER_KEY_URL: PLUGIN_URL + "tracks/search", PARAMETER_KEY_MODE: MODE_TRACKS_SEARCH}, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_groups_menu():
    addDirectoryItem(name="Hottest", parameters={PARAMETER_KEY_URL: PLUGIN_URL + "groups/hottest", PARAMETER_KEY_MODE: MODE_GROUPS_HOTTEST}, isFolder=True)
    addDirectoryItem(name="Search", parameters={PARAMETER_KEY_URL: PLUGIN_URL + "groups/search", PARAMETER_KEY_MODE: MODE_GROUPS_SEARCH}, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_tracks(tracks, parameters={}):
    xbmcplugin.setContent(handle, "songs")
    for track in tracks:
        li = xbmcgui.ListItem(label=track[client.TRACK_TITLE], thumbnailImage=track[client.TRACK_ARTWORK_URL])
        li.setInfo("music", { "title": track[client.TRACK_TITLE], "genre": track.get(client.TRACK_GENRE, "") })
        li.setProperty("mimetype", 'audio/mpeg')
        li.setProperty("IsPlayable", "true")
        track_parameters = { PARAMETER_KEY_MODE: MODE_TRACK_PLAY, PARAMETER_KEY_URL: PLUGIN_URL + "tracks/" + track[client.TRACK_PERMALINK], "permalink": track[client.TRACK_PERMALINK] }
        url = sys.argv[0] + '?' + urllib.urlencode(track_parameters)
        ok = xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=False)
    if not len(tracks) < parameters[PARAMETER_KEY_LIMIT]:
        modified_parameters = parameters.copy()
        modified_parameters[PARAMETER_KEY_OFFSET] = str(int(parameters[PARAMETER_KEY_OFFSET]) + int(parameters[PARAMETER_KEY_LIMIT]))
        addDirectoryItem(name="More...", parameters=modified_parameters, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def play_track(id):
    track = soundcloud_client.get_track(id)
    li = xbmcgui.ListItem(label=track[client.TRACK_TITLE], thumbnailImage=track.get(client.TRACK_ARTWORK_URL, ""), path=track[client.TRACK_STREAM_URL])
    li.setInfo("music", { "title": track[client.TRACK_TITLE], "genre": track.get(client.TRACK_GENRE, "") })
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)

def show_artists():
    xbmcplugin.setContent(handle, "artists")
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def show_groups(groups, parameters):
    for group in groups:
        li = xbmcgui.ListItem(label=group.get(client.GROUP_NAME, ""), thumbnailImage=group.get(client.GROUP_ARTWORK_URL, ""))
        group_parameters = {PARAMETER_KEY_MODE: MODE_GROUPS_TRACKS, PARAMETER_KEY_URL: PLUGIN_URL + "groups/" + group[client.GROUP_PERMALINK], "group_id": group[client.GROUP_ID]}
        url = sys.argv[0] + '?' + urllib.urlencode(group_parameters)
        ok = xbmcplugin.addDirectoryItem(handle, url=url, listitem=li, isFolder=True)
    if not len(groups) < parameters[PARAMETER_KEY_LIMIT]:
        more_item_parameters = parameters.copy()
        more_item_parameters[PARAMETER_KEY_OFFSET] = str(int(parameters[PARAMETER_KEY_OFFSET]) + int(parameters[PARAMETER_KEY_LIMIT]))
        addDirectoryItem(name="More...", parameters=more_item_parameters, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

def _show_keyboard(default="", heading="", hidden=False):
    """ shows a keyboard and returns a value """
    keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        return unicode(keyboard.getText(), "utf-8")
    return default

def show_root_list():
    addDirectoryItem(name='Groups', parameters={ PARAMETER_KEY_URL: PLUGIN_URL + 'groups', PARAMETER_KEY_MODE: MODE_GROUPS}, isFolder=True)
    addDirectoryItem(name='Tracks', parameters={PARAMETER_KEY_URL: PLUGIN_URL + 'tracks', PARAMETER_KEY_MODE: MODE_TRACKS}, isFolder=True)
    addDirectoryItem(name='Artists', parameters={PARAMETER_KEY_URL: PLUGIN_URL + 'artists', PARAMETER_KEY_MODE: MODE_ARTISTS}, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

##################################################################

init_debugger()
params = parameters_string_to_dict(sys.argv[2])
url = urllib.unquote_plus(params.get(PARAMETER_KEY_URL, ""))
name = urllib.unquote_plus(params.get("name", ""))
mode = int(params.get(PARAMETER_KEY_MODE, "0"))
query = urllib.unquote_plus(params.get("q", ""))
print "##########################################################"
print("Mode: %s" % mode)
print("URL: %s" % url)
print("Name: %s" % name)
print "##########################################################"

if not sys.argv[ 2 ] or not url:
    # new start
    ok = show_root_list()
elif mode == MODE_GROUPS:
    ok = show_groups_menu()
elif mode == MODE_TRACKS:
    ok = show_tracks_menu()
elif mode == MODE_ARTISTS:
    ok = show_artists()
elif mode == MODE_TRACKS_SEARCH:
    if (not query):
        query = _show_keyboard()
    tracks = soundcloud_client.get_tracks(int(params.get(PARAMETER_KEY_OFFSET, "0")), int(params.get(PARAMETER_KEY_LIMIT, "50")), mode, url, query)
    ok = show_tracks(parameters={PARAMETER_KEY_OFFSET: int(params.get(PARAMETER_KEY_OFFSET, "0")), PARAMETER_KEY_LIMIT: int(params.get(PARAMETER_KEY_LIMIT, "50")), PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL:url, "q":query}, tracks=tracks)
elif mode == MODE_TRACKS_HOTTEST:
    tracks = soundcloud_client.get_tracks(int(params.get(PARAMETER_KEY_OFFSET, "0")), int(params.get(PARAMETER_KEY_LIMIT, "50")), mode, url)
    ok = show_tracks(parameters={PARAMETER_KEY_OFFSET: int(params.get(PARAMETER_KEY_OFFSET, "0")), PARAMETER_KEY_LIMIT: int(params.get(PARAMETER_KEY_LIMIT, "50")), PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL:url}, tracks=tracks)
elif mode == MODE_GROUPS_SEARCH:
    if (not query):
        query = _show_keyboard()
    groups = soundcloud_client.get_groups(int(params.get(PARAMETER_KEY_OFFSET, "0")), int(params.get(PARAMETER_KEY_LIMIT, "50")), mode, url, query)
    ok = show_groups(groups=groups, parameters={PARAMETER_KEY_OFFSET: int(params.get(PARAMETER_KEY_OFFSET, "0")), PARAMETER_KEY_LIMIT: int(params.get(PARAMETER_KEY_LIMIT, "50")), PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL:url, "q":query})
elif mode == MODE_GROUPS_HOTTEST:
    groups = soundcloud_client.get_groups(int(params.get(PARAMETER_KEY_OFFSET, "0")), int(params.get(PARAMETER_KEY_LIMIT, "50")), mode, url)
    ok = show_groups(parameters={PARAMETER_KEY_OFFSET: int(params.get(PARAMETER_KEY_OFFSET, "0")), PARAMETER_KEY_LIMIT: int(params.get(PARAMETER_KEY_LIMIT, "50")), PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL:url}, groups=groups)
elif mode == MODE_GROUPS_TRACKS:
    tracks = soundcloud_client.get_group_tracks(int(params.get(PARAMETER_KEY_OFFSET, "0")), int(params.get(PARAMETER_KEY_LIMIT, "50")), mode, url, int(params.get("group_id", "1")))
    ok = show_tracks(parameters={PARAMETER_KEY_OFFSET: int(params.get(PARAMETER_KEY_OFFSET, "0")), PARAMETER_KEY_LIMIT: int(params.get(PARAMETER_KEY_LIMIT, "50")), PARAMETER_KEY_MODE: mode, PARAMETER_KEY_URL: url}, tracks=tracks)
elif mode == MODE_TRACK_PLAY:
    play_track(params.get(PARAMETER_KEY_PERMALINK, "1"))