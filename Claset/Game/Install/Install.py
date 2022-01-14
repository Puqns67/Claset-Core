# -*- coding: utf-8 -*-
"""下载游戏"""

from logging import getLogger

from Claset.Utils import (
    DownloadManager, Configs, AdvancedPath,
    loadFile, saveFile, dfCheck, moveFile, pathAdder
)
from Claset.Game.Utils import (
    getVersionManifestURL,
    Version_Client_DownloadList, AssetIndex_DownloadList,
    VersionManifest_To_Version, Version_To_AssetIndex
)
from Claset.Game.Utils.Exceptions import TargetVersionNotFound

from .Exceptions import UnknownVersion, DownloadError

Logger = getLogger(__name__)


class GameInstaller():
    """
    游戏安装器
    * Name: 游戏版本名
    * Version: 游戏版本号
    * Downloader: 下载器，不定义则使用全局下载器
    """
    def __init__(self, Downloader: DownloadManager, VersionName: str, MinecraftVersion: str, WaitDownloader: bool = True, UsingDownloadServer: str | None = None, AutoInstall: bool = True):
        self.Downloader = Downloader
        self.VersionName = VersionName
        self.MinecraftVersion = MinecraftVersion
        self.WaitDownloader = WaitDownloader
        self.VersionDir = pathAdder("$VERSION", VersionName)

        # 载入相关的配置
        self.GlobalSettings = Configs(ID="Settings")
        if UsingDownloadServer != None:
            self.UsingDownloadServer = UsingDownloadServer
        else:
            self.UsingDownloadServer: str = Configs(ID="Settings").get(["DownloadServer"])

        self.Mirrors = Configs(ID="Mirrors")[self.UsingDownloadServer]

        if AutoInstall:
            # 开始安装
            self.InstallVanilla()

            # 更新版本 Json
            self.updateVersionJson()

            # 创建版本配置文件
            self.createConfig()


    def InstallVanilla(self) -> None:
        """下载并安装游戏"""
        Logger.info("Start installation name \"%s\" from Vanilla Verison \"%s\"", self.VersionName, self.MinecraftVersion)
        VersionManifest_Info = getVersionManifestURL()
        self.MainDownloadProject = self.Downloader.addTask(InputTask=VersionManifest_Info)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise DownloadError

        self.getVersionJson(VersionManifest_Info)
        self.getAssetIndexJson()

        # 解析下载项
        DownloadList = Version_Client_DownloadList(InitFile=self.VersionJson, Name=self.VersionName)
        DownloadList.extend(AssetIndex_DownloadList(InitFile=self.AssetIndexJson))

        # 下载
        Logger.info("Downloading Minecraft Vanilla Verison \"%s\", from mirror \"%s\"", self.VersionName, self.MinecraftVersion)
        self.Downloader.addTasks(InputTasks=DownloadList, MainProjectID=self.MainDownloadProject)
        if ((self.WaitDownloader == True) and (self.Downloader.projectJoin(self.MainDownloadProject) > 0)): raise DownloadError


    def getVersionJson(self, VersionManifest_Info: dict) -> None:
        """获取对应版本的 Version json"""
        try: VersionJsonTask = VersionManifest_To_Version(InitFile=loadFile(pathAdder(VersionManifest_Info["OutputPath"], VersionManifest_Info["FileName"]), Type="json"), TargetVersion=self.MinecraftVersion)
        except TargetVersionNotFound: raise UnknownVersion

        OldVersionJsonPath = pathAdder(VersionJsonTask["OutputPath"], VersionJsonTask["FileName"])
        self.Downloader.addTask(InputTask=VersionJsonTask, ProjectID=self.MainDownloadProject)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise DownloadError

        self.VersionJsonPath = AdvancedPath().pathAdder("$VERSION", self.VersionName, self.VersionName + ".json")

        dfCheck(self.VersionJsonPath, "fm")
        moveFile(File=OldVersionJsonPath, To=self.VersionJsonPath, Rename=True)
        self.VersionJson = loadFile(Path=self.VersionJsonPath, Type="json")


    def getAssetIndexJson(self) -> None:
        """获取对应版本的 AssetIndex json"""
        AssetIndexJsonTask = Version_To_AssetIndex(InitFile=self.VersionJson)
        AssetIndexJsonPath = pathAdder(AssetIndexJsonTask["OutputPath"], AssetIndexJsonTask["FileName"])
        self.Downloader.addTask(InputTask=AssetIndexJsonTask, ProjectID=self.MainDownloadProject)

        if (self.Downloader.projectJoin(self.MainDownloadProject) > 0): raise DownloadError

        self.AssetIndexJson = loadFile(Path=AssetIndexJsonPath, Type="json")


    def updateVersionJson(self, **About: dict[str: str]) -> None:
        """更新 Version Json"""
        self.VersionJson["id"] = self.VersionName
        self.VersionJson["jar"] = self.VersionName
        saveFile(Path=self.VersionJsonPath, FileContent=self.VersionJson, Type="json")

    
    def createConfig(self) -> None:
        """创建版本配置文件"""
        ProcessList = ["REPLACE:[UnableGlobal, NativesDir]->natives"]
        Configs(ID="Game", FilePath=pathAdder("$VERSION", self.VersionName, "ClasetVersionConfig.json"), ProcessList=ProcessList)


    def replaceURL(self, URL: str, URLType: str, MirrorName: str | None = None) -> str:
        if MirrorName == None: MirrorName = self.UsingDownloadServer


    def InstallForge(self):
        """安装Forge"""


    def InstallFabric(self):
        """安装Fabric"""

