# -*- coding: utf-8 -*-

from hashlib import sha1

from Claset.Utils import (
    AdvancedPath,
    DownloadTask,
    System,
    Arch,
    formatPlatform,
    formatDollar,
    dfCheck,
    removeDir,
    path,
    OriginalVersion,
)
from Claset.Utils.Exceptions.Claset import Continue

from .Exceptions import (
    UnsupportSystemHost,
    FeaturesMissingKey,
    TargetVersionNotFound,
)

__all__ = (
    "getVersionManifestTask",
    "ResolveRule",
    "getNativesObject",
    "removeGame",
    "genNativeDirName",
    "parseLibraryName",
)

Pather = AdvancedPath(
    Others=[
        {
            "MCVersionCache": "$CACHE/MCVersionJson",
            "MCAssetIndexCache": "$ASSETS/indexes",
            "MCVersionManifestCache": "$CACHE",
        },
        "&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>",
    ]
)


def getVersionManifestTask(Ver: int = 1, Path: str | None = None) -> DownloadTask:
    """获取对应版本的 Manifest URL"""
    match Ver:
        case 1:
            FileName = "version_manifest.json"
            URL = Pather.path("$LauncherMeta/mc/game/version_manifest.json")
        case 2:
            FileName = "version_manifest_v2.json"
            URL = Pather.path("$LauncherMeta/mc/game/version_manifest_v2.json")
        case _:
            raise ValueError("Unknown Ver")
    return DownloadTask(
        URL=URL,
        OutputPaths=Pather.pathAdder(Path or "$MCVersionManifestCache", FileName),
    )


def ResolveRule(Items: list[dict], Features: dict | None = dict()) -> bool:
    """规则匹配"""
    allow = False
    if Features is None:
        Features = dict()
    for Item in Items:
        if Item.get("os") is not None:
            if Item["os"].get("name") is not None:
                if Item["os"]["name"] != System().get(Format="Minecraft"):
                    continue
            if Item["os"].get("arch") is not None:
                if Item["os"]["arch"] != Arch().get(Format="Minecraft"):
                    continue
            if Item["os"].get("version") is not None:
                if Item["os"]["version"] != OriginalVersion:
                    continue
        if Item.get("features") is not None:
            try:
                for FeaturesKey in Item["features"]:
                    if FeaturesKey in Features:
                        if Features[FeaturesKey] != Item["features"][FeaturesKey]:
                            raise Continue
                    else:
                        raise FeaturesMissingKey(FeaturesKey)
            except Continue:
                continue
        try:
            allow = {"allow": True, "disallow": False}[Item.get("action")]
        except KeyError:
            raise UnsupportSystemHost
    return allow


def getNativesObject(
    Libraries: dict, Features: dict | None = None, getExtract: bool = False
) -> dict | None:
    # 判断是否需要输出
    if "natives" not in Libraries:
        return None
    if "rules" in Libraries:
        if ResolveRule(Items=Libraries["rules"], Features=Features) == False:
            return None

    # 解析系统信息
    Output = Libraries["downloads"]["classifiers"][
        formatDollar(
            Libraries["natives"][System().get(Format="Minecraft")],
            arch=Arch().get(Format="PureNumbers"),
        )
    ]

    # 实现 getExtract
    if getExtract and ("extract" in Libraries):
        Output["Extract"] = Libraries["extract"]
    else:
        Output["Extract"] = dict()

    return Output


def removeGame(Name: str):
    """移除游戏实例"""
    if dfCheck(Path=f"$VERSION\{Name}", Type="d"):
        removeDir(path(f"$VERSION\{Name}", IsPath=True))
    else:
        raise TargetVersionNotFound(Name)


def genNativeDirName(VersionName: str) -> str:
    """生成适用于当前平台的 Native 文件夹名"""
    return f"Temp-Claset-Natives-{sha1(VersionName)}"


def parseLibraryName(Input: str) -> str:
    """解析库名至路径"""
    Splited = Input.split(":")
    LibraryPath, LibraryName, LibraryVersion = Splited[:3]

    if len(Splited) == 4:
        if "@" in Splited[3]:
            FileName, Extension = Splited[3].split("@")
        else:
            FileName = Splited[3]
            Extension = None
    else:
        FileName = None

        if "@" in LibraryVersion:
            LibraryVersion, Extension = LibraryVersion.split("@")
        else:
            Extension = None

    return Pather.pathAdder(
        "$LIBRERIES",
        LibraryPath.split("."),
        f"{LibraryName}/{LibraryVersion}/{LibraryName}-{LibraryVersion}{'-' + FileName if FileName else str()}.{Extension if Extension else 'jar'}",
    )
