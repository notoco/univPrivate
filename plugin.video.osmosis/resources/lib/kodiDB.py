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
from kodi_six.utils import py2_decode
from datetime import datetime
import mysql.connector
import os
import sqlite3
import xbmc
import xbmcvfs

from .common import Globals, Settings
from .stringUtils import cleanStrmFilesys, cleanTitle, completePath, invCommas
from .utils import addon_log

globals = Globals()
settings = Settings()


class Config(object):
    '''Configure me so examples work

    Use me like this:

        mysql.connector.Connect(**Config.dbinfo())
    '''

    if settings.USE_MYSQL:
        DATABASETYPE = ''
        CHARSET = 'utf8'
        UNICODE = True
        WARNINGS = True
        BUFFERED = True


        # Databases
        @classmethod
        def dataBaseVal(cls):

            DBValues = ['USERNAME', 'PASSWORD', 'NAME', 'IP', 'PORT']

            if cls.DATABASETYPE == 'KMovies':
                DBValues = [
                    settings.DATABASE_MYSQL_KODI_VIDEO_USERNAME,
                    settings.DATABASE_MYSQL_KODI_VIDEO_PASSWORD,
                    settings.DATABASE_MYSQL_KODI_VIDEO_DATABASENAME,
                    settings.DATABASE_MYSQL_KODI_VIDEO_IP,
                    settings.DATABASE_MYSQL_KODI_VIDEO_PORT
                ]
            elif cls.DATABASETYPE == 'KMusic':
                DBValues = [
                    settings.DATABASE_MYSQL_KODI_MUSIC_USERNAME,
                    settings.DATABASE_MYSQL_KODI_MUSIC_PASSWORD,
                    settings.DATABASE_MYSQL_KODI_MUSIC_DATABASENAME,
                    settings.DATABASE_MYSQL_KODI_MUSIC_IP,
                    settings.DATABASE_MYSQL_KODI_MUSIC_PORT
                ]
            elif cls.DATABASETYPE == 'Movies':
                DBValues = [
                    settings.DATABASE_MYSQL_OSMOSIS_MOVIE_USERNAME,
                    settings.DATABASE_MYSQL_OSMOSIS_MOVIE_PASSWORD,
                    settings.DATABASE_MYSQL_OSMOSIS_MOVIE_DATABASENAME,
                    settings.DATABASE_MYSQL_OSMOSIS_MOVIE_IP,
                    settings.DATABASE_MYSQL_OSMOSIS_MOVIE_PORT
                ]
            elif cls.DATABASETYPE == 'TVShows':
                DBValues = [
                    settings.DATABASE_MYSQL_OSMOSIS_TVSHOW_USERNAME,
                    settings.DATABASE_MYSQL_OSMOSIS_TVSHOW_PASSWORD,
                    settings.DATABASE_MYSQL_OSMOSIS_TVSHOW_DATABASENAME,
                    settings.DATABASE_MYSQL_OSMOSIS_TVSHOW_IP,
                    settings.DATABASE_MYSQL_OSMOSIS_TVSHOW_PORT
                ]
            elif cls.DATABASETYPE == 'Music':
                DBValues = [
                    settings.DATABASE_MYSQL_OSMOSIS_MUSIC_USERNAME,
                    settings.DATABASE_MYSQL_OSMOSIS_MUSIC_PASSWORD,
                    settings.DATABASE_MYSQL_OSMOSIS_MUSIC_DATABASENAME,
                    settings.DATABASE_MYSQL_OSMOSIS_MUSIC_IP,
                    settings.DATABASE_MYSQL_OSMOSIS_MUSIC_PORT
                ]

            return {
                'user': DBValues[0],
                'password': DBValues[1],
                'database': DBValues[2],
                'host': DBValues[3],
                'port': DBValues[4],
                'charset': cls.CHARSET,
                'use_unicode': cls.UNICODE,
                'get_warnings': cls.WARNINGS,
                'buffered': cls.BUFFERED,
            }


