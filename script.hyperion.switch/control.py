# -*- coding: utf-8 -*-

import xbmcaddon
import xbmcgui
import os

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
state = server_enable = addon.getSetting('state')
icon = addon.getAddonInfo('icon')


def turn_off():
    os.system("hyperion-remote --off")
    addon.setSetting('state', 'false')


def turn_on():
    os.system("hyperion-remote --on")
    addon.setSetting('state', 'true')


def send_notification(message):
    xbmcgui.Dialog().notification(addonname, message, icon=icon)


def get_setting(name):
    return addon.getSetting(name)


def set_setting(name, value):
    addon.setSetting(name, value)

