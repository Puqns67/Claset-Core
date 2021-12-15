# -*- coding: utf-8 -*-
"""下载游戏"""

from logging import getLogger
from re import compile as reCompile

from Claset.Utils.Download import DownloadManager
from Claset.Utils.Path import pathAdder
from Claset.Utils.AdvancedPath import path as aPathmd
from Claset.Utils.File import loadFile, saveFile, dfCheck, moveFile
from Claset.Utils.Configs import Configs

from . import LoadJson

from .Exceptions import Install as Ex_Install, LoadJson as Ex_LoadJson

__all__ = ["GameInstaller", "getVersionManifestURL"]
Logger = getLogger(__name__)


class GameInstaller():
    """
    游戏安装器
    * Name: 游戏版本名
    * Version: 游戏版本号
    * Downloader: 下载器，不定义则使用全局下载器
    """
    def __init__(self, Downloader: DownloadManager, Name: str, Version: str, WaitDownloader: bool = True, UsingDownloadServer: str | None = None):
        self.Downloader = Downloader
        self.Name = Name
        self.Version = Version
        self.WaitDownloader = WaitDownloader

        # 载入相关的配置
        if UsingDownloadServer != None: self.UsingDownloadServer: str = Configs().getConfig(ID="Settings", TargetVersion=0)["DownloadServer"]
        else: self.UsingDownloadServer = UsingDownloadServer

        if self.UsingDownloadServer == "Vanilla": self.Mirrors = Configs().getConfig(ID="Mirrors", TargetVersion=0)
        else: self.Mirrors = None

        # 开始安装
        self.InstallVanilla()

        # 更新版本 Json
        self.updateVersionJson()


    def InstallVanilla(self):
        """下载并安装游戏"""
        Logger.info("Start installation \"%s\" from Vanilla Verison \"%s\"", self.Name, self.Version)
        VersionManifest_Info = getVersionManifestURL()
        self.MainDownloadProject = self.Downloader.addTask(InputTask=VersionManifest_Info)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise Ex_Install.DownloadError

        self.getVersionJson(VersionManifest_Info)
        self.getAssetIndexJson()

        # 解析下载项
        DownloadList = LoadJson.Version_Client_DownloadList(InitFile=self.VersionJson, Name=self.Name)
        DownloadList.extend(LoadJson.AssetIndex_DownloadList(InitFile=self.AssetIndexJson))

        # 下载
        Logger.info("Downloading Minecraft Vanilla Verison \"%s\", from mirror \"%s\"", self.Name, self.Version)
        self.Downloader.addTasks(InputTasks=DownloadList, MainProjectID=self.MainDownloadProject)
        if ((self.WaitDownloader == True) and (self.Downloader.projectJoin(self.MainDownloadProject) > 0)): raise Ex_Install.DownloadError


    def getVersionJson(self, VersionManifest_Info: dict):
        """获取对应版本的 Version json"""
        try:
            VersionJsonTask = LoadJson.VersionManifest_To_Version(InitFile=loadFile(pathAdder(VersionManifest_Info["OutputPath"], VersionManifest_Info["FileName"]), Type="json"), TargetVersion=self.Version)
        except Ex_LoadJson.TargetVersionNotFound:
            raise Ex_Install.UnknownVersion

        OldVersionJsonPath = pathAdder(VersionJsonTask["OutputPath"], VersionJsonTask["FileName"])
        self.Downloader.addTask(InputTask=VersionJsonTask, ProjectID=self.MainDownloadProject)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise Ex_Install.DownloadError

        self.VersionJsonPath = aPathmd().pathAdder("$VERSION", self.Name, self.Name + ".json")

        dfCheck(self.VersionJsonPath, "fm")
        moveFile(Path=OldVersionJsonPath, To=self.VersionJsonPath, Rename=True)
        self.VersionJson = loadFile(Path=self.VersionJsonPath, Type="json")


    def getAssetIndexJson(self):
        """获取对应版本的 AssetIndex json"""
        AssetIndexJsonTask = LoadJson.Version_To_AssetIndex(InitFile=self.VersionJson)
        AssetIndexJsonPath = pathAdder(AssetIndexJsonTask["OutputPath"], AssetIndexJsonTask["FileName"])
        self.Downloader.addTask(InputTask=AssetIndexJsonTask, ProjectID=self.MainDownloadProject)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise Ex_Install.DownloadError

        self.AssetIndexJson = loadFile(Path=AssetIndexJsonPath, Type="json")


    def updateVersionJson(self, **About: dict[str: str]):
        """更新 Version Json"""
        self.VersionJson["id"] = self.Name
        self.VersionJson["jar"] = self.Name
        saveFile(Path=self.VersionJsonPath, FileContent=self.VersionJson, Type="json")


    def replaceURL(self, URL: str, URLType: str, MirrorName: str | None = None) -> str:
        if MirrorName == None: MirrorName = self.UsingDownloadServer


    def InstallForge(self):
        """安装Forge"""


    def InstallFabric(self):
        """安装Fabric"""


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