def initDatabase():
    for database in globals.DATABASES:
        if database.get('dbtype') == 'movies': database.get('db')['sqliteDB'] = settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH
        elif database.get('dbtype') == 'tvshows': database.get('db')['sqliteDB'] = settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH
        elif database.get('dbtype') == 'music': database.get('db')['sqliteDB'] = settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH

    if not settings.USE_MYSQL:
        if not xbmcvfs.exists(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH):
            if not xbmcvfs.exists(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_PATH):
                xbmcvfs.mkdirs(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_PATH)
            createMovDB()
        elif not valDB(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'Movies'):
            xbmcvfs.delete(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH)
            createMovDB()

        if not xbmcvfs.exists(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH):
            if not xbmcvfs.exists(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_PATH):
                xbmcvfs.mkdirs(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_PATH)
            createShowDB()
        elif not valDB(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'TVShows'):
            xbmcvfs.delete(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH)
            createShowDB()

        if not xbmcvfs.exists(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH):
            if not xbmcvfs.exists(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_PATH):
                xbmcvfs.mkdirs(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_PATH)
            createMusicDB()
        elif not valDB(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH, 'Music'):
            xbmcvfs.delete(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH)
            createMusicDB()
    else:
        if not valDB(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'Movies'):
            createMovDB()

        if not valDB(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'TVShows'):
            createShowDB()

        if not valDB(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH, 'Music'):
            createMusicDB()

    createSchemaVersionTable()


def updateDatabase():
    dirs, files = xbmcvfs.listdir(globals.DATABASE_SQLLITE_OSMOSIS_SCHEMA_VERSION_FILES_PATH)
    for dir in dirs:
        dbtype = dir.lower()
        dir_path = os.path.join(globals.DATABASE_SQLLITE_OSMOSIS_SCHEMA_VERSION_FILES_PATH, dir)
        subdirs, subfiles = xbmcvfs.listdir(dir_path)
        for subfile in subfiles:
            file_path = os.path.join(dir, subfile)
            if not checkSchemaVersion(file_path, dbtype):
                complete_file_path = os.path.join(dir_path, subfile)
                file = xbmcvfs.File(complete_file_path, 'r')
                query = file.read()
                file.close()
                con, cursor = None, None
                try:
                    for database in globals.DATABASES:
                        if database.get('dbtype') == dbtype:
                            con, cursor = openDB(database.get('db').get('sqliteDB'), database.get('db').get('mysqlDBType'))
                            cursor.execute(query)
                finally:
                    if cursor:
                        cursor.close()
                    if con:
                        con.close()

                writeSchemaVersion(os.path.join(dir, subfile), datetime.now(), 1, dbtype)


def musicDatabase(strAlbumName, strArtistName, strSongTitle, strPath, strURL, iTrack, iDuration, strArtPath, listGenre, iYear, tFileModTime=None):
    strPath = completePath(os.path.join(settings.STRM_LOC, strPath))

    # Write to music db and get id's
    iRoleID = writeRole('Artist')
    iPathID = writePath(strPath)
    iArtistID = writeArtist(strArtistName)
    iAlbumID = writeAlbums(strAlbumName, strArtistName)
    iSongID = writeSong(iPathID, iAlbumID, strArtistName, strSongTitle, iDuration, iTrack, listGenre, iYear, tFileModTime)
    iSongArtistID = writeSongArtist(iArtistID, iSongID, 1, strArtistName, 0)
    if listGenre:
        for strGenre in listGenre:
            iGenreID = writeGenre(strGenre)
            writeSongGenre(iGenreID, iSongID)
    writeAlbumArtist(iArtistID, iAlbumID, strArtistName)
    if strArtPath and strArtPath != '':
        writeThump(iArtistID, 'artist', 'thumb', strArtPath)
        writeThump(iAlbumID, 'album', 'thumb', strArtPath)

    writeIntoSongTable(strSongTitle, iSongID, strArtistName, strAlbumName, iAlbumID, strPath, iPathID, strURL, iRoleID, iArtistID, iSongArtistID, 'F')


def createMusicDB():
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH, 'Music')

        query = 'CREATE TABLE songs (id INTEGER PRIMARY KEY{}, \
                strSongTitle VARCHAR(255), \
                strArtistName VARCHAR(255), \
                strAlbumName VARCHAR(255), \
                strPath TEXT, \
                strURL TEXT, \
                roleID INTEGER, \
                pathID INTEGER, \
                artistID INTEGER, \
                albumID INTEGER, \
                songID INTEGER, \
                songArtistRel INTEGER, \
                delSong CHAR(1));'

        query = query.format('' if not settings.USE_MYSQL else ' AUTO_INCREMENT')

        cursor.execute(query)
        con.commit()
    finally:
        cursor.close()
        con.close()


