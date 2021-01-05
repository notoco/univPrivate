# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui
import os, sys

addon = xbmcaddon.Addon()
state = addon.getSetting('state')
icon = addon.getAddonInfo('icon')
amb_bright = addon.getSetting('bright')

def turn_off():
    os.system("hyperion-remote -L 0")
    addon.setSetting('state', 'false')

def turn_on():
    os.system("hyperion-remote -L " + amb_bright)
    addon.setSetting('state', 'true')

def cpu():
    send_notification("Użycie systemu", "CPU: $INFO[System.CPUUsage]   RAM: $INFO[System.memory(used.percent)]")

def send_notification(komponent, message):
    xbmcgui.Dialog().notification(komponent, message, icon=icon)

def get_setting(name):
    return addon.getSetting(name)

def set_setting(name, value):
    addon.setSetting(name, value)

