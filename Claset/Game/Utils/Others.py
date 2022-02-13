# -*- coding: utf-8 -*-

from platform import system, machine, version
from re import match

from Claset.Utils import AdvancedPath, DownloadTask

from .Exceptions import UnsupportSystemHost, FeaturesContinue, FeaturesMissingKey


def getVersionManifestTask(Ver: int = 1, Path: str | None = None) -> DownloadTask:
    """获取对应版本的 Manifest URL"""
    APath = AdvancedPath(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])
    match Ver:
        case 1:
            FileName = "version_manifest.json"
            URL = APath.path("$LauncherMeta/mc/game/version_manifest.json")
        case 2:
            FileName = "version_manifest_v2.json"
            URL = APath.path("$LauncherMeta/mc/game/version_manifest_v2.json")
        case _:
            raise ValueError("Unknown Ver")
    if Path == None: Path = "$MCVersionManifest/"
    return(DownloadTask(URL=URL, OutputPaths=APath.pathAdder(Path, FileName)))


def ResolveRule(Items: list[dict], Features: dict | None = dict()) -> bool:
    """规则匹配"""
    allow = False
    if Features == None: Features = dict()
    for Item in Items:
        if Item.get("os") != None:
            if Item["os"].get("name") != None:
                SystemHost = {"windows": "windows", "darwin": "osx", "linux": "linux", "java": "java", "": None}[system().lower()]
                if SystemHost in ("java", None): raise UnsupportSystemHost(SystemHost)
                if Item["os"]["name"] != SystemHost: continue
            if Item["os"].get("arch") != None:
                if Item["os"]["arch"] != {"amd64": "x64", "x86_64": "x64", "x64": "x64", "i386": "x86", "x86": "x86", "i686": "x86"}[machine().lower()]: continue
            if Item["os"].get("version") != None:
                if match(Item["os"]["version"], version()) == None: continue
        if Item.get("features") != None:
            try:
                for FeaturesKey in Item["features"].keys():
                    if FeaturesKey in Features.keys():
                        if Features[FeaturesKey] != Item["features"][FeaturesKey]: raise FeaturesContinue
                    else: raise FeaturesMissingKey(FeaturesKey)
            except FeaturesContinue: continue
        allow = {"allow": True, "disallow": False, None: None}[Item.get("action")]
        if allow == None: raise UnsupportSystemHost
    return(allow)


def getNativesObject(Libraries: dict, Features: dict | None = None, getExtract: bool = False) -> dict | None:
    # 判断是否需要输出
    LibrariesKeys = Libraries.keys()
    if not ("natives" in LibrariesKeys): return(None)
    if "rules" in LibrariesKeys:
        if ResolveRule(Items=Libraries["rules"], Features=Features) == False: return(None)

    # 解析系统信息
    SystemHost = {"Windows": "windows", "Darwin": "osx", "Linux": "linux", "Java": "java", "": None}[system()]
    if SystemHost in ("java", None): raise UnsupportSystemHost(SystemHost)
    Output = Libraries["downloads"]["classifiers"][Libraries["natives"][SystemHost]]

    # 实现 getExtract
    if (getExtract and ("extract" in LibrariesKeys)):
        Output["Extract"] = Libraries["extract"]
    else: Output["Extract"] = dict()

    return(Output)