def writeRole(strRole):
    selectQuery = 'SELECT idRole FROM role WHERE strRole LIKE \'{}\';'
    selectArgs = (strRole,)
    insertQuery = 'INSERT INTO role (strRole) VALUES (\'{}\');'
    insertArgs = (strRole,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writePath(strPath):
    selectStrPath = strPath if not settings.USE_MYSQL else strPath.replace('\\', '\\\\\\\\')
    insertStrPath = strPath if not settings.USE_MYSQL else strPath.replace('\\', '\\\\')

    selectQuery = 'SELECT idPath FROM path WHERE strPath LIKE \'{}\';'
    selectArgs = (selectStrPath,)
    insertQuery = 'INSERT INTO path (strPath) VALUES (\'{}\');'
    insertArgs = (insertStrPath,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeArtist(strArtist):
    selectQuery = 'SELECT idArtist FROM artist WHERE strArtist LIKE \'{}\';'
    selectArgs = (strArtist,)
    insertQuery = 'INSERT INTO artist (strArtist) VALUES (\'{}\');'
    insertArgs = (strArtist,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeGenre(strGenre):
    selectQuery = 'SELECT idGenre FROM genre WHERE strGenre LIKE \'{}\';'
    selectArgs = (strGenre,)
    insertQuery = 'INSERT INTO genre (strGenre) VALUES (\'{}\');'
    insertArgs = (strGenre,)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeAlbums(strAlbum, strArtist, strReleaseType='album'):
    artistCol = 'strArtistDisp' if globals.KODI_VERSION >= 18 else 'strArtists'

    selectQuery = 'SELECT idAlbum FROM album WHERE strAlbum LIKE \'{}\';'
    selectArgs = (strAlbum,)
    insertQuery = 'INSERT INTO album (strAlbum, ' + artistCol + ', strReleaseType, strGenres) VALUES (\'{}\', \'{}\', \'{}\', \'{}\');'
    insertArgs = (strAlbum, strArtist, strReleaseType, 'osmosis')

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeSong(iPathID, iAlbumID, strArtist, strTitle, iDuration, iTrack, listGenre, iYear, tFileModTime):
    tDateAdded = datetime.fromtimestamp(tFileModTime) if tFileModTime else datetime.now()
    strDateAdded = tDateAdded.strftime('%Y-%m-%d %H:%M:%S')
    strTitle = invCommas(strTitle)
    strFileName = cleanStrmFilesys(strTitle)
    strFileName = '{0}.strm'.format(strFileName)

    selectQuery = 'SELECT idSong FROM song WHERE strArtistDisp LIKE \'{}\' AND strTitle LIKE \'{}\';'
    selectArgs = (strArtist, strTitle)
    insertQuery = 'INSERT INTO song (dateAdded, idAlbum, idPath, strArtistDisp, strTitle, strFileName, iTrack, iDuration, iTimesPlayed, iStartOffset, iEndOffset, userrating, comment, mood, votes'
    insertQueryValue = ' VALUES (\'{}\', {}, {}, \'{}\', \'{}\', \'{}\', {}, {}, {}, {}, {}, {}, \'{}\', \'{}\', {}'
    insertArgs = (strDateAdded, iAlbumID, iPathID, strArtist, strTitle, strFileName, iTrack, iDuration, 0, 0, 0, 0, 'osmosis', 'osmosis', 0)
    updateQuery = 'UPDATE song SET idAlbum = {}, idPath = {}, strFileName = \'{}\', iTrack = {}, iDuration = {} WHERE strArtistDisp LIKE \'{}\' AND strTitle LIKE \'{}\';'
    updateArgs = (iAlbumID, iPathID, strFileName, iTrack, iDuration, strArtist, strTitle)
    if listGenre:
        strGenres = ', '.join(genre.strip() for genre in listGenre)
        insertQuery += ', strGenres'
        insertQueryValue += ', \'{}\''
        insertArgs += (strGenres,)
    if iYear:
        if globals.KODI_VERSION == 18:
            insertQuery += ', iYear'
            insertQueryValue += ', {}'
        else:
            insertQuery += ', strReleaseDate'
            insertQueryValue += ', \'{}\''
        insertArgs += (iYear,)

    insertQuery += ')'
    insertQueryValue += ');'

    return manageDbRecord(selectQuery, selectArgs, '{0}{1}'.format(insertQuery, insertQueryValue), insertArgs, updateQuery, updateArgs)


def writeSongArtist(iArtistID, iSongID, iRoleID, strArtist, iOrderID):
    selectQuery = 'SELECT idSong FROM song_artist WHERE idSong = {};'
    selectArgs = (iSongID,)
    insertQuery = 'INSERT INTO song_artist (idArtist, idSong, idRole, iOrder, strArtist) VALUES (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'
    insertArgs = (iArtistID, iSongID, iRoleID, iOrderID, strArtist)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeSongGenre(genreID, songID):
    selectQuery = 'SELECT idSong FROM song_genre WHERE idGenre=\'{}\' and idSong=\'{}\';'
    selectArgs = (genreID, songID)
    insertQuery = 'INSERT INTO song_genre (idGenre, idSong, iOrder) VALUES (\'{}\', \'{}\', \'{}\');'
    insertArgs = (genreID, songID, 0)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeAlbumArtist(iArtistID, iAlbumID, strArtist):
    selectQuery = 'SELECT idAlbum FROM album_artist WHERE idAlbum = {};'
    selectArgs = (iAlbumID,)
    insertQuery = 'INSERT INTO album_artist (idArtist, idAlbum, iOrder, strArtist) VALUES (\'{}\', \'{}\', \'{}\', \'{}\');'
    insertArgs = (iArtistID, iAlbumID, 0, strArtist)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeThump(iMediaID, strMediaType, strImageType, strArtPath):
    selectQuery = 'SELECT media_id FROM art WHERE media_id = {} AND media_type LIKE \'{}\';'
    selectArgs = (iMediaID, strMediaType)
    insertQuery = 'INSERT INTO art (media_id, media_type, type, url) VALUES (\'{}\', \'{}\', \'{}\', \'{}\');'
    insertArgs = (iMediaID, strMediaType, strImageType, strArtPath)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs)


def writeIntoSongTable (strSongTitle, iSongID, strArtistName, strAlbumName, iAlbumID, strPath, iPathID, strURL, iRoleID, iArtistID, iSongArtistID, strDelSong):
    strPath = strPath if not settings.USE_MYSQL else strPath.replace('\\', '\\\\')
    strSongTitle = strSongTitle.replace('\'', '\'\'')

    selectQuery = 'SELECT id FROM songs WHERE songID = {} AND artistID = {} AND albumID = {};'
    selectArgs = (iSongID, iArtistID, iAlbumID)
    insertQuery = 'INSERT INTO songs (strSongTitle, songID, strArtistName, strAlbumName, albumID, strPath, pathID, strURL, roleID, artistID, songArtistRel, delSong) VALUES (\'{}\', {}, \'{}\', \'{}\', {}, \'{}\', {}, \'{}\', {}, {}, \'{}\', \'{}\');'
    insertArgs = (strSongTitle, iSongID, strArtistName, strAlbumName, iAlbumID, strPath, iPathID, strURL, iRoleID, iArtistID, iSongArtistID, strDelSong)

    return manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, database=settings.DATABASE_SQLLITE_OSMOSIS_MUSIC_FILENAME_AND_PATH)


def manageDbRecord(selectQuery, selectArgs, insertQuery, insertArgs, updateQuery=None, updateArgs=None, database=settings.DATABASE_SQLLITE_KODI_MUSIC_FILENAME_AND_PATH):
    dID = None
    try:
        con, cursor = openDB(database, 'KMusic' if database == settings.DATABASE_SQLLITE_KODI_MUSIC_FILENAME_AND_PATH else 'Music')

        if selectArgs:
            selectQuery = selectQuery.format(*selectArgs)
            cursor.execute(selectQuery)
        else:
            cursor.execute(selectQuery)

        searchResult = cursor.fetchone()

        if not searchResult:
            insertQuery = insertQuery.format(*insertArgs)
            cursor.execute(insertQuery)
            con.commit()
            dID = cursor.lastrowid
        else:
            if updateQuery:
                if updateArgs:
                    updateQuery = updateQuery.format(*updateArgs)
                    cursor.execute(updateQuery)
                else:
                    cursor.execute(updateQuery)
                con.commit()
            dID = searchResult[0]
    finally:
        cursor.close()
        con.close()

    return dID


def valDB(dbpath, dbtype):
    con, cursor = openDB(dbpath, dbtype)

    if dbtype == 'Music':
        table = 'songs'
    else:
        table = 'stream_ref'

    if not settings.USE_MYSQL:
        query = 'SELECT * FROM sqlite_master WHERE name LIKE \'{0}\' and type LIKE \'table\';'.format(table)

        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        con.close()
        return True if len(result) == 1 else False
    else:
        query = 'SHOW TABLES LIKE \'{0}\';'.format(table)

        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        con.close()
        return True if result else False


def writeMovie(movieList):
    dbMovieList = []

    for entry in movieList:
        kmovName = kmovieExists(entry.get('title'), entry.get('imdbnumber'))
        movID = movieExists(kmovName, entry.get('path'))
        if movID is not None:
            movieStreamExists(movID, entry.get('provider'), entry.get('url'))
            dbMovieList.append({'path': entry.get('path'), 'title': kmovName, 'movieID': movID, 'provider': entry.get('provider')})

    return dbMovieList


def writeShow(episode):
    dbEpisode = None

    if episode is not None:
        showID = showExists(episode.get('tvShowTitle'), episode.get('path'))
        if showID is not None:
            episodeStreamExists(showID, episode.get('strSeasonEpisode'), episode.get('provider'), episode.get('url'), episode.get('metadata'))
            dbEpisode = {'path': episode.get('path'), 'tvShowTitle': episode.get('tvShowTitle'), 'showID': showID, 'strSeasonEpisode': episode.get('strSeasonEpisode')}

    return dbEpisode


def createMovDB():
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'Movies')

        sql_strm_ref = 'CREATE TABLE stream_ref (id INTEGER PRIMARY KEY{}, mov_id INTEGER NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);'
        sql_movtable = 'CREATE TABLE movies (id INTEGER PRIMARY KEY{}, title TEXT NOT NULL, filePath TEXT NOT NULL);'

        sql_strm_ref = sql_strm_ref.format('' if not settings.USE_MYSQL else ' AUTO_INCREMENT')
        sql_movtable = sql_movtable.format('' if not settings.USE_MYSQL else ' AUTO_INCREMENT')

        cursor.execute(sql_strm_ref)
        cursor.execute(sql_movtable)
        con.commit()
    finally:
        cursor.close()
        con.close()


