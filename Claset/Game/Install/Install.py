# -*- coding: utf-8 -*-
"""下载游戏"""

from logging import getLogger

from Claset.Utils import (
    DownloadManager, Configs, AdvancedPath,
    loadFile, saveFile, dfCheck, moveFile, pathAdder
)

from ..Utils import (
    getVersionManifestURL,
    Version_Client_DownloadList, AssetIndex_DownloadList,
    VersionManifest_To_Version, Version_To_AssetIndex
)
from ..Utils.Exceptions import TargetVersionNotFound

from .Exceptions import UnknownVersion, DownloadError

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
        Logger.info("Start installation name \"%s\" from Vanilla Verison \"%s\"", self.Name, self.Version)
        VersionManifest_Info = getVersionManifestURL()
        self.MainDownloadProject = self.Downloader.addTask(InputTask=VersionManifest_Info)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise DownloadError

        self.getVersionJson(VersionManifest_Info)
        self.getAssetIndexJson()

        # 解析下载项
        DownloadList = Version_Client_DownloadList(InitFile=self.VersionJson, Name=self.Name)
        DownloadList.extend(AssetIndex_DownloadList(InitFile=self.AssetIndexJson))

        # 下载
        Logger.info("Downloading Minecraft Vanilla Verison \"%s\", from mirror \"%s\"", self.Name, self.Version)
        self.Downloader.addTasks(InputTasks=DownloadList, MainProjectID=self.MainDownloadProject)
        if ((self.WaitDownloader == True) and (self.Downloader.projectJoin(self.MainDownloadProject) > 0)): raise DownloadError


    def getVersionJson(self, VersionManifest_Info: dict):
        """获取对应版本的 Version json"""
        try: VersionJsonTask = VersionManifest_To_Version(InitFile=loadFile(pathAdder(VersionManifest_Info["OutputPath"], VersionManifest_Info["FileName"]), Type="json"), TargetVersion=self.Version)
        except TargetVersionNotFound: raise UnknownVersion

        OldVersionJsonPath = pathAdder(VersionJsonTask["OutputPath"], VersionJsonTask["FileName"])
        self.Downloader.addTask(InputTask=VersionJsonTask, ProjectID=self.MainDownloadProject)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise DownloadError

        self.VersionJsonPath = AdvancedPath().pathAdder("$VERSION", self.Name, self.Name + ".json")

        dfCheck(self.VersionJsonPath, "fm")
        moveFile(File=OldVersionJsonPath, To=self.VersionJsonPath, Rename=True)
        self.VersionJson = loadFile(Path=self.VersionJsonPath, Type="json")


    def getAssetIndexJson(self):
        """获取对应版本的 AssetIndex json"""
        AssetIndexJsonTask = Version_To_AssetIndex(InitFile=self.VersionJson)
        AssetIndexJsonPath = pathAdder(AssetIndexJsonTask["OutputPath"], AssetIndexJsonTask["FileName"])
        self.Downloader.addTask(InputTask=AssetIndexJsonTask, ProjectID=self.MainDownloadProject)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise DownloadError

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

