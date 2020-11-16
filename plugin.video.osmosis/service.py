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
from kodi_six.utils import py2_decode
from json import dumps, loads
import os
from re import search
from time import ctime, mktime, strftime, strptime, time
import xbmc
import xbmcvfs

from resources.lib.common import Globals, Settings, sleep
from resources.lib.kodiDB import initDatabase, updateDatabase

globals = Globals()
settings = Settings()


def setDBs(files, path):
    dbtypes = ['video', 'music']

    for dbtype in dbtypes:
        dbname = None
        for file in files:
            if file.lower().startswith('my{0}'.format(dbtype)):
                if dbname is None:
                    dbname = file
                elif search('(\d+)', dbname) and search('(\d+)', file):
                    dbnumber = int(search('(\d+)', dbname).group(1))
                    filedbnumber = int(search('(\d+)', file).group(1))
                    if filedbnumber > dbnumber:
                        dbname = file

        if dbname is not None:
            dbpath = py2_decode(os.path.join(path, dbname))
            dbsetting = settings.DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH if dbtype == 'video' else settings.DATABASE_SQLLITE_KODI_MUSIC_FILENAME_AND_PATH
            if dbpath != dbsetting:
                globals.addon.setSetting('KMovie-DB path', dbpath) if dbtype == 'video' else globals.addon.setSetting('KMusic-DB path', dbpath)


def writeScheduledUpdate(now, next=None):
    if not next:
        next = now + (settings.SCHEDULED_UPDATE_INTERVAL * 60 * 60)
    next_json = dict(interval=settings.SCHEDULED_UPDATE_INTERVAL, time=ctime(next))

    file = xbmcvfs.File(settings.SCHEDULED_UPDATE_INTERVAL_FILENNAME_AND_PATH, 'w')
    file.write(bytearray(dumps(next_json), 'utf-8'))
    file.close()

    return next, next_json


def readFile(path):
    file = xbmcvfs.File(path, 'r')
    content = file.read()
    file.close()
    return content


def writeFile(path):
    file = xbmcvfs.File(path, 'w')
    file.write(bytearray(content, 'utf-8'))
    file.close()


if __name__ == '__main__':
    initDatabase()
    updateDatabase()

    if not settings.USE_MYSQL and settings.FIND_SQLLITE_DB:
        path = py2_decode(os.path.join(globals.HOME_PATH, 'userdata/Database/'))
        if xbmcvfs.exists(path):
            dirs, files = xbmcvfs.listdir(path)
            setDBs(files, path)

    if settings.UPDATE_AT_STARTUP:
        writeScheduledUpdate(time())
        xbmc.executebuiltin('RunPlugin(plugin://{0}/?url=&mode=666&updateActor=3)'.format(globals.PLUGIN_ID))

    monitor = globals.monitor
    while not monitor.abortRequested():
        if settings.SCHEDULED_UPDATE == 1:
            now = time()
            next = None
            next_json = None
            if not next_json:
                if not xbmcvfs.exists(settings.SCHEDULED_UPDATE_INTERVAL_FILENNAME_AND_PATH):
                    next, next_json = writeScheduledUpdate(now)
                else:
                    next_json = loads(readFile(settings.SCHEDULED_UPDATE_INTERVAL_FILENNAME_AND_PATH))
                    next = mktime(strptime(next_json.get('time')))

            if next_json.get('interval') != settings.SCHEDULED_UPDATE_INTERVAL:
                next = mktime(strptime(next_json.get('time'))) + ((settings.SCHEDULED_UPDATE_INTERVAL - next_json.get('interval')) * 60 * 60)
                next, next_json = writeScheduledUpdate(now, next)

            if (next <= now):
                next, next_json = writeScheduledUpdate(now)
                xbmc.executebuiltin('RunPlugin(plugin://{0}/?mode=666&updateActor=1)'.format(globals.PLUGIN_ID))
        if settings.SCHEDULED_UPDATE == 2 and strftime('%H:%M') == strftime('%H:%M', settings.SCHEDULED_UPDATE_TIME):
            xbmc.executebuiltin('RunPlugin(plugin://{0}/?mode=666&updateActor=2)'.format(globals.PLUGIN_ID))
            sleep(60)
        sleep(30)