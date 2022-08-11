# -*- coding: utf-8 -*-
"""解析游戏 Json"""

from logging import getLogger
from os.path import basename as baseName

from Claset.Utils import AdvancedPath, DownloadTask, System, formatDollar

from .Others import Pather, ResolveRule, getNativesObject, parseLibraryName
from .Exceptions import TargetVersionNotFound

__all__ = (
    "Versionmanifest_VersionList",
    "VersionManifest_To_Version",
    "Version_Client_DownloadTasks",
    "Version_Server_DownloadTasks",
    "Version_To_AssetIndex",
    "AssetIndex_DownloadTasks",
    "getClassPath",
    "getLog4j2Infos",
)
Logger = getLogger(__name__)


def Versionmanifest_VersionList(InitFile: dict, Recommend: str | None = None) -> list[str]:
    if Recommend is not None:
        return InitFile["Latest"][Recommend]
    OutputList = list()
    for Version in InitFile["versions"]:
        OutputList.append(Version["id"])
    return OutputList


def VersionManifest_To_Version(InitFile: dict, TargetVersion: str | None) -> DownloadTask:
    """从 VersionManifest Json 提取 Version Json 的相关信息并转化为 DownloadManager Task"""
    if TargetVersion is None:
        TargetVersion = InitFile["latest"]["release"]

    for Version in InitFile["versions"]:
        if Version["id"] == TargetVersion:
            return DownloadTask(
                URL=Version["url"],
                OutputPath=Pather.path("$MCVersionCache", IsPath=True),
                FileName=baseName(Version["url"]),
                Overwrite=False,
            )

    raise TargetVersionNotFound(TargetVersion)


def Version_Client_DownloadTasks(
    InitFile: dict, Name: str, Types: dict = dict()
) -> list[DownloadTask]:
    Tasks = list()

    # Client
    try:
        Client = InitFile["downloads"]["client"]
        Tasks.append(
            DownloadTask(
                URL=Client["url"],
                Size=Client["size"],
                Sha1=Client["sha1"],
                OutputPaths=Pather.pathAdder("$VERSION", Name, Name + ".jar"),
                Overwrite=False,
            )
        )
    except KeyError:
        pass

    # Libraries
    for Libraries in InitFile["libraries"]:
        if "rules" in Libraries:
            if ResolveRule(Items=Libraries["rules"], Features=Types) == False:
                continue

        Natives = getNativesObject(Libraries=Libraries, Features=Types)
        if Natives is not None:
            Tasks.append(
                DownloadTask(
                    URL=Natives["url"],
                    Size=Natives["size"],
                    Sha1=Natives["sha1"],
                    OutputPaths=Pather.pathAdder("$LIBRERIES", Natives["path"]),
                    Overwrite=False,
                )
            )

        try:
            Artifact = Libraries["downloads"]["artifact"]
            Tasks.append(
                DownloadTask(
                    URL=Artifact["url"],
                    Size=Artifact["size"],
                    Sha1=Artifact["sha1"],
                    OutputPaths=Pather.pathAdder("$LIBRERIES", Artifact["path"]),
                    Overwrite=False,
                )
            )
        except KeyError:
            pass

    # Log4j2 config
    Log4j2Config = getLog4j2Infos(InitFile=InitFile, Type="DownloadTask")
    if Log4j2Config is not None:
        Tasks.append(Log4j2Config)

    return Tasks


def Version_Server_DownloadTasks(InitFile: dict, SaveTo: str) -> list[DownloadTask]:
    """从 Version 获取对应的 Server jar 下载列表"""
    Server = InitFile["downloads"]["server"]
    return [
        DownloadTask(
            URL=Server["url"],
            Sha1=Server["sha1"],
            Size=Server["size"],
            OutputPath=Pather.path(SaveTo, IsPath=True),
            Overwrite=False,
        )
    ]


def Version_To_AssetIndex(InitFile: dict) -> DownloadTask:
    """从 Version Json 提取 AssetIndex Json 的相关信息并转化为 DownloadManager Task"""
    assetIndex = InitFile["assetIndex"]
    return DownloadTask(
        URL=assetIndex["url"],
        Sha1=assetIndex["sha1"],
        Size=assetIndex["size"],
        OutputPath=Pather.path("$MCAssetIndexCache", IsPath=True),
        FileName=baseName(assetIndex["url"]),
        Overwrite=False,
    )


def AssetIndex_DownloadTasks(InitFile: dict) -> list[DownloadTask]:
    Objects = InitFile["objects"]
    Tasks: list[DownloadTask] = list()
    Pather = AdvancedPath(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])

    for i in Objects:
        Tasks.append(
            DownloadTask(
                FileName=Objects[i]["hash"],
                URL=Pather.path(
                    "$Assets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"]
                ),
                Size=Objects[i]["size"],
                OutputPath=Pather.pathAdder("$ASSETS/objects", Objects[i]["hash"][:2]),
                Sha1=Objects[i]["hash"],
                Overwrite=False,
                Retry=3,
                ConnectTimeout=3,
                ReadTimeout=15,
            )
        )

    return Tasks


def getClassPath(VersionJson: dict, VersionJarPath: str, Features: dict | None = None) -> str:
    Output = str()
    splitBy = System().get(Format={"Windows": ";", "Other": ":"})
    for Libraries in VersionJson["libraries"]:
        if "rules" in Libraries:
            if ResolveRule(Items=Libraries["rules"], Features=Features) == False:
                continue
        LibraryFullPath = parseLibraryName(Libraries["name"])
        if LibraryFullPath not in Output:
            Output += LibraryFullPath + splitBy
    Output += VersionJarPath
    return Output


def getLog4j2Infos(
    InitFile: dict, Type: str, Platform: str | None = None
) -> DownloadTask | str | None:
    if Platform is None:
        Platform = "client"

    try:
        Target = InitFile["logging"][Platform]
    except KeyError:
        return None

    FilePath = Pather.pathAdder("$ASSETS", "log_configs", Target["file"]["id"])

    match Type:
        case "DownloadTask":
            try:
                return DownloadTask(
                    URL=Target["file"]["url"],
                    Size=Target["file"]["size"],
                    Sha1=Target["file"]["sha1"],
                    OutputPaths=FilePath,
                    Overwrite=False,
                )
            except KeyError:
                return None
        case "Argument":
            return formatDollar(Target["argument"], path=FilePath)
        case _:
            raise ValueError(Type)
