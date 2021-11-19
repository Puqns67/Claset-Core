# -*- coding: utf-8 -*-
"""下载游戏"""

from Claset import Downloader as GlobalDownloader
from Claset.Base.Download import DownloadManager
from Claset.Base.AdvancedPath import path as aPathmd, pathAdder
from Claset.Base.File import loadFile

from . import LoadJson

from .Exceptions import Install as Ex_Install, LoadJson as Ex_LoadJson


class Installer():
    """游戏安装器"""
    def __init__(self, Downloader: DownloadManager | None = None):
        if Downloader != None:
            self.Downloader = Downloader
        else: self.Downloader = GlobalDownloader


    def InstallGame(self, Name: str, Version: str, Forge: str | None = None, Fabric: str | None = None):
        """通过游戏版本下载游戏"""
        VersionManifest_Info = getVersionManifestURL()
        MainDownloadProject = self.Downloader.addTask(InputTask=VersionManifest_Info)

        if (self.Downloader.projectJoin(MainDownloadProject) > 0): raise Ex_Install.DownloadError

        # 获取对应版本的 Version json
        try:
            VersionJsonTask = LoadJson.VersionManifest_To_Version(InitFile=loadFile(pathAdder(VersionManifest_Info["OutputPath"], VersionManifest_Info["FileName"]), Type="json"), TargetVersion=Version)
        except Ex_LoadJson.TargetVersionNotFound:
            raise Ex_Install.UnknownVersion
        VersionJsonPath = pathAdder(VersionJsonTask["OutputPath"], VersionJsonTask["FileName"])
        self.Downloader.addTask(InputTask=VersionJsonTask, ProjectID=MainDownloadProject)

        if (self.Downloader.projectJoin(MainDownloadProject) > 0): raise Ex_Install.DownloadError

        VersionJson = loadFile(Path=VersionJsonPath, Type="json")
        del(VersionJsonTask)
        del(VersionJsonPath)

        # 获取对应版本的 AssetIndex json
        AssetIndexJsonTask = LoadJson.Version_To_AssetIndex(InitFile=VersionJson)
        AssetIndexJsonPath = pathAdder(AssetIndexJsonTask["OutputPath"], AssetIndexJsonTask["FileName"])
        self.Downloader.addTask(InputTask=AssetIndexJsonTask, ProjectID=MainDownloadProject)

        if (self.Downloader.projectJoin(MainDownloadProject) > 0): raise Ex_Install.DownloadError

        AssetIndexJson = loadFile(Path=AssetIndexJsonPath, Type="json")
        del(AssetIndexJsonTask)
        del(AssetIndexJsonPath)

        # 解析下载项
        DownloadList = LoadJson.Version_Client_DownloadList(InitFile=VersionJson, Name=Name)
        DownloadList.extend(LoadJson.AssetIndex_DownloadList(InitFile=AssetIndexJson))

        # 下载
        self.Downloader.addTasks(InputTasks=DownloadList, MainProjectID=MainDownloadProject)
        if (self.Downloader.projectJoin(MainDownloadProject) > 0): raise Ex_Install.DownloadError


def getVersionManifestURL(Ver: int = 1, Path: str | None = None) -> dict:
    """获取对应版本的 Manifest URL"""
    match Ver:
        case 1:
            FileName = "version_manifest.json"
            URL = "$LauncherMeta/mc/game/version_manifest.json"
        case 2:
            FileName = "version_manifest_v2.json"
            URL = "$LauncherMeta/mc/game/version_manifest_v2.json"
        case _:
            raise ValueError("getVersionManifestURL(): Unknown Type")
    APath = aPathmd(Others=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>"])
    URL = APath.path(URL)
    if Path == None: Path = APath.path("$MCVersionManifest/", IsPath=True)
    return({"URL": URL, "FileName": FileName, "OutputPath": Path})

