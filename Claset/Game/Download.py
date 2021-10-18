#VERSION=0
#
#Claset/Game/Download.py
#下载游戏
#

from os.path import abspath

from Claset.Base.AdvancedPath import path as aPath

def getVersionManifestURL(Ver: int = 1):
    match Ver:
        case 1:
            FileName = "version_manifest_v2.json"
            URL = "$LauncherMeta/mc/game/version_manifest_v2.json"
        case 2:
            FileName = "version_manifest_v2.json"
            URL = "$LauncherMeta/mc/game/version_manifest_v2.json"
        case _:
            raise TypeError("getVersionManifestURL(): Unknown Type")
    APath = aPath(Others=True, OtherTypes=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])
    URL = APath.path(URL)
    Path = APath.path("$MCVersionManifest/")
    return({"URL": URL, "FileName": FileName, "OutputPath": abspath(Path), "Retry": 3})

