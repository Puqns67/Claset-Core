# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from logging import getLogger
from re import match
from platform import system, machine, version
from zipfile import ZipFile, is_zipfile as isZipFile
from os.path import basename as baseName, splitext as splitExt

from Claset.Base.File import loadFile
from Claset.Base.AdvancedPath import path as aPathmd

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
        LibrariesKeys = Libraries.keys()

        if "rules" in LibrariesKeys:
            if ResolveRules(Items=Libraries["rules"], Features=Types) == False: continue

        if "natives" in LibrariesKeys:
            try:
                SystemHost = {"Windows": "windows", "Darwin": "osx", "Linux": "linux", "Java": "java", "": None}[system()]
                if SystemHost in ("java", None): raise Ex_LoadJson.UnsupportSystemHost(SystemHost)
                Classifiers = Libraries["downloads"]["classifiers"][Libraries["natives"][SystemHost]]
                if "extract" in LibrariesKeys: Extract = Libraries["extract"]
                else: Extract = None
                Tasks.append({
                    "URL": Classifiers["url"],
                    "Size": Classifiers["size"],
                    "Sha1": Classifiers["sha1"],
                    "OutputPath": "$LIBRERIES/" + Classifiers["path"],   
                    "Overwrite": False,
                    "FileName": None,
                    "Next": ProcessClassifiers,
                    "NextArgs": {
                        "ExtractTo": aPathmd().pathAdder("$VERSION/", Name, "/natives"),
                        "Extract": Extract
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
        "OutputPath": aPathmd().path(SaveTo, IsPath=True),
        "Overwrite": False
    }])


def Version_RunCodeList(InitFile: dict) -> list[str]:
    pass


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


def ProcessClassifiers(Task: dict): # 需要对其中的 sha1 文件处理
    """处理 Classifiers"""
    if not(isZipFile(Task["OutputPaths"])): raise Ex_LoadJson.ClassifiersFileError
    Logger.info("Extract Classifiers: %s", Task["FileName"])
    File = ZipFile(file=Task["OutputPaths"], mode="r")
    FileList = File.namelist()

    # 分离 sha1 文件, 并生成 File Sha1 的对应关系, 存入 FileSha1. 生成文件名列表
    FileSha1 = dict()
    FileNameList = list()

    for FilePathInZip in FileList:
        FileNameList.append(baseName(FilePathInZip))

        Name, Ext = splitExt(FilePathInZip)
        print(Name, Ext)
        if Ext == ".sha1":
            Logger.debug("Excluded: \"%s\" From \"%s\" By file extension name", FilePathInZip, baseName(Task["OutputPaths"]))
            FileList.remove(FilePathInZip)

        elif ((Ext == ".sha1") and (Name in FileList)):
            FileList.remove(FilePathInZip)

            # 读取对应的 sha1 值
            Sha1 = loadFile(Path=File.read(FilePathInZip), Type="text")
            if Sha1[-1] == "\n": Sha1 = Sha1.rstrip()

            FileSha1[Name] = Sha1

    for FilePathInZip in FileList:
        if Task["NextArgs"].get("Extract") != None:
            if "exclude" in Task["NextArgs"]["Extract"].keys():
                try:
                    for Exclude in Task["NextArgs"]["Extract"]["exclude"]:
                        if Exclude in FilePathInZip:
                            Logger.debug("Excluded: \"%s\" From \"%s\" By Extract", FilePathInZip, baseName(Task["OutputPaths"]))
                            raise Ex_LoadJson.ClassifiersContinue
                except Ex_LoadJson.ClassifiersContinue: continue

        try:
            File.extract(FilePathInZip, Task["NextArgs"]["ExtractTo"])
        except FileExistsError:
            Logger.warning("Classifiers file Exist: \"%s\" From \"%s\"", FilePathInZip, baseName(Task["OutputPaths"]))

