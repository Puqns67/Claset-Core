# VERSION=5
#
# Claset/Game/LoadJson.py
# 用于解析游戏Json
#

from re import match
from platform import system, machine, version

from Claset.Base.File import loadFile

from .Exceptions import LoadJson as Ex_LoadJson


def getDL_AssetsIndex(InitFile: str) -> list:
    Objects = InitFile["objects"]
    Tasks = list()

    for i in Objects:
        Tasks.append({
            "FileName": Objects[i]["hash"],
            "URL": "$Assets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"],
            "Size": Objects[i]["size"],
            "OutputPath": "$ASSETS/objects/" + Objects[i]["hash"][:2],
            "Overwrite": False,
            "Retry": 3,
            "OtherURL": "$OfficialAssets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"],
            "Sha1": Objects[i]["hash"],
            "ConnectTimeout": 3,
            "ReadTimeout": 15
        })

    return(Tasks)


def ResolveRules(Items: list, Features: dict = dict()) -> bool:
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
            for FeaturesKey in Item["features"].keys():
                if FeaturesKey in Features.keys():
                    if Features[FeaturesKey] != Item["features"][FeaturesKey]: continue
                else: raise Ex_LoadJson.FeaturesMissingKey(FeaturesKey)
        allow = {"allow": True, "disallow": False, None: None}[Item.get("action")]
        if allow == None: raise SystemError
    return(allow)


def getDL_Version():
    pass