def createShowDB():
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'TVShows')

        sql_strm_ref = 'CREATE TABLE stream_ref (id INTEGER PRIMARY KEY{}, show_id INTEGER NOT NULL, seasonEpisode TEXT NOT NULL, provider TEXT NOT NULL, url TEXT NOT NULL);'
        sql_showtable = 'CREATE TABLE shows (id INTEGER PRIMARY KEY{}, showTitle TEXT NOT NULL, filePath TEXT NOT NULL);'

        sql_strm_ref = sql_strm_ref.format('' if not settings.USE_MYSQL else ' AUTO_INCREMENT')
        sql_showtable = sql_showtable.format('' if not settings.USE_MYSQL else ' AUTO_INCREMENT')

        cursor.execute(sql_strm_ref)
        cursor.execute(sql_showtable)
        con.commit()
    finally:
        cursor.close()
        con.close()


def createSchemaVersionTable():
    for database in globals.DATABASES:
        try:
            con, cursor = openDB(database.get('db').get('sqliteDB'), database.get('db').get('mysqlDBType'))

            if not settings.USE_MYSQL:
                query = 'SELECT * FROM sqlite_master WHERE name LIKE \'schema_version\' and type LIKE \'table\';'
                cursor.execute(query)
                result = cursor.fetchone()
            else:
                query = 'SHOW TABLES LIKE \'schema_version\';'
                cursor.execute(query)
                result = cursor.fetchone()

            if not result:
                query = 'CREATE TABLE schema_version (installed_rank INTEGER PRIMARY KEY{0}, filename TEXT NOT NULL, installed_on TIMESTAMP NOT NULL, success TINYINT NOT NULL);'
                query = query.format('' if not settings.USE_MYSQL else ' AUTO_INCREMENT')
                cursor.execute(query)
                con.commit()
        finally:
            cursor.close()
            con.close()


