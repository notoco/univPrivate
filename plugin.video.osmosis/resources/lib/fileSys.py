# Copyright (C) 2016 stereodruid(J.G.)
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
from kodi_six.utils import py2_encode, py2_decode
import fileinput
import os
import re
import shutil
import codecs
import errno
import xbmc
import xbmcgui
import xbmcvfs

from .common import Globals, Settings, jsonrpc
from .kodiDB import delStream
from .l10n import getString
from .stringUtils import cleanByDictReplacements, cleanStrmFilesys, completePath, \
    getMovieStrmPath, getProviderId, getStrmname, multiRstrip, parseMediaListURL, replaceStringElem
from .utils import addon_log, addon_log_notice

globals = Globals()
settings = Settings()


def writeSTRM(path, file, url):
    addon_log('writeSTRM')
    return makeSTRM(path, file, url)


def makeSTRM(filepath, filename, url):
    addon_log('makeSTRM')
    name_orig, plugin_url = parseMediaListURL(url)

    mtime = None

    filepath = multiRstrip(filepath)
    filepath = completePath(os.path.join(settings.STRM_LOC, filepath))

    if not xbmcvfs.exists(filepath):
        dirs = filepath.replace(settings.STRM_LOC, '').split('\\') if filepath.find('\\') != -1 else filepath.replace(settings.STRM_LOC, '').split('/')
        dirs = filter(None, dirs)

        filepath = settings.STRM_LOC
        for dir in dirs:
            filepath = completePath(os.path.join(filepath, dir))
            if not xbmcvfs.exists(filepath):
                xbmcvfs.mkdir(filepath)

    if not settings.STRM_LOC.startswith('smb:') and not settings.STRM_LOC.startswith('nfs:'):
        fullpath = '{0}.strm'.format(py2_decode(os.path.normpath(xbmc.translatePath(os.path.join(filepath, filename)))))
    else:
        fullpath = '{0}{1}.strm'.format(filepath, filename)
#        if xbmcvfs.exists(fullpath):
#            if settings.CLEAR_STRMS == 'true':
#                x = 0 #xbmcvfs.delete(fullpath)
#            else:
#                return fullpath

#    if fullpath.find('Audio') > 0:
#        try:
#            if xbmcvfs.exists(fullpath):
#                return fullpath, None
#        except:
#            if xbmcvfs.exists(fullpath):
#                return fullpath, None

    try:
        fullpath = fullpath
        fle = xbmcvfs.File(fullpath, 'w')
    except:
        fullpath = fullpath
        fle = xbmcvfs.File(fullpath, 'w')

    fle.write(bytearray(url, 'utf-8'))
    fle.close()
    del fle

    try:
        if fullpath.find('Audio') > 0:
            mtime = xbmcvfs.Stat(fullpath).st_mtime()
    except OSError:
        pass

    return fullpath, mtime


def isInMediaList(mediaTitle, url, cType='Other'):
    addon_log('isInMediaList')
    existInList = False

    if not xbmcvfs.exists(globals.DATA_PATH):
        xbmcvfs.mkdirs(globals.DATA_PATH)
    if not xbmcvfs.exists(settings.MEDIALIST_FILENNAME_AND_PATH):
        xbmcvfs.File(settings.MEDIALIST_FILENNAME_AND_PATH, 'a').close()

    thelist = readMediaList()
    if len(thelist) > 0:
        for i in thelist:
            splits = i.strip().split('|')
            if getStrmname(splits[1]) == getStrmname(mediaTitle):
                splitPlugin = re.search('plugin:\/\/([^\/\?]*)', splits[2])
                mediaPlugin = re.search('plugin:\/\/([^\/\?]*)', url)
                if mediaPlugin and splitPlugin and mediaPlugin.group(1) == splitPlugin.group(1):
                    existInList = True

    if existInList:
        return True
    else:
        return False


