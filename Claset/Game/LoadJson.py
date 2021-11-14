# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from logging import getLogger
from re import match
from platform import system, machine, version
from zipfile import ZipFile, is_zipfile

from Claset.Base.AdvancedPath import path as aPathmd

from .Exceptions import LoadJson as Ex_LoadJson

Logger = getLogger(__name__)


def Versionmanifest_VersionList(InitFile: dict, Recommend: str | None = None) -> list[str]:
    if Recommend != None: return(InitFile["Latest"][Recommend])
    OutputList = list()
    for Version in InitFile["versions"]: OutputList.append(Version["id"])
    return(OutputList)


def VersionManifest_To_Version(InitFile: dict, TargetVersion: str) -> list[dict]:
    for Version in InitFile["versions"]:
        if Version["id"] == TargetVersion:
            return([{
                "URL": Version["url"],
                "OutputPath": "$MCVersion",
                "Sha1": Version["sha1"],
                "Overwrite": False,
            }])
    raise Ex_LoadJson.TargetVersionNotFound(TargetVersion)


def Version_Client_DownloadList(InitFile: dict, Name: str, Types: dict = dict()) -> list[dict]:
    Tasks = list()

    # Client
    Client = InitFile["downloads"]["client"]
    Tasks.append({
        "URL": Client["url"],
        "Sha1": Client["sha1"],
        "Size": Client["size"],
        "OutputPaths": aPathmd().path("$VERSION/" + Name + "/" + Name + ".jar"),
        "Overwrite": False
    })

    # Libraries
    for Libraries in InitFile["libraries"]:
        LibrariesKeys = Libraries.keys()

        if "rules" in LibrariesKeys:
            if ResolveRules(Items=Libraries["rules"], Features=Types) == False: continue

        if "natives" in LibrariesKeys:
            try:
                SystemHost = {"Windows": "windows", "Darwin": "osx", "Linux": "linux", "Java": "java", "": None}[system()]
                if SystemHost in ("java", None): raise Ex_LoadJson.UnsupportSystemHost(SystemHost)
                Classifiers = Libraries["downloads"]["classifiers"][Libraries["natives"][SystemHost]]
                Tasks.append({
                    "URL": Classifiers["url"],
                    "Size": Classifiers["size"],
                    "Sha1": Classifiers["sha1"],
                    "OutputPath": "$LIBRERIES/" + Classifiers["path"],
                    "Overwrite": False,
                    "FileName": None,
                    "Next": ProcessClassifiers,
                    "NextArgs": {
                        "ExtractTo": aPathmd().path("$VERSION/" + Name + "/natives", IsPath=True)
                    }
                })
            except KeyError: pass

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
        "OutputPath": aPathmd().path(SaveTo),
        "Overwrite": False
    }])


def Version_RunCodeList(InitFile: dict) -> list[str]:
    pass


def Version_To_AssetIndex(InitFile: dict) -> list[dict]:
    assetIndex = InitFile["assetIndex"]
    return([{
        "URL": assetIndex["url"],
        "Sha1": assetIndex["sha1"],
        "Size": assetIndex["size"],
        "OutputPath": "$MCAssetIndex",
        "Overwrite": False
    }])


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


def ProcessClassifiers(Task: dict):
    """处理 Classifiers"""
    if not(is_zipfile(Task["OutputPaths"])): raise Ex_LoadJson.ClassifiersFileError
    Logger.info("Extract Classifiers: %s", Task["FileName"])
    File = ZipFile(file=Task["OutputPaths"], mode="r")
    FileList = File.namelist()
    for FilePathInZip in FileList:
        if "META-INF" in FilePathInZip: continue
        File.extract(FilePathInZip, Task["NextArgs"]["ExtractTo"])