def kmovieExists(title, imdbnumber):
    dbMovieName = None
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH, 'KMovies')

        # title = invCommas(title)
        cursor.execute('SELECT strFileName FROM movie_view WHERE uniqueid_value LIKE \'{}\';'.format(imdbnumber))

        dbMovieName = cursor.fetchone()

        if dbMovieName is None:
            dbMovieName = title
        else:
            dbMovieName = dbMovieName[0]
        dbMovieName = cleanTitle(dbMovieName)
    finally:
        cursor.close()
        con.close()

    return dbMovieName


def movieExists(title, path):
    dbMovieID = None
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'Movies')

        title = invCommas(title)

        cursor.execute('SELECT id, title, filePath FROM movies WHERE title LIKE \'{}\';'.format(title))
        dbMovie = cursor.fetchone()

        path = completePath(path) if not settings.USE_MYSQL else completePath(path).replace('\\', '\\\\')
        path = invCommas(path)
        if dbMovie is None:
            cursor.execute('INSERT INTO movies (title, filePath) VALUES (\'{}\', \'{}\');'.format(title, path))
            con.commit()
            dbMovieID = cursor.lastrowid
        else:
            dbMovieID = dbMovie[0]
            if py2_decode(dbMovie[2]) != path:
                cursor.execute('UPDATE movies SET filePath = \'{0}\' WHERE id LIKE \'{1}\';'.format(path, dbMovieID))
                con.commit()
    finally:
        cursor.close()
        con.close()

    return dbMovieID


