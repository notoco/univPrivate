#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This module gets called from the context menu item "Sync directory to library" (32001).
The purpose is to stage all movies/tvshows in the current directory, and update database
'''

import xbmc
import xbmcgui

import resources.lib.utils as utils
from resources.lib.menus.synced import SyncedMenu


@utils.entrypoint
def main():
    ''' Main entrypoint for context menu item '''
    container_type = xbmc.getInfoLabel('Container.Content')
    dir_path = xbmc.getInfoLabel('Container.FolderPath')
    dir_label = xbmc.getInfoLabel('Container.FolderName')
    # Get content type
    STR_CHOOSE_CONTENT_TYPE = utils.ADDON.getLocalizedString(32100)
    STR_MOVIE = utils.ADDON.getLocalizedString(32102)
    STR_TV_SHOW = utils.ADDON.getLocalizedString(32101)
    typeofcontent = xbmcgui.Dialog().select(STR_CHOOSE_CONTENT_TYPE, ['Sync All Items', 'Sync Only Movies', 'Sync Only Shows', '[COLOR red][B]Cancel[/B][/COLOR]'])

    # Call corresponding method
    if typeofcontent == 0:
        sync_type = 'all_items'
    elif typeofcontent == 1:
        sync_type = 'movies'
    elif typeofcontent == 2:
        sync_type = 'tvshow'
    elif typeofcontent == -1 or 3:
        xbmc.sleep(200)
        utils.notification('Type of content not selected, Try again.')

    try:
        SyncedMenu().sync_all_items_in_directory(sync_type, dir_label, dir_path)
    except Exception:
        pass


if __name__ == '__main__':
    main()
