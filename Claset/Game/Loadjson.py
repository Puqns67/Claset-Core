# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from re import I, match
from platform import system, machine, version

from Claset.Base.AdvancedPath import path as aPathmd

from .Exceptions import LoadJson as Ex_LoadJson


def VersionManifest_DownloadList(InitFile: dict, TargetVersion: str) -> list[dict]:
    for Version in InitFile["versions"]:
        if Version["id"] == TargetVersion:
            return([{
                "URL": Version["url"],
                "OutputPath": "$MCVersion",
                "Sha1": Version["sha1"],
                "Overwrite": False,
            }])
    raise Ex_LoadJson.TargetVersionNotFound(TargetVersion)


def Version_DownloadList_WIP(InitFile: dict, Types: dict = dict()) -> list[dict]:
    # 暂不支持 natives classifiers
    Tasks = list()
    for Libraries in InitFile["libraries"]:
        LibrariesKeys = Libraries.keys()
        if "rules" in LibrariesKeys:
            if ResolveRules(Items=Libraries["rules"], Features=Types) == False: continue
        Tasks.append(Libraries["name"])

    return(Tasks)


def Version_getRunCodeList(InitFile: dict):
    pass


def AssetsIndex_DownloadList(InitFile: dict) -> list[dict]:
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


def ResolveRules(Items: list[dict], Features: dict = dict()) -> bool:
    """匹配规则"""
    allow = False
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
        if allow == None: raise SystemError
    return(allow)