def movieStreamExists(movieID, provider, url):
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'Movies')

        if url.find('?url=plugin') != -1:
            url = url.strip().replace('?url=plugin', 'plugin', 1)

        cursor.execute('SELECT mov_id, url FROM stream_ref WHERE mov_id = {} AND provider LIKE \'{}\';'.format(movieID, provider))
        dbMovie = cursor.fetchall()

        if len(dbMovie) > 1:
            cursor.execute('DELETE FROM stream_ref WHERE mov_id = {} AND provider LIKE \'{}\';'.format(movieID, provider))
            dbMovie = []

        if len(dbMovie) == 0:
            cursor.execute('INSERT INTO stream_ref (mov_id, provider, url) VALUES ({}, \'{}\', \'{}\');'.format(movieID, provider, invCommas(url)))
            con.commit()
        else:
            if py2_decode(dbMovie[0][1]) != url:
                cursor.execute('UPDATE stream_ref SET url=\'{}\' WHERE mov_id = {};'.format(invCommas(url), movieID))
                con.commit()
    finally:
        cursor.close()
        con.close()


def showExists(title, path):
    dbShowID = None
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'TVShows')

        title = invCommas(title)

        cursor.execute('SELECT id, showTitle FROM shows WHERE showTitle LIKE \'{}\';'.format(title))
        dbShow = cursor.fetchone()

        if dbShow is None:
            path = completePath(path) if not settings.USE_MYSQL else completePath(path).replace('\\', '\\\\')
            path = invCommas(path)
            cursor.execute('INSERT INTO shows (showTitle, filePath) VALUES (\'{}\', \'{}\');'.format(title, path))
            con.commit()
            dbShowID = cursor.lastrowid
        else:
            dbShowID = dbShow[0]
    finally:
        cursor.close()
        con.close()

    return dbShowID


def episodeStreamExists(showID, seEp, provider, url, metadata):
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'TVShows')

        if url.find('?url=plugin') > -1:
            url = url.strip().replace('?url=plugin', 'plugin', 1)

        cursor.execute('SELECT show_id, url, metadata FROM stream_ref WHERE show_id = {0} AND seasonEpisode LIKE \'{1}\' AND provider LIKE \'{2}\';'.format(showID, seEp, provider))
        dbShow = cursor.fetchall()

        if len(dbShow) > 1:
            cursor.execute('DELETE FROM stream_ref WHERE show_id = {0} AND seasonEpisode LIKE \'{1}\' AND provider LIKE \'{2}\';'.format(showID, seEp, provider))
            dbShow = []

        if len(dbShow) == 0:
            query = 'INSERT INTO stream_ref (show_id, seasonEpisode, provider, url, metadata) VALUES ({0}, \'{1}\', \'{2}\', \'{3}\', \'{4}\');'.format(showID, seEp, provider, invCommas(url), invCommas(metadata))
            cursor.execute(query)
            con.commit()
        else:
            if py2_decode(dbShow[0][1]) != url or not dbShow[0][2]:
                cursor.execute('UPDATE stream_ref SET url = \'{0}\', metadata = \'{1}\' WHERE show_id = {2} AND seasonEpisode LIKE \'{3}\' AND provider LIKE \'{4}\';'.format(invCommas(url), invCommas(metadata), showID, seEp, provider))
                con.commit()
    finally:
        cursor.close()
        con.close()


