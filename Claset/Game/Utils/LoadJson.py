# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from logging import getLogger
from os.path import basename as baseName

from Claset.Utils import AdvancedPath

from .Others import ResolveRule, getNativesObject
from .Exceptions import TargetVersionNotFound

Logger = getLogger(__name__)


def Versionmanifest_VersionList(InitFile: dict, Recommend: str | None = None) -> list[str]:
    if Recommend != None: return(InitFile["Latest"][Recommend])
    OutputList = list()
    for Version in InitFile["versions"]: OutputList.append(Version["id"])
    return(OutputList)


def VersionManifest_To_Version(InitFile: dict, TargetVersion: str) -> dict:
    """从 VersionManifest Json 提取 Version Json 的相关信息并转化为 DownloadManager Task"""
    for Version in InitFile["versions"]:
        if Version["id"] == TargetVersion:
            return({
                "URL": Version["url"],
                "OutputPath": "$MCVersion",
                "FileName": baseName(Version["url"]),
                "Overwrite": False,
            })
    raise TargetVersionNotFound(TargetVersion)


def Version_Client_DownloadList(InitFile: dict, Name: str, Types: dict = dict()) -> list[dict]:
    Tasks = list()

    # Client
    Client = InitFile["downloads"]["client"]
    Tasks.append({
        "URL": Client["url"],
        "Sha1": Client["sha1"],
        "Size": Client["size"],
        "OutputPaths": AdvancedPath().path("$VERSION/" + Name + "/" + Name + ".jar", IsPath=True),
        "Overwrite": False
    })

    # Libraries
    for Libraries in InitFile["libraries"]:
        if "rules" in Libraries.keys():
            if ResolveRule(Items=Libraries["rules"], Features=Types) == False: continue

        Natives = getNativesObject(Libraries=Libraries, Features=Types)
        if Natives != None:
            Tasks.append({
                "URL": Natives["url"],
                "Size": Natives["size"],
                "Sha1": Natives["sha1"],
                "OutputPath": "$LIBRERIES/" + Natives["path"],
                "Overwrite": False,
                "FileName": None
            })

        try:
            Artifact = Libraries["downloads"]["artifact"]
            Tasks.append({
                "URL": Artifact["url"],
                "Size": Artifact["size"],
                "Sha1": Artifact["sha1"],
                "OutputPath": "$LIBRERIES/" + Artifact["path"],
                "Overwrite": False,
                "FileName": None
            })
        except KeyError: pass

    return(Tasks)


def Version_Server_DownloadList(InitFile: dict, SaveTo: str) -> list[dict]:
    """从 Version 获取对应的 Server jar 下载列表"""
    Server = InitFile["downloads"]["server"]
    return([{
        "URL": Server["url"],
        "Sha1": Server["sha1"],
        "Size": Server["size"],
        "OutputPath": AdvancedPath().path(SaveTo, IsPath=True),
        "Overwrite": False
    }])


def Version_To_AssetIndex(InitFile: dict) -> dict:
    """从 Version Json 提取 AssetIndex Json 的相关信息并转化为 DownloadManager Task"""
    assetIndex = InitFile["assetIndex"]
    return({
        "URL": assetIndex["url"],
        "Sha1": assetIndex["sha1"],
        "Size": assetIndex["size"],
        "OutputPath": "$MCAssetIndex",
        "FileName": baseName(assetIndex["url"]),
        "Overwrite": False
    })


def AssetIndex_DownloadList(InitFile: dict) -> list[dict]:
    Objects = InitFile["objects"]
    Tasks = list()
    Pather = AdvancedPath(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])

    for i in Objects:
        Tasks.append({
            "FileName": Objects[i]["hash"],
            "URL": Pather.path("$Assets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"]),
            "Size": Objects[i]["size"],
            "OutputPath": "$ASSETS/objects/" + Objects[i]["hash"][:2],
            "Sha1": Objects[i]["hash"],
            "Overwrite": False,
            "Retry": 3,
            "ConnectTimeout": 3,
            "ReadTimeout": 15
        })

    return(Tasks)

