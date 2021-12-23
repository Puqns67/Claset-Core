# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from logging import getLogger
from re import match
from platform import system, machine, version
from os.path import basename as baseName

from Claset.Utils.AdvancedPath import path as aPathmd

from .Exceptions import LoadJson as Ex_LoadJson

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
    raise Ex_LoadJson.TargetVersionNotFound(TargetVersion)


def Version_Client_DownloadList(InitFile: dict, Name: str, Types: dict = dict()) -> list[dict]:
    Tasks = list()

    # Client
    Client = InitFile["downloads"]["client"]
    Tasks.append({
        "URL": Client["url"],
        "Sha1": Client["sha1"],
        "Size": Client["size"],
        "OutputPaths": aPathmd().path("$VERSION/" + Name + "/" + Name + ".jar", IsPath=True),
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
        "OutputPath": aPathmd().path(SaveTo, IsPath=True),
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
    Pather = aPathmd(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])

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


def ResolveRule(Items: list[dict], Features: dict | None = dict()) -> bool:
    """规则匹配"""
    allow = False
    if Features == None: Features = dict()
    for Item in Items:
        if Item.get("os") != None:
            if Item["os"].get("name") != None:
                SystemHost = {"Windows": "windows", "Darwin": "osx", "Linux": "linux", "Java": "java", "": None}[system()]
                if SystemHost in ("java", None): raise Ex_LoadJson.UnsupportSystemHost(SystemHost)
                if Item["os"]["name"] != SystemHost: continue
            if Item["os"].get("arch") != None:
                if Item["os"]["arch"] != {"AMD64": "x64", "X64": "x64", "i386": "x86", "X86": "x86", "i686": "x86"}[machine()]: continue
            if Item["os"].get("version") != None:
                if match(Item["os"]["version"], version()) == None: continue
        if Item.get("features") != None:
            try:
                for FeaturesKey in Item["features"].keys():
                    if FeaturesKey in Features.keys():
                        if Features[FeaturesKey] != Item["features"][FeaturesKey]: raise Ex_LoadJson.FeaturesContinue
                    else: raise Ex_LoadJson.FeaturesMissingKey(FeaturesKey)
            except Ex_LoadJson.FeaturesContinue: continue
        allow = {"allow": True, "disallow": False, None: None}[Item.get("action")]
        if allow == None: raise Ex_LoadJson.UnsupportSystemHost
    return(allow)


def getNativesObject(Libraries: dict, Features: dict | None = None, getExtract: bool = False) -> dict | None:
    # 判断是否需要输出
    LibrariesKeys = Libraries.keys()
    if not ("natives" in LibrariesKeys): return(None)
    if "rules" in LibrariesKeys:
        if ResolveRule(Items=Libraries["rules"], Features=Features) == False: return(None)

    # 解析系统信息
    SystemHost = {"Windows": "windows", "Darwin": "osx", "Linux": "linux", "Java": "java", "": None}[system()]
    if SystemHost in ("java", None): raise Ex_LoadJson.UnsupportSystemHost(SystemHost)
    Output = Libraries["downloads"]["classifiers"][Libraries["natives"][SystemHost]]

    # 实现 getExtract
    if (getExtract and ("extract" in LibrariesKeys)):
        Output["Extract"] = Libraries["extract"]
    else: Output["Extract"] = dict()

    return(Output)