def getVideo(ID, seasonEpisode=None):
    provList = None

    try:
        args = {'sqliteDB': settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'mysqlDBType': 'Movies'} if not seasonEpisode \
                else {'sqliteDB': settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'mysqlDBType': 'TVShows'}
        con, cursor = openDB(**args)

        if seasonEpisode is None:
            query = 'SELECT stream_ref.url, stream_ref.provider, movies.filePath FROM stream_ref INNER JOIN movies ON stream_ref.mov_id = movies.id WHERE stream_ref.mov_id = {};'
            args = (ID,)
        else:
            query = 'SELECT stream_ref.url, stream_ref.provider, shows.filePath, stream_ref.metadata FROM stream_ref INNER JOIN shows ON stream_ref.show_id = shows.id WHERE stream_ref.show_id = {} AND stream_ref.seasonEpisode LIKE \'{}\';'
            args = (ID, seasonEpisode)

        cursor.execute(query.format(*args))
        provList = cursor.fetchall()
    finally:
        cursor.close()
        con.close()

    return provList


def delStream(path, provider, isShow):
    streams = []

    addon_log('delStream: path = {0}, provider = {1}, isShow = {2}'.format(py2_decode(path), py2_decode(provider), isShow))
    try:
        args = {'sqliteDB': settings.DATABASE_SQLLITE_OSMOSIS_MOVIE_FILENAME_AND_PATH, 'mysqlDBType': 'Movies'} if not isShow \
                else {'sqliteDB': settings.DATABASE_SQLLITE_OSMOSIS_TVSHOW_FILENAME_AND_PATH, 'mysqlDBType': 'TVShows'}
        con, cursor = openDB(**args)

        path = invCommas(path)
        if isShow == False:
            query = 'SELECT movies.title FROM movies WHERE movies.id IN (SELECT stream_ref.mov_id FROM stream_ref WHERE stream_ref.mov_id IN (SELECT movies.id FROM movies WHERE movies.filePath like \'{0}\') and stream_ref.provider like \'{1}\');'
        else:
            query = 'SELECT stream_ref.seasonEpisode FROM stream_ref WHERE stream_ref.show_id IN (SELECT shows.id FROM shows WHERE shows.filePath like \'{0}\') and stream_ref.provider like \'{1}\';'
        args = [path, provider]
        addon_log('delStream: query = {0}'.format(query.format(*args)))
        cursor.execute(query.format(*args))
        streams_delete = cursor.fetchall()

        if isShow == False:
            query = 'DELETE FROM stream_ref WHERE stream_ref.mov_id IN (SELECT movies.id FROM movies WHERE movies.filePath like \'{0}\') and stream_ref.provider like \'{1}\';'
        else:
            query = 'DELETE FROM stream_ref WHERE stream_ref.show_id IN (SELECT shows.id FROM shows WHERE shows.filePath like \'{0}\') and stream_ref.provider like \'{1}\';'
        addon_log('delStream: query = {0}'.format(query.format(*args)))
        cursor.execute(query.format(*args))
        con.commit()

        if isShow == False:
            query = 'SELECT movies.title FROM movies WHERE movies.id IN (SELECT stream_ref.mov_id FROM stream_ref WHERE stream_ref.mov_id IN (SELECT movies.id FROM movies WHERE movies.filePath like \'{0}\'));'
        else:
            query = 'SELECT stream_ref.seasonEpisode FROM stream_ref WHERE stream_ref.show_id IN (SELECT shows.id FROM shows WHERE shows.filePath like \'{0}\');'
        addon_log('delStream: query = {0}'.format(query.format(*args)))
        cursor.execute(query.format(*args))
        streams_keep = cursor.fetchall()

        streams = [s for s in streams_delete if s not in streams_keep]
    except:
        streams = []
    finally:
        cursor.close()
        con.close()

    return streams


