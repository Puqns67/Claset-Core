# -*- coding: utf-8 -*-
"""默认配置相关的内容, 包含最新的版本的版本号与文件, 和老版本之间的差异"""

from . import Download, Game, Logs, Mirrors, Paths, Settings, User

ConfigIDs = {
    "Paths": "Paths.json",
    "Download": "Download.json",
    "Mirrors": "Mirrors.json",
    "Settings": "Settings.json",
    "Logs": "Logs.json",
    "Game": "$NONGLOBAL$",
    "Users": "Users.json"
}

ConfigInfos = {
    "Version": {
        "Download": Download.LastVersion,
        "Paths": Paths.LastVersion,
        "Mirrors": Mirrors.LastVersion,
        "Settings": Settings.LastVersion,
        "Logs": Logs.LastVersion,
        "Game": Game.LastVersion,
        "Users": User.LastVersion
    },
    "File": {
        "Download": Download.File,
        "Paths": Paths.File,
        "Mirrors": Mirrors.File,
        "Settings": Settings.File,
        "Logs": Logs.File,
        "Game": Game.File,
        "Users": User.File
    },
    "Difference": {
        "Download": Download.Difference,
        "Paths": Paths.Difference,
        "Mirrors": Mirrors.Difference,
        "Settings": Settings.Difference,
        "Logs": Logs.Difference,
        "Game": Game.Difference,
        "Users": User.Difference
    }
}

__all__ = [
    "ConfigIDs", "ConfigInfos"
]

