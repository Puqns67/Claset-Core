# -*- coding: utf-8 -*-
"""默认配置相关的内容, 包含最新的版本的版本号与文件, 和老版本之间的差异"""

from . import Paths
from . import Download
from . import Mirrors
from . import Settings
from . import Logs
from . import Game

ConfigIDs = {
    "Paths": "Paths.json",
    "Download": "Download.json",
    "Mirrors": "Mirrors.json",
    "Settings": "Settings.json",
    "Logs": "Logs.json",
    "Game": "$NONGLOBAL"
}

ConfigInfos = {
    "Version": {
        "Download": Download.LastVersion,
        "Paths": Paths.LastVersion,
        "Mirrors": Mirrors.LastVersion,
        "Settings": Settings.LastVersion,
        "Logs": Logs.LastVersion
    },
    "File": {
        "Download": Download.File,
        "Paths": Paths.File,
        "Mirrors": Mirrors.File,
        "Settings": Settings.File,
        "Logs": Logs.File
    },
    "Difference": {
        "Download": Download.Difference,
        "Paths": Paths.Difference,
        "Mirrors": Mirrors.Difference,
        "Settings": Settings.Difference,
        "Logs": Logs.Difference
    }
}

del(Download)
del(Paths)
del(Mirrors)
del(Settings)

__all__ = [
    "ConfigIDs", "ConfigInfos"
]