def delBookMark(bookmarkID, fileID):
    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH, 'KMovies')

        selectquery = 'SELECT idBookmark FROM bookmark WHERE {} = {};'
        deletequery = 'DELETE FROM bookmark WHERE {} = {};'
        args = ('idFile', fileID)

        cursor.execute(selectquery.format(*args))
        dbbookmark = cursor.fetchone()

        if dbbookmark:
            cursor.execute(deletequery.format(*args))

        args = ('idBookmark', bookmarkID)
        cursor.execute(selectquery.format(*args))
        dbbookmark = cursor.fetchone()

        if dbbookmark:
            cursor.execute(deletequery.format(*args))

        con.commit()
    finally:
        cursor.close()
        con.close()


def getKodiMovieID(sFilePath):
    dbMovie = None

    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH, 'KMovies')

        sFilePath = invCommas(sFilePath)

        # movie.c00 = title; movie.c14 = genre; movie.c22 = filepath
        cursor.execute('SELECT movie.idMovie, movie.idFile, movie.premiered, movie.c14, movie.c22 FROM movie WHERE movie.c22 LIKE \'%{0}%\';'.format(sFilePath))
        dbMovie = cursor.fetchone()
        if dbMovie:
            dbMovie = {'id': dbMovie[0], 'fileid': dbMovie[1], 'premiered': dbMovie[2], 'genre': dbMovie[3], 'filepath': dbMovie[4]}
    finally:
        cursor.close()
        con.close()

    return dbMovie


def getKodiEpisodeID(sFilePath, iSeason, iEpisode):
    dbEpisode = None

    try:
        con, cursor = openDB(settings.DATABASE_SQLLITE_KODI_VIDEO_FILENAME_AND_PATH, 'KMovies')

        sFilePath = invCommas(sFilePath)

        # episode.c00 = title; episode.c05 = aired; episode.c06 = thumb; episode.c12 = season; episode.c13 = episode; episode.c18 = filepath;
        query = 'SELECT episode.idEpisode, episode.idFile, episode.c00, episode.c05, episode.c06, episode.c18 FROM episode WHERE episode.c12 = {0} and episode.c13 = {1} and episode.c18 LIKE \'%{2}%\';'
        cursor.execute(query.format(iSeason, iEpisode, sFilePath))
        dbEpisode = cursor.fetchone()
        if dbEpisode:
            dbEpisode = {'id': dbEpisode[0], 'fileid': dbEpisode[1], 'title': dbEpisode[2], 'aired': dbEpisode[3], 'thumb': dbEpisode[4], 'filepath': dbEpisode[5]}
    finally:
        cursor.close()
        con.close()

    return dbEpisode


def openDB(sqliteDB, mysqlDBType):
    if not settings.USE_MYSQL:
        con = sqlite3.connect(sqliteDB)
        cursor = con.cursor()
    else:
        Config.DATABASETYPE = mysqlDBType
        Config.BUFFERED = True
        config = Config.dataBaseVal().copy()
        con = mysql.connector.Connect(**config)
        cursor = con.cursor()

    return con, cursor


def checkSchemaVersion(filename, dbtype):
    con, cursor, entry = None, None, None

    try:
        for database in globals.DATABASES:
            if database.get('dbtype') == dbtype:
                con, cursor = openDB(database.get('db').get('sqliteDB'), database.get('db').get('mysqlDBType'))
                query = 'SELECT * FROM schema_version WHERE schema_version.filename = \'{0}\';'.format(filename)
                cursor.execute(query)
                entry = cursor.fetchone()
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return entry


def writeSchemaVersion(filename, installed_on, success, dbtype):
    con, cursor, entry = None, None, None

    try:
        for database in globals.DATABASES:
            if database.get('dbtype') == dbtype:
                con, cursor = openDB(database.get('db').get('sqliteDB'), database.get('db').get('mysqlDBType'))
                query = 'INSERT INTO schema_version (filename, installed_on, success) VALUES (\'{0}\', \'{1}\', {2});'.format(filename, installed_on, success)
                cursor.execute(query)
                con.commit()
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()
