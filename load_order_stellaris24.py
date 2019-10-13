# -*- coding: utf-8 -*-
import json
from shutil import copyfile
import os
import ctypes  # An included library with Python install.
import sys

def abort(message):
    Mbox('', message, 0)
    sys.exit(1)

class Mod():
    def __init__(self, hashKey, name, modId):
        self.hashKey = hashKey
        self.name = name
        self.modId = modId
        self.sortedKey = name.encode('ascii', errors='ignore')

def sortedKey(mod):
    return mod.sortedKey

def getModList(data):
	modList = []
	for key, data in data.items():
		name = data['displayName']
		modId = data['gameRegistryId']
		mod = Mod(key, name, modId)
		modList.append(mod)
	modList.sort(key=sortedKey, reverse=True)
	return modList


def writeLoadOrder(idList, dlc_load, enabled_mods):
    data = {}
    with open(dlc_load, 'r+') as json_file:
        data = json.load(json_file)

    if len(data) < 1:
        abort('dlc_load.json loading failed')
    if enabled_mods is not None:
        idList = [m for m in idList if m in enabled_mods]
    data['enabled_mods'] = idList

    with open(dlc_load, 'w') as json_file:
        json.dump(data, json_file)

def writeDisplayOrder(hashList, game_data):
    data = {}
    with open(game_data, 'r+') as json_file:
        data = json.load(json_file)
    if len(data) < 1:
        abort('game_data.json loading failed')
    data['modsOrder'] = hashList
    with open(game_data, 'w') as json_file:
        json.dump(data, json_file)

def run(settingPath):
    registry = os.path.join(settingPath, 'mods_registry.json')
    dlc_load = os.path.join(settingPath, 'dlc_load.json')
    copyfile(dlc_load, dlc_load + '.bak')
    game_data = os.path.join(settingPath, 'game_data.json')
    copyfile(game_data, game_data + '.bak')

    modList = []
    with open(registry) as json_file:
        data = json.load(json_file)
        modList = getModList(data)
    if len(modList) <= 0:
        abort('no mod found')
    enabled_mods = None
    if os.path.exists(dlc_load):
        with open(dlc_load) as dlc_load_file:
            dlc_load_data = json.load(dlc_load_file)
            # Do some legwork ahead of time to put into a set to avoidic quadratic loop later for filtering.
            enabled_mods = frozenset(dlc_load_data.get("enabled_mods", []))
    idList = [mod.modId for mod in modList]
    hashList = [mod.hashKey for mod in modList]
    writeDisplayOrder(hashList, game_data)
    writeLoadOrder(idList, dlc_load, enabled_mods)

def Mbox(title, text, style):
    if hasattr(ctypes, "windll"):
        return ctypes.windll.user32.MessageBoxW(0, text, title, style)
    else:
        print(text)

# check Stellaris settings location
locations = [os.path.join(os.path.expanduser('~'), 'Documents', 'Paradox Interactive', 'Stellaris'), ".", "..", os.path.join(os.path.expanduser('~'), '.local', 'share','Paradox Interactive', 'Stellaris')]
settingPaths = [settingPath for settingPath in locations if os.path.isfile(os.path.join(settingPath, "mods_registry.json"))]
if (len(settingPaths) > 0):
    print('find Stellaris setting at ', settingPaths[0])
    run(settingPaths[0])
    Mbox('', 'done', 0)
else:
    Mbox('', 'unable to location "mods_registry.json', 0)
