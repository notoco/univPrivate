#!/usr/bin/python
# coding: utf-8

########################

import xbmc
import xbmcgui
import random
import os
import time

from resources.lib.utils import split
from resources.lib.helper import *
from resources.lib.image import *
from resources.lib.player_monitor import PlayerMonitor

########################

NOTIFICATION_METHOD = ['VideoLibrary.OnUpdate',
                       'VideoLibrary.OnScanFinished',
                       'VideoLibrary.OnCleanFinished',
                       'AudioLibrary.OnUpdate',
                       'AudioLibrary.OnScanFinished'
                       ]

########################

class Service(xbmc.Monitor):
    def __init__(self):
        self.player_monitor = False
        self.restart = False
        self.screensaver = False
        self.service_enabled = ADDON.getSettingBool('service')
        self.service_interval = xbmc.getInfoLabel('Skin.String(ServiceInterval)') or ADDON.getSetting('service_interval')
        self.service_interval = float(self.service_interval)

        self.widget_refresh = 0
        self.get_backgrounds = 200
        self.set_background = xbmc.getInfoLabel('Skin.String(BackgroundInterval)') or ADDON.getSetting('background_interval')
        self.set_background = int(self.set_background)

        self.blur_background = condition('Skin.HasSetting(BlurEnabled)')
        self.blur_radius = xbmc.getInfoLabel('Skin.String(BlurRadius)') or ADDON.getSetting('blur_radius')

        self.master_lock = None
        self.login_reload = False

        if self.service_enabled:
            self.start()
        else:
            self.keep_alive()

    def onNotification(self, sender, method, data):
        #log('Skin debug -----------------------------> Kodi_Monitor: sender %s - method: %s  - data: %s' % (sender, method, data))
        if ADDON_ID in sender and 'restart' in method:
            self.restart = True

        if method in NOTIFICATION_METHOD:
            sync_library_tags()

            if method.endswith('Finished'):
                reload_widgets(instant=True, reason=method)
            else:
                reload_widgets(reason=method)

    def onSettingsChanged(self):
        log('Service: Addon setting changed', force=True)
        self.restart = True

    def onScreensaverActivated(self):
        self.screensaver = True

    def onScreensaverDeactivated(self):
        self.screensaver = False

    def stop(self):
        if self.service_enabled:
            del self.player_monitor
            log('Service: Player monitor stopped', force=True)
            log('Service: Stopped', force=True)

        if self.restart:
            log('Service: Applying changes', force=True)
            xbmc.sleep(500) # Give Kodi time to set possible changed skin settings. Just to be sure to bypass race conditions on slower systems.
            DIALOG.notification(ADDON_ID, ADDON.getLocalizedString(32006))
            self.__init__()

    def keep_alive(self):
        log('Service: Disabled', force=True)

        while not self.abortRequested() and not self.restart:
            self.waitForAbort(5)

        self.stop()

    def start(self):
        log('Service: Started', force=True)

        self.player_monitor = PlayerMonitor()

        while not self.abortRequested() and not self.restart:

            ''' Only run timed tasks if screensaver is inactive to avoid keeping NAS/servers awake
            '''
            if not self.screensaver:

                ''' Grab fanarts
                '''
                if self.get_backgrounds >= 200:
                    log('Start new fanart grabber process')
                    movie_fanarts, tvshow_fanarts, artists_fanarts = self.grabfanart()
                    self.get_backgrounds = 0

                else:
                    self.get_backgrounds += self.service_interval

                ''' Set background properties
                '''
                if self.set_background >= 10:

                    if movie_fanarts or tvshow_fanarts or artists_fanarts:
                        winprop('EmbuaryBackground', random.choice(movie_fanarts + tvshow_fanarts + artists_fanarts))
                    if movie_fanarts or tvshow_fanarts:
                        winprop('EmbuaryBackgroundVideos', random.choice(movie_fanarts + tvshow_fanarts))
                    if movie_fanarts:
                        winprop('EmbuaryBackgroundMovies', random.choice(movie_fanarts))
                    if tvshow_fanarts:
                        winprop('EmbuaryBackgroundTVShows', random.choice(tvshow_fanarts))
                    if artists_fanarts:
                        winprop('EmbuaryBackgroundMusic', random.choice(artists_fanarts))

                    self.set_background = 0

                else:
                    self.set_background += self.service_interval

                ''' Blur backgrounds
                '''
                if self.blur_background:
                    ImageBlur(radius=self.blur_radius)

                ''' Refresh widgets
                '''
                if self.widget_refresh >= 600:
                    reload_widgets(instant=True)
                    self.widget_refresh = 0

                else:
                    self.widget_refresh += self.service_interval

            ''' Workaround for login screen bug
            '''
            if not self.login_reload:
                if condition('System.HasLoginScreen'):
                    log('System has login screen enabled. Reload the skin to load all strings correctly.')
                    execute('ReloadSkin()')
                    self.login_reload = True

            ''' Master lock reload logic for widgets
            '''
            if condition('System.HasLocks'):
                if self.master_lock is None:
                    self.master_lock = condition('System.IsMaster')
                    log('Master mode: %s' % self.master_lock)

                if self.master_lock == True and not condition('System.IsMaster'):
                    log('Left master mode. Reload skin.')
                    self.master_lock = False
                    execute('ReloadSkin()')

                elif self.master_lock == False and condition('System.IsMaster'):
                    log('Entered master mode. Reload skin.')
                    self.master_lock = True
                    execute('ReloadSkin()')

            elif self.master_lock is not None:
                self.master_lock = None

            self.waitForAbort(self.service_interval)

        self.stop()

    def grabfanart(self):
        movie_fanarts = list()
        tvshow_fanarts = list()
        artists_fanarts = list()

        ''' Movie fanarts
        '''
        try:
            movie_query = json_call('VideoLibrary.GetMovies',
                                properties=['art'],
                                sort={'method': 'random'}, limit=40
                                )

            for art in movie_query['result']['movies']:
                movie_fanart = art['art'].get('fanart')
                if movie_fanart:
                    movie_fanarts.append(movie_fanart)

        except Exception:
            pass

        ''' TV show fanarts
        '''
        try:
            tvshow_query = json_call('VideoLibrary.GetTVShows',
                                properties=['art'],
                                sort={'method': 'random'}, limit=40
                                )
            for art in tvshow_query['result']['tvshows']:
                tvshow_fanart = art['art'].get('fanart')
                if tvshow_fanart:
                    tvshow_fanarts.append(tvshow_fanart)

        except Exception:
            pass

        ''' Music fanarts
        '''
        try:
            artist_query = json_call('AudioLibrary.GetArtists',
                                properties=['fanart'],
                                sort={'method': 'random'}, limit=40
                                )
            for art in artist_query['result']['artists']:
                artist_fanart = art.get('fanart')
                if artist_fanart:
                    artists_fanarts.append(artist_fanart)

        except Exception:
            pass

        return movie_fanarts, tvshow_fanarts, artists_fanarts