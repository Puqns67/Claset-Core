# -*- coding: utf-8 -*-
"""默认配置相关的内容, 包含最新的版本的版本号与文件, 和老版本之间的差异"""

from . import Accounts, Download, Game, Logs, Mirrors, Paths, Settings

ConfigIDs = [
    "Download", "Paths", "Mirrors", "Settings", "Logs", "Game", "Accounts"
]

ConfigInfos = {
    "Version": {
        "Download": Download.LastVersion,
        "Paths": Paths.LastVersion,
        "Mirrors": Mirrors.LastVersion,
        "Settings": Settings.LastVersion,
        "Logs": Logs.LastVersion,
        "Game": Game.LastVersion,
        "Accounts": Accounts.LastVersion
    },
    "File": {
        "Download": Download.File,
        "Paths": Paths.File,
        "Mirrors": Mirrors.File,
        "Settings": Settings.File,
        "Logs": Logs.File,
        "Game": Game.File,
        "Accounts": Accounts.File
    }, 
    "Difference": {
        "Download": Download.Difference,
        "Paths": Paths.Difference,
        "Mirrors": Mirrors.Difference,
        "Settings": Settings.Difference,
        "Logs": Logs.Difference,
        "Game": Game.Difference,
        "Accounts": Accounts.Difference
    },
    "Path": {
        "Download": "Download.json",
        "Paths": "Paths.json",
        "Mirrors": "Mirrors.json",
        "Settings": "Settings.json",
        "Logs": "Logs.json",
        "Game": "$NONGLOBAL$",
        "Accounts": "Accounts.json"
    }
}


def changeConfObject(Name: str, Version: int, File: dict, Difference: dict, Path: str) -> None:
    if Name not in ConfigIDs: ConfigIDs.append(Name)
    ConfigInfos["Version"][Name] = Version
    ConfigInfos["File"][Name] = File
    ConfigInfos["Difference"][Name] = Difference
    ConfigInfos["Path"][Name] = Path


__all__ = [
    "ConfigIDs", "ConfigInfos", "changeConfigObject"
]

