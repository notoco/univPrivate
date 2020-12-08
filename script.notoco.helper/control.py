# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui
import os, sys

addon = xbmcaddon.Addon()
state = addon.getSetting('state')
icon = addon.getAddonInfo('icon')
xbmc_host = addon.getSetting('host')
xbmc_port = addon.getSetting('port')
amb_bright = addon.getSetting('bright')


headers = {'content-type': 'application/json'}

xbmc_json_rpc_url = "http://" + xbmc_host + ":" + str(xbmc_port) + "/json-rpc"

def turn_off():
    os.system("hyperion-remote -L 0")
    addon.setSetting('state', 'false')
    send_notification("Ambilight", "Off")

def turn_on():
    os.system("hyperion-remote -L " + amb_bright)
    addon.setSetting('state', 'true')
    send_notification("Ambilight", "On")

def send_notification(komponent, message):
    xbmcgui.Dialog().notification(komponent, message, icon=icon)

def get_setting(name):
    return addon.getSetting(name)

def set_setting(name, value):
    addon.setSetting(name, value)

