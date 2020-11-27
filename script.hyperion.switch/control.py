# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui
import requests

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
state = server_enable = addon.getSetting('state')
icon = addon.getAddonInfo('icon')
xbmc_host = addon.getSetting('host')
xbmc_port = addon.getSetting('port')

headers = {'content-type': 'application/json'}

xbmc_json_rpc_url = "http://" + xbmc_host + ":" + str(xbmc_port) + "/json-rpc"

def turn_off():
    hyperion_connect = '{"command":"componentstate","componentstate":{"component":"ALL","state":false}}'
    response = requests.post(xbmc_json_rpc_url, data=hyperion_connect, headers=headers)
    addon.setSetting('state', 'false')

def turn_on():
    hyperion_connect = '{"command":"componentstate","componentstate":{"component":"ALL","state":true}}'
    response = requests.post(xbmc_json_rpc_url, data=hyperion_connect, headers=headers)
    addon.setSetting('state', 'true')

def send_notification(message):
    xbmcgui.Dialog().notification(addonname, message, icon=icon)

def get_setting(name):
    return addon.getSetting(name)

def set_setting(name, value):
    addon.setSetting(name, value)

