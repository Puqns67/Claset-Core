# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from logging import getLogger
from os.path import basename as baseName

from Claset.Utils import AdvancedPath, DownloadTask, path, pathAdder

from .Others import ResolveRule, getNativesObject
from .Exceptions import TargetVersionNotFound

Logger = getLogger(__name__)


def Versionmanifest_VersionList(InitFile: dict, Recommend: str | None = None) -> list[str]:
    if Recommend != None: return(InitFile["Latest"][Recommend])
    OutputList = list()
    for Version in InitFile["versions"]: OutputList.append(Version["id"])
    return(OutputList)


def VersionManifest_To_Version(InitFile: dict, TargetVersion: str | None) -> DownloadTask:
    """从 VersionManifest Json 提取 Version Json 的相关信息并转化为 DownloadManager Task"""
    if TargetVersion == None:
        TargetVersion = InitFile["latest"]["release"]

    for Version in InitFile["versions"]:
        if Version["id"] == TargetVersion:
            return(DownloadTask(
                URL = Version["url"],
                OutputPath = path("$MCVersion", IsPath=True),
                FileName = baseName(Version["url"]),
                Overwrite = False
            ))

    raise TargetVersionNotFound(TargetVersion)


def Version_Client_DownloadList(InitFile: dict, Name: str, Types: dict = dict()) -> list[DownloadTask]:
    Tasks = list()

    # Client
    Client = InitFile["downloads"]["client"]
    Tasks.append(DownloadTask(
        URL = Client["url"],
        Size = Client["size"],
        Sha1 = Client["sha1"],
        OutputPaths = pathAdder("$VERSION", Name, Name + ".jar"),
        Overwrite = False
    ))

    # Libraries
    for Libraries in InitFile["libraries"]:
        if "rules" in Libraries.keys():
            if ResolveRule(Items=Libraries["rules"], Features=Types) == False: continue

        Natives = getNativesObject(Libraries=Libraries, Features=Types)
        if Natives != None:
            Tasks.append(DownloadTask(
                URL = Natives["url"],
                Size = Natives["size"],
                Sha1 = Natives["sha1"],
                OutputPaths = pathAdder("$LIBRERIES/", Natives["path"]),
                Overwrite = False,
                FileName = None
            ))

        try:
            Artifact = Libraries["downloads"]["artifact"]
            Tasks.append(DownloadTask(
                URL = Artifact["url"],
                Size = Artifact["size"],
                Sha1 = Artifact["sha1"],
                OutputPaths = pathAdder("$LIBRERIES/", Artifact["path"]),
                Overwrite = False,
                FileName = None
            ))
        except KeyError: pass

    # Log4j2 config
    Log4j2Config = getLog4j2Infos(InitFile=InitFile, Type="DownloadTask")
    if Log4j2Config != None:
        Tasks.append(Log4j2Config)

    return(Tasks)


def Version_Server_DownloadList(InitFile: dict, SaveTo: str) -> list[DownloadTask]:
    """从 Version 获取对应的 Server jar 下载列表"""
    Server = InitFile["downloads"]["server"]
    return([DownloadTask(
        URL = Server["url"],
        Sha1 = Server["sha1"],
        Size = Server["size"],
        OutputPath = path(SaveTo, IsPath=True),
        Overwrite = False
    )])


def Version_To_AssetIndex(InitFile: dict) -> DownloadTask:
    """从 Version Json 提取 AssetIndex Json 的相关信息并转化为 DownloadManager Task"""
    assetIndex = InitFile["assetIndex"]
    return(DownloadTask(
        URL = assetIndex["url"],
        Sha1 = assetIndex["sha1"],
        Size = assetIndex["size"],
        OutputPath = path("$MCAssetIndex", IsPath=True),
        FileName = baseName(assetIndex["url"]),
        Overwrite = False
    ))


def AssetIndex_DownloadList(InitFile: dict) -> list[DownloadTask]:
    Objects = InitFile["objects"]
    Tasks: list[DownloadTask] = list()
    Pather = AdvancedPath(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])

    for i in Objects:
        Tasks.append(DownloadTask(
            FileName = Objects[i]["hash"],
            URL = Pather.path("$Assets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"]),
            Size = Objects[i]["size"],
            OutputPath = pathAdder("$ASSETS/objects", Objects[i]["hash"][:2]),
            Sha1 = Objects[i]["hash"],
            Overwrite = False,
            Retry = 3,
            ConnectTimeout = 3,
            ReadTimeout = 15
        ))

    return(Tasks)


def getClassPath(VersionJson: dict, VersionJarPath: str, Features: dict | None = None) -> str:
    Output = str()
    for Libraries in VersionJson["libraries"]:
        if "rules" in Libraries.keys():
            if ResolveRule(Items=Libraries["rules"], Features=Features) == False: continue
        try: Temp = pathAdder("$LIBRERIES/", Libraries["downloads"]["artifact"]["path"])
        except KeyError: pass
        if Temp not in Output:
            Output += Temp + ";"
    Output += VersionJarPath
    return(Output)


def getLog4j2Infos(InitFile: dict, Type: str, Platform: str | None = None) -> DownloadTask | str | None:
    if Platform == None:
        Platform = "client"

    try:
        Target = InitFile["logging"][Platform]
    except KeyError:
        return None

    FilePath = pathAdder("$ASSETS", "log_configs", Target["file"]["id"])

    match Type:
        case "DownloadTask":
            return(DownloadTask(
                URL = Target["file"]["url"],
                Size = Target["file"]["size"],
                Sha1 = Target["file"]["sha1"],
                OutputPaths = FilePath,
                Overwrite = False
            ))
        case "Argument":
            return(Target["argument"].replace("${path}", FilePath))