def writeMediaList(url, name, cType='Other', cleanName=True, albumartist=None):
    addon_log('writeMediaList')
    existInList = False
    replaced = False

    if not xbmcvfs.exists(globals.DATA_PATH):
        xbmcvfs.mkdirs(globals.DATA_PATH)
    if not xbmcvfs.exists(settings.MEDIALIST_FILENNAME_AND_PATH):
        xbmcvfs.File(settings.MEDIALIST_FILENNAME_AND_PATH, 'w').close()

    thelist = readMediaList()

    thelist = [x for x in thelist if x != '']
    if len(thelist) > 0 :
        for entry in thelist:
            splits = entry.strip().split('|')
            if getStrmname(splits[1]).lower() == getStrmname(name).lower():
                existInList = True
                splits[0] = cType
                splits[1] = name
                plugin = re.sub('.*(plugin:\/\/[^<]*)', '\g<1>', url)
                name_orig = re.sub('(?:name_orig=([^;]*);)(plugin:\/\/[^<]*)', '\g<1>', url)

                replaced = False
                splits2 = list(filter(None, splits[2].split('<next>')))
                for s, split2 in enumerate(splits2):
                    split2_plugin = re.sub('.*(plugin:\/\/[^<]*)', '\g<1>', split2)
                    split2_name_orig = re.sub('(?:name_orig=([^;]*);)(plugin:\/\/[^<]*)', '\g<1>', split2)
                    if re.sub('%26OfferGroups%3DB0043YVHMY', '', split2_plugin) == re.sub('%26OfferGroups%3DB0043YVHMY', '', plugin) or split2_name_orig == name_orig:
                        splits2[s] = url
                        replaced = True
                if replaced == True:
                    splits[2] = '<next>'.join(set(splits2))
                    addon_log_notice('writeMediaList: replace {0} in {1}'.format(name_orig, name))
                else:
                    splits[2] = '{0}<next>{1}'.format(splits[2], url) if splits[2].strip() != '' else '{0}'.format(url)
                    addon_log_notice('writeMediaList: append {0} to {1}'.format(name_orig, name))
                if albumartist:
                    if len(splits) == 5:
                        splits[4] = albumartist
                    else:
                        splits.append(albumartist)

                newentry = '|'.join(splits)
                thelist = replaceStringElem(thelist, entry, newentry)

    if not existInList:
        newentry = [cType, name, url]
        if albumartist:
            newentry.append(albumartist)
        newentry = ('|'.join(newentry))
        thelist.append(newentry)

    output_file = xbmcvfs.File(settings.MEDIALIST_FILENNAME_AND_PATH, 'w')
    output_file.write(bytearray('\n'.join(thelist).strip(), 'utf-8'))

    if not existInList or not replaced:
        globals.dialog.notification(getString(39141, globals.addon), getStrmname(name), globals.MEDIA_ICON, 5000)


def writeTutList(step):
    addon_log('writeTutList')
    existInList = False
    thelist = []
    thefile = os.path.join(globals.DATA_PATH, 'firstTimeTut.xml')
    theentry = '{0}\n'.format(step)

    if not xbmcvfs.exists(globals.DATA_PATH):
        xbmcvfs.mkdirs(globals.DATA_PATH)
    if not xbmcvfs.exists(thefile):
        open(thefile, 'a').close()

    fle = codecs.open(thefile, 'r', 'utf-8')
    thelist = fle.readlines()
    fle.close()
    del fle

    if len(thelist) > 0:
        for i in thelist:
            if i.find(step) != -1:
                existInList = True
    if existInList != True:
        thelist.append(step)

        with open(thefile, 'w') as output_file:
            for linje in thelist:
                if not linje.startswith('\n'):
                    output_file.write('{0}\n'.format(linje.strip()))
                else:
                    output_file.write(linje.strip())
            return False
    else:
        return True


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    else:
        fle = codecs.open(thefile, 'r', 'utf-8')
        thelist = fle.readlines()
        fle.close()
        del fle
    if theentry not in thelist:
        thelist.append(theentry)
    else:
        thelist = replaceStringElem(thelist, theentry, theentry)

    with open(thefile, 'w') as output_file:
        for linje in thelist:
            if not linje.startswith('\n'):
                output_file.write('{0}\n'.format(linje.strip()))
            else:
                output_file.write(linje.strip())


