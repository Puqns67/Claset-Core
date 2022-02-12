# -*- coding: utf-8 -*-
"""下载游戏"""

from logging import getLogger

from Claset import getDownloader
from Claset.Utils import (
    DownloadManager, Configs,
    loadFile, saveFile, dfCheck, copyFile, pathAdder
)
from Claset.Game.Utils import (
    getVersionManifestDownloadTaskObject,
    Version_Client_DownloadList, AssetIndex_DownloadList,
    VersionManifest_To_Version, Version_To_AssetIndex
)
from Claset.Game.Utils.Exceptions import TargetVersionNotFound

from .Exceptions import UnknownVersion, DownloadError, UndefinedMirror

Logger = getLogger(__name__)


class GameInstaller():
    """
    游戏安装器
    * Name: 游戏版本名
    * Version: 游戏版本号
    * Downloader: 下载器, 不定义则使用全局下载器
    """
    def __init__(self, VersionName: str, MinecraftVersion: str | None = None, Downloader: DownloadManager | None = None, WaitDownloader: bool = True, UsingDownloadServer: str | None = None):
        self.VersionName = VersionName
        self.MinecraftVersion = MinecraftVersion
        self.WaitDownloader = WaitDownloader
        self.VersionDir = pathAdder("$VERSION", VersionName)

        if Downloader == None:
            self.Downloader = getDownloader()
        else:
            self.Downloader = Downloader

        self.MainDownloadProject = self.Downloader.createProject()

        # 载入相关的配置
        self.GlobalSettings = Configs(ID="Settings")
        if UsingDownloadServer != None:
            self.UsingDownloadServer = UsingDownloadServer
        else:
            self.UsingDownloadServer: str = Configs(ID="Settings").get(["DownloadServer"])

        try:
            self.Mirrors = Configs(ID="Mirrors")[self.UsingDownloadServer]
        except KeyError:
            raise UndefinedMirror(self.UsingDownloadServer)


    def InstallVanilla(self) -> None:
        """下载并安装游戏"""
        if self.MinecraftVersion == None:
            Logger.info("Start installation name \"%s\" from latest Vanilla stable Verison", self.VersionName)
        else:
            Logger.info("Start installation name \"%s\" from Vanilla Verison \"%s\"", self.VersionName, self.MinecraftVersion)
        self.VersionJson = self.getVersionJson()
        self.AssetIndexJson = self.getAssetIndexJson(VersionJson=self.VersionJson, MainProjectID=self.MainDownloadProject)

        # 解析下载项
        DownloadList = Version_Client_DownloadList(InitFile=self.VersionJson, Name=self.VersionName)
        DownloadList.extend(AssetIndex_DownloadList(InitFile=self.AssetIndexJson))

        # 下载
        Logger.info("Downloading Minecraft Vanilla Verison \"%s\", from mirror \"%s\"", self.VersionName, self.MinecraftVersion)
        self.Downloader.addTasks(InputTasks=DownloadList, MainProjectID=self.MainDownloadProject)

        if self.WaitDownloader:
            self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)

        # 创建版本配置文件
        self.createConfig()


    def getVersionJson(self) -> dict:
        """获取对应版本的 Version json, 自动获取 Version Manifest"""
        VersionManifestTask = self.Downloader.fullTask(getVersionManifestDownloadTaskObject())
        if dfCheck(Path=VersionManifestTask["OutputPaths"], Type="f"):
            VersionManifestFileType = "OLD"
        else:
            self.Downloader.addTask(InputTask=VersionManifestTask, ProjectID=self.MainDownloadProject)
            self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)
            VersionManifestFileType = "NEW"
        VersionManifestFile = loadFile(Path=VersionManifestTask["OutputPaths"], Type="json")

        # 如版本号为空, 则使用最新的稳定版 Minecraft
        if self.MinecraftVersion == None:
            self.MinecraftVersion = VersionManifestFile["latest"]["release"]

        while True:
            try:
                VersionTask = self.Downloader.fullTask(VersionManifest_To_Version(InitFile=VersionManifestFile, TargetVersion=self.MinecraftVersion))
            except TargetVersionNotFound:
                match VersionManifestFileType:
                    case "NEW":
                        raise UnknownVersion(self.MinecraftVersion)
                    case "OLD":
                        self.Downloader.addTask(InputTask=VersionManifestTask, ProjectID=self.MainDownloadProject)
                        self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)
                        VersionManifestFile = loadFile(Path=VersionManifestTask["OutputPaths"], Type="json")
                        VersionManifestFileType = "NEW"
            else: break

        self.Downloader.addTask(InputTask=VersionTask, ProjectID=self.MainDownloadProject)
        self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)

        self.VersionPath = pathAdder("$VERSION", self.VersionName, self.VersionName + ".json")

        dfCheck(Path=self.VersionPath, Type="fm")
        copyFile(src=VersionTask["OutputPaths"], dst=self.VersionPath)
        VersionJson = loadFile(Path=self.VersionPath, Type="json")
        # 数据保持
        VersionJson["id"] = self.VersionName
        VersionJson["jar"] = self.VersionName
        VersionJson["version"] = self.MinecraftVersion
        saveFile(Path=self.VersionPath, FileContent=VersionJson, Type="json")

        return(VersionJson)


    def getAssetIndexJson(self, VersionJson: dict, MainProjectID: int) -> dict:
        """获取对应版本的 AssetIndex json"""
        AssetIndexTask = self.Downloader.fullTask(Version_To_AssetIndex(InitFile=VersionJson))
        self.Downloader.addTask(InputTask=AssetIndexTask, ProjectID=MainProjectID)
        self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)
        return(loadFile(Path=AssetIndexTask["OutputPaths"], Type="json"))


    def createConfig(self) -> None:
        """创建版本配置文件"""
        ProcessList = ["REPLACE:[UnableGlobal, NativesDir]->natives"]
        Configs(ID="Game", FilePath=pathAdder("$VERSION", self.VersionName, "ClasetVersionConfig.json"), ProcessList=ProcessList)


    def InstallForge(self):
        """安装Forge"""


    def InstallFabric(self):
        """安装Fabric"""


    def __del__(self):
        """释放函数"""
        self.Downloader.deleteProject(self.MainDownloadProject)

