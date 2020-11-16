# Copyright (C) 2016 stereodruid(J.G.) Mail: stereodruid@gmail.com
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it.
# You can modify it for private use only.
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import PY2, py2_decode
from ast import literal_eval
import os
import sys
import time
import re
import xbmc
import xbmcplugin

from resources.lib.common import Globals, Settings, jsonrpc
from resources.lib.create import addMultipleSeasonToMediaList, addToMedialist, fillPlugins, \
    fillPluginItems, removeAndReadMedialistEntry, removeItemsFromMediaList, renameMediaListEntry, \
    searchAddons
from resources.lib.fileSys import writeTutList
from resources.lib.guiTools import addDir, getSources, mediaListDialog, selectDialog
from resources.lib.l10n import getString
from resources.lib.playback import play
from resources.lib.tvdb import removeShowsFromTVDBCache
from resources.lib.updateAll import strm_update
from resources.lib.utils import addon_log

try:
    from urllib.parse import parse_qsl
except:
    from urlparse import parse_qsl


def reassign(d):
    for k, v in d.items():
        try:
            evald = literal_eval(v)
            if isinstance(evald, dict):
                d[k] = evald
        except (ValueError, SyntaxError):
            pass


if __name__ == '__main__':
    globals = Globals()
    params = dict(parse_qsl(sys.argv[2][1:]))
    reassign(params)
    if PY2:
        sys.argv[0] = py2_decode(sys.argv[0])
        for k, v in params.items():
            params[k] = py2_decode(v)
    addon_log('params = {0}'.format(params))

    mode = int(params.get('mode')) if params.get('mode') else None

    if mode == None:
        getSources()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not writeTutList('select:PluginType'):
            tutWin = ['Adding content to your library',
                      'Welcome, this is your first time using OSMOSIS. Here, you can select the content type you want to add:\n'
                      +'Video Plugins: Select to add Movies, TV-Shows, YouTube Videos\n'
                      +'Music Plugins: Select to add Music']
            globals.dialog.ok(tutWin[0], tutWin[1])
    elif mode == 1:
        fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not writeTutList('select:Addon'):
            tutWin = ['Adding content to your library',
                      'Here, you can select the Add-on:\n'
                      +'The selected Add-on should provide Video/Music content in the right structure.\n'
                      +'Take a look at ++ Naming video files/TV shows ++ http://kodi.wiki/view/naming_video_files/TV_shows.']
            globals.dialog.ok(tutWin[0], tutWin[1])
    elif mode == 2:
        fillPluginItems(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 666:
        strm_update(actor=params.get('updateActor', 0))
    elif mode == 4:
        selectedItems = mediaListDialog(header_prefix=getString(39123, globals.addon))
        if selectedItems and len(selectedItems) > 0:
            strm_update(selectedItems)
    elif mode == 41:
        selectedItems = mediaListDialog(header_prefix=getString(39006, globals.addon), expand=False)
        if selectedItems and len(selectedItems) > 0:
            renameMediaListEntry(selectedItems)
    elif mode == 42:
        selectedItems = mediaListDialog(header_prefix=getString(39123, globals.addon))
        if selectedItems and len(selectedItems) > 0:
            removeAndReadMedialistEntry(selectedItems)
    elif mode == 5:
        removeItemsFromMediaList('list')
    elif mode == 51:
        selectedItems = mediaListDialog(True, False, header_prefix=getString(39008, globals.addon), cTypeFilter='TV-Shows')
        if selectedItems and len(selectedItems) > 0:
            removeShowsFromTVDBCache(selectedItems)
    elif mode == 52:
        removeShowsFromTVDBCache()
    elif mode == 6:
        xbmc.executebuiltin('InstallAddon(service.watchdog)')
        xbmc.executebuiltin('Container.Refresh')
    elif mode == 7:
        jsonrpc('Addons.SetAddonEnabled', dict(addonid='service.watchdog', enabled=True))
        xbmc.executebuiltin('Container.Refresh')
    elif mode == 10:
        play(sys.argv, params)
    elif mode == 100:
        fillPlugins(params.get('url'))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 101:
        fillPluginItems(params.get('url'), name_parent=params.get('name', ''))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        if not writeTutList('select:AddonNavi'):
            tutWin = ['Adding content to your library',
                      'Search for your Movie, TV-Show or Music.\n'
                      +'Mark/select content, do not play a Movie or enter a TV-Show.\n'
                      +'Open context menu on the selected and select *create strms*.']
            globals.dialog.ok(tutWin[0], tutWin[1])
    elif mode == 102:
        favs = jsonrpc('Favourites.GetFavourites', dict(properties=['path', 'window', 'windowparameter', 'thumbnail'])).get('favourites', {})
        if favs:
            for fav in favs:
                if params.get('type') == 'video' and fav.get('window') == 'videos':
                    addDir(fav.get('title'), fav.get('windowparameter'), 101, {'thumb': fav.get('thumbnail')}, type=type)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    elif mode == 103:
        addons = searchAddons(['video'])
        list = [addon.get('name') for addon in addons]
        ignore_addons = Settings().PLAYBACK_IGNORE_ADDON_STRING.split('|')
        preselects = [i for i, addon in enumerate(addons) if addon.get('addonid') in ignore_addons]
        selects = selectDialog(getString(33005, globals.addon), list, multiselect=True, preselect=preselects)
        playback_ignore_addon_string = '|'.join([addons[select].get('addonid') for select in selects]) if selects else ''
        globals.addon.setSetting('playback_ignore_addon_string', playback_ignore_addon_string)
    elif mode == 104:
        addons = searchAddons(['video', 'audio'])
        list = ['{0} ({1})'.format(addon.get('name'), addon.get('provides')) for addon in addons]
        infolabel_addons = Settings().INFOLABELS_ADD_ADDON_STRING.split('|')
        preselects = [i for i, addon in enumerate(addons) if addon.get('addonid') in infolabel_addons]
        selects = selectDialog(getString(33006, globals.addon), list, multiselect=True, preselect=preselects)
        infolabels_add_addon_string = '|'.join([addons[select].get('addonid') for select in selects]) if selects else ''
        globals.addon.setSetting('infolabels_add_addon_string', infolabels_add_addon_string)
    elif mode == 200:
        addon_log('write multi strms')
        addToMedialist(params)
    elif mode == 201:
        addon_log('write single strm')
        # fillPluginItems(url)
        # makeSTRM(name, name, url)
    elif mode == 202:
        addon_log('Add all season individually to MediaList')
        addMultipleSeasonToMediaList(params)