def removeMediaList(delList):
    addon_log('Removing items')

    if xbmcvfs.exists(settings.MEDIALIST_FILENNAME_AND_PATH):
        removeStreamsFromDatabaseAndFilesystem(delList)

        thelist = readMediaList()

        newlist = []
        for entry in thelist:
            additem = True
            for item in delList:
                if entry.find(item.get('url')) > -1:
                    if entry.find('<next>') > -1:
                        entry = entry.replace('name_orig={0};{1}'.format(item.get('name_orig', ''), item.get('url')), '')
                        entry = entry.replace(item.get('url'), '')
                        splits = entry.split('|')
                        splits[2] = '<next>'.join(list(filter(None, splits[2].split('<next>'))))
                        entry = '|'.join(splits)
                        if len(splits[2]) == 0:
                            additem = False
                    else:
                        additem = False
                        break;

            if additem:
                newlist.append(entry)

        fle = xbmcvfs.File(settings.MEDIALIST_FILENNAME_AND_PATH, 'w')
        fle.write(bytearray('\n'.join(newlist).strip(), 'utf-8'))
        fle.close()
        del fle


def readMediaList():
    if xbmcvfs.exists(settings.MEDIALIST_FILENNAME_AND_PATH):
        fle = xbmcvfs.File(settings.MEDIALIST_FILENNAME_AND_PATH, 'r')
        thelist = py2_decode(fle.read()).splitlines()
        fle.close()
        return thelist
    else:
        return list()


def removeStreamsFromDatabaseAndFilesystem(delList):
    for item in delList:
        try:
            splits = item.get('entry').split('|')
            type = splits[0]
            isAudio = True if type.lower().find('audio') > -1 else False

            if type.lower().find('movies') > -1:
                path = xbmc.translatePath(os.path.join(settings.STRM_LOC, getMovieStrmPath(type, splits[1])))
            else:
                path = os.path.join(settings.STRM_LOC, type)

                if isAudio and len(splits) > 3:
                    path = os.path.join(path, cleanByDictReplacements(splits[3]))

                itemPath = getStrmname(splits[1])
                path = xbmc.translatePath(os.path.join(path, cleanStrmFilesys(itemPath)))

            path = completePath(py2_decode(path))

            addon_log('remove: {0}'.format(path))

            deleteFromFileSystem = True
            for split2 in splits[2].split('<next>'):
                streams = None
                if type.lower().find('tv-shows') > -1 or type.lower().find('movies') > -1:
                    deleteFromFileSystem = False
                    streams = [stream[0] for stream in delStream(path[len(settings.STRM_LOC) + 1:len(path)], getProviderId(item.get('url')).get('providerId'), type.lower().find('tv-shows') > -1)]
                    if len(streams) > 0:
                        dirs, files = xbmcvfs.listdir(path)
                        for file in files:
                            if py2_decode(file).replace('.strm', '') in streams:
                                filePath = os.path.join(py2_encode(path), file)
                                addon_log_notice('removeStreamsFromDatabaseAndFilesystem: delete file = \'{0}\''.format(py2_decode(filePath)))
                                xbmcvfs.delete(xbmc.translatePath(filePath))
                    dirs, files = xbmcvfs.listdir(path)
                    if not files and not dirs:
                        deleteFromFileSystem = True
                        addon_log_notice('removeStreamsFromDatabaseAndFilesystem: delete empty directory = {0}'.format(path))

            if deleteFromFileSystem:
                xbmcvfs.rmdir(path, force=True)

            if isAudio:
                jsonrpc('AudioLibrary.Clean')
        except OSError:
                print ('Unable to remove: {0}'.format(path))