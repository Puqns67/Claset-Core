#VERSION=0
#
#Claset/Game/Download.py
#下载游戏
#

import Claset.Base.Path as Pathmd
import Claset.Base.AdvancedPath as AdvancedPath

def getVersionManifest(Downloader, ver="v1"):
    RURL = ""
    if ver == "v1":
        RURL = "$LauncherMeta/mc/game/version_manifest.json"
    elif ver == "v2":
        RURL = "$LauncherMeta/mc/game/version_manifest_v2.json"
    apath = AdvancedPath.path(Others=True, OtherTypes=[["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<1>", "&F<$EXEC/Configs/Settings.json>&V<DownloadServer>"]])
    URL = apath.path(RURL)
    Path = Pathmd.path("$MCVersionManifest/")
    print(URL, Path)
    return(Downloader.add({"URL": URL, "OutputPath": Path, "Retry": 3}))

