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
import os
import re

from .common import Globals, Settings, jsonrpc
from .moduleUtil import getModule
from .utils import multiple_replace, multiple_reSub


def cleanString(string):
    newstr = newstr.replace('&', '&amp;')
    newstr = newstr.replace('>', '&gt;')
    newstr = newstr.replace('<', '&lt;')
    return newstr


def uncleanString(string):
    newstr = string
    newstr = newstr.replace('&amp;', '&')
    newstr = newstr.replace('&gt;', '>')
    newstr = newstr.replace('&lt;', '<')
    return newstr


def cleanLabels(text, formater='', keep_year=False):
    dictresub = {'\[COLOR (.+?)\]' : '', '\[/COLOR\]' : '', '\[COLOR=(.+?)\]' : '', '\[color (.+?)\]': '',
                 '\[/color\]': '', '\[Color=(.+?)\]': '', '\[/Color\]': ''}

    replacements = (('[]', ''), ('[UPPERCASE]', ''),
                   ('[/UPPERCASE]', ''), ('[LOWERCASE]', ''),
                   ('[/LOWERCASE]', ''), ('[B]', ''), ('[/B]', ''),
                   ('[I]', ''), ('[/I]', ''),
                   ('[D]', ''), ('[F]', ''),
                   ('[CR]', ''), ('[HD]', ''),
                   ('()', ''), ('[CC]', ''),
                   ('[Cc]', ''), ('[Favorite]', ''),
                   ('[DRM]', ''), ('(cc).', ''),
                   ('(n)', ''), ('(SUB)', ''),
                   ('(DUB)', ''), ('(repeat)', ''),
                   ('(English Subtitled)', ''), ('*', ''),
                   ('\n', ''), ('\r', ''),
                   ('\t', ''), ('\ ', ''),
                   ('/ ', ''), ('\\', '/'),
                   ('//', '/'), ('plugin.video.', ''),
                   ('plugin.audio.', ''))

    text = multiple_reSub(text, dictresub)
    text = multiple_replace(text, *replacements)
    text = cleanStrmFilesys(text)
    if not keep_year:
        text = re.sub('\(.\d*\)', '', text)
    if formater == 'title':
        text = text.title().replace('\'S', '\'s')
    elif formater == 'upper':
        text = text.upper()
    elif formater == 'lower':
        text = text.lower()

    text = re.sub('\s\s+', ' ', text)

    return text.strip()


def cleanStrms(text, formater=''):
    text = text.replace('Full Episodes', '')
    if formater == 'title':
        text = text.title().replace('\'S', '\'s')
    elif formater == 'upper':
        text = text.upper()
    elif formater == 'lower':
        text = text.lower()
    else:
        text = text
    return text


def cleanStrmFilesys(string):
    return re.sub('[\/:*?<>|!"]', '', string)


def multiRstrip(text):
    replaceRstrip = ['.', ',', '-', '_', ' ', '#', '+', '`', '&', '%', '!', '?']
    for i in replaceRstrip:
        text.rstrip(i)
    return text


def removeHTMLTAGS(text):
    return re.sub('<[^<]+?>', '', text)


def removeNonAscii(s): return ''.join(filter(lambda x: ord(x) < 128, s))


def unicodetoascii(text):

    TEXT = (text.
            replace('\xe2\x80\x99', '\'').
            replace('\xc3\xa9', 'e').
            replace('\xe2\x80\x90', '-').
            replace('\xe2\x80\x91', '-').
            replace('\xe2\x80\x92', '-').
            replace('\xe2\x80\x93', '-').
            replace('\xe2\x80\x94', '-').
            replace('\xe2\x80\x94', '-').
            replace('\xe2\x80\x98', '\'').
            replace('\xe2\x80\x9b', '\'').
            replace('\xe2\x80\x9c', '"').
            replace('\xe2\x80\x9c', '"').
            replace('\xe2\x80\x9d', '"').
            replace('\xe2\x80\x9e', '"').
            replace('\xe2\x80\x9f', '"').
            replace('\xe2\x80\xa6', '...').
            replace('\xe2\x80\xb2', '\'').
            replace('\xe2\x80\xb3', '\'').
            replace('\xe2\x80\xb4', '\'').
            replace('\xe2\x80\xb5', '\'').
            replace('\xe2\x80\xb6', '\'').
            replace('\xe2\x80\xb7', '\'').
            replace('\xe2\x81\xba', '+').
            replace('\xe2\x81\xbb', '-').
            replace('\xe2\x81\xbc', '=').
            replace('\xe2\x81\xbd', '(').
            replace('\xe2\x81\xbe', ')')
            )
    return TEXT


def removeStringElem(lst, string=''):
    return ([x for x in lst if x != string])


def replaceStringElem(lst, old='', new=''):
    return ([x.replace(old, new) for x in lst])


def cleanByDictReplacements(string):
    dictReplacements = {'\'\(\\d+\)\'': '', '()': '', 'Kinofilme': '',
                        '  ': ' ', '\(de\)': '', '\(en\)': '',
                        '\(TVshow\)': '', 'Movies': '', 'Filme': '',
                        'Movie': '', '\'.\'': ' ', '\(\)': '',
                        '"?"': '', '"':''}

    return multiple_reSub(string, dictReplacements)


def getMovieStrmPath(strmTypePath, mediaListEntry_name, movie_name=None):
    settings = Settings()
    if settings.FOLDER_MEDIALISTENTRY_MOVIE:
        mediaListEntry_name = cleanByDictReplacements(getStrmname(mediaListEntry_name))
        mediaListEntry_name = cleanStrmFilesys(mediaListEntry_name)
        strmTypePath = os.path.join(strmTypePath, mediaListEntry_name)
    if movie_name and settings.FOLDER_MOVIE:
        movie_name = cleanByDictReplacements(getStrmname(movie_name))
        movie_name = cleanStrmFilesys(movie_name)
        strmTypePath = os.path.join(strmTypePath, movie_name)

    return strmTypePath


def getStrmname(strm_name):
    return strm_name.replace('++RenamedTitle++', '').strip()


def parseMediaListURL(url):
    match = re.findall('(?:name_orig=([^;]*);)?(.*)', url)
    name_orig = match[0][0] if match[0][0] and match[0][0] != '' else None
    plugin_url = match[0][1]
    return [name_orig, plugin_url]


def invCommas(string):
   string = string.replace('\'', '\'\'')
   return string


def cleanTitle(string):
   string = string.replace('.strm', '')
   return string


def completePath(filepath):
    if not filepath.endswith('\\') and not filepath.endswith('/'):
        filepath += os.sep

    return filepath


def getAddonname(addonid):
    result = jsonrpc('Addons.GetAddonDetails', dict(addonid=addonid, properties=['name']))
    if len(result) > 0:
        return result['addon']['name']
    else:
        return addonid


def getProviderId(url):
    provider = None
    plugin_id = re.search('plugin:\/\/([^\/\?]*)', url)

    if plugin_id:
        module = getModule(plugin_id.group(1))
        if module and hasattr(module, 'getProviderId'):
            providerId = module.getProviderId(plugin_id.group(1), url)
        else:
            providerId = plugin_id.group(1)

        provider = dict(plugin_id=plugin_id.group(1), providerId=providerId)

    return provider


def getProvidername(url):
    provider = getProviderId(url)

    if provider:
        pid = provider.get('plugin_id')
        provider = Globals().CACHE_ADDONNAME.cacheFunction(getAddonname, pid)
        module = getModule(pid)
        if module and hasattr(module, 'getProvidername'):
            provider = module.getProvidername(provider, url)

    return provider
