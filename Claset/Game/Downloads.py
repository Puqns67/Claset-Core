#VERSION=0
#
#Claset/Game/Download.py
#下载游戏
#

from Claset.Base.AdvancedPath import path as APathmd

def getVersionManifest(Downloader, ver: int = 1):
    Real_URL = str()
    if ver == 1:
        Real_URL = "$LauncherMeta/mc/game/version_manifest.json"
    elif ver == 2:
        Real_URL = "$LauncherMeta/mc/game/version_manifest_v2.json"
    apath = APathmd(Others=True, OtherTypes=[["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<1>", "&F<$EXEC/Configs/Settings.json>&V<DownloadServer>"]])
    URL = apath.path(Real_URL)
    Path = APathmd("$MCVersionManifest/")
    print(URL, Path)
    return(Downloader.add({"URL": URL, "OutputPath": Path, "Retry": 3}))

