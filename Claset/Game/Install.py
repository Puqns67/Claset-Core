# -*- coding: utf-8 -*-
"""下载游戏"""

from os.path import abspath

from Claset.Base.AdvancedPath import path as aPathmd


# 下载游戏
def InstallGame(Name: str, Version: str, Forge: str | None = None, Fabric: str | None = None):
    pass


# 获取 Manifest 的 URL
def getVersionManifestURL(Ver: int = 1):
    match Ver:
        case 1:
            FileName = "version_manifest.json"
            URL = "$LauncherMeta/mc/game/version_manifest.json"
        case 2:
            FileName = "version_manifest_v2.json"
            URL = "$LauncherMeta/mc/game/version_manifest_v2.json"
        case _:
            raise TypeError("getVersionManifestURL(): Unknown Type")
    APath = aPathmd(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])
    URL = APath.path(URL)
    Path = APath.path("$MCVersionManifest/", IsPath=True)
    return({"URL": URL, "FileName": FileName, "OutputPath": Path})

