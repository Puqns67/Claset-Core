# -*- coding: utf-8 -*-
"""下载游戏"""

from logging import getLogger

from Claset import getDownloader
from Claset.Utils import (
    DownloadManager, Configs,
    loadFile, saveFile, dfCheck, moveFile, pathAdder
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
    * Downloader: 下载器，不定义则使用全局下载器
    """
    def __init__(self, VersionName: str, MinecraftVersion: str, Downloader: DownloadManager | None = None, WaitDownloader: bool = True, UsingDownloadServer: str | None = None):
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

        # 更新版本 Json
        self.updateVersionJson()

        # 创建版本配置文件
        self.createConfig()


    def getVersionJson(self) -> dict:
        """获取对应版本的 Version json, 自动获取 Version Manifest"""
        VersionManifestTask = getVersionManifestDownloadTaskObject()
        if dfCheck(Path=VersionManifestTask["OutputPaths"], Type="f"):
            VersionManifestFileType = "OLD"
        else:
            self.Downloader.addTask(InputTask=VersionManifestTask, ProjectID=self.MainDownloadProject)
            self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)
            VersionManifestFileType = "NEW"
        VersionManifestFile = loadFile(Path=VersionManifestTask["OutputPaths"], Type="json")

        while True:
            try:
                VersionTask = VersionManifest_To_Version(InitFile=VersionManifestFile, TargetVersion=self.MinecraftVersion)
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
        moveFile(File=pathAdder(VersionTask["OutputPath"], VersionTask["FileName"]), To=self.VersionPath, Rename=True)
        return(loadFile(Path=self.VersionPath, Type="json"))


    def getAssetIndexJson(self, VersionJson: dict, MainProjectID: int) -> dict:
        """获取对应版本的 AssetIndex json"""
        AssetIndexTask = self.Downloader.fullTask(Version_To_AssetIndex(InitFile=VersionJson))
        self.Downloader.addTask(InputTask=AssetIndexTask, ProjectID=MainProjectID)
        self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)
        return(loadFile(Path=AssetIndexTask["OutputPaths"], Type="json"))


    def updateVersionJson(self, **About: dict[str: str]) -> None:
        """更新 Version Json"""
        self.VersionJson["id"] = self.VersionName
        self.VersionJson["jar"] = self.VersionName
        saveFile(Path=self.VersionPath, FileContent=self.VersionJson, Type="json")

    
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


    def __del__(self):
        """释放函数"""
        self.Downloader.deleteProject(self.MainDownloadProject)

