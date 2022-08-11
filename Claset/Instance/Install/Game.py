# -*- coding: utf-8 -*-
"""游戏安装器"""

from logging import getLogger

from Claset.Utils import (
    DownloadTask,
    DownloadManager,
    Configs,
    FileTypes,
    loadFile,
    saveFile,
    dfCheck,
    copyFile,
    pathAdder,
    getDownloader,
)
from Claset.Instance.Utils import (
    InstanceInfos,
    getVersionManifestTask,
    VersionManifest_To_Version,
    Version_To_AssetIndex,
)
from Claset.Instance.Utils.Exceptions import TargetVersionNotFound

from .Exceptions import *

__all__ = ("GameInstaller",)
Logger = getLogger(__name__)


class GameInstaller:
    """
    游戏安装器
    * Name: 游戏版本名
    * Version: 游戏版本号
    * Downloader: 下载器, 不定义则使用全局下载器
    """

    def __init__(
        self,
        VersionName: str,
        MinecraftVersion: str | None = None,
        Downloader: DownloadManager | None = None,
        WaitDownloader: bool = True,
        UsingDownloadServer: str | None = None,
    ):
        self.VersionName = VersionName
        self.MinecraftVersion = MinecraftVersion
        self.WaitDownloader = WaitDownloader
        self.VersionDir = pathAdder("$VERSION", VersionName)
        self.VersionInfos = InstanceInfos(VersionName=VersionName)

        if Downloader is None:
            self.Downloader = getDownloader()
        else:
            self.Downloader = Downloader

        # 载入相关的配置
        self.GlobalSettings = Configs(ID="Settings")
        if UsingDownloadServer is not None:
            self.UsingDownloadServer = UsingDownloadServer
        else:
            self.UsingDownloadServer: str = Configs(ID="Settings")["DownloadServer"]

        try:
            self.Mirrors = Configs(ID="Mirrors")[self.UsingDownloadServer]
        except KeyError:
            raise UndefinedMirror(self.UsingDownloadServer)

    def __del__(self):
        """释放函数"""
        if hasattr(self, "MainDownloadProject"):
            self.Downloader.deleteProject(self.MainDownloadProject)

    def InstallVanilla(self) -> None:
        """下载并安装游戏, 需要先获取任务"""
        if self.VersionInfos.check():
            raise VanillaInstalled(self.VersionName)

        if not hasattr(self, "MainDownloadProject"):
            self.MainDownloadProject = self.Downloader.createProject()

        # 下载
        if self.MinecraftVersion is None:
            Logger.info(
                'Start installation name "%s" from latest Vanilla stable Verison',
                self.VersionName,
            )
        else:
            Logger.info(
                'Start installation name "%s" from Vanilla Verison "%s"',
                self.VersionName,
                self.MinecraftVersion,
            )

        Logger.info('Checking exists files for "%s"', self.VersionName)
        DownloadTasks = self.getTasks()

        if len(DownloadTasks) <= 0:
            Logger.info('Install Minecraft Vanilla Verison "%s"', self.VersionName)
        else:
            Logger.info(
                'Downloading Minecraft Vanilla Verison "%s", from mirror "%s"',
                self.VersionName,
                self.UsingDownloadServer,
            )
            self.Downloader.addTask(
                InputTasks=DownloadTasks, MainProjectID=self.MainDownloadProject
            )

            if self.WaitDownloader:
                self.Downloader.waitProject(
                    ProjectIDs=self.MainDownloadProject, Raise=DownloadError
                )

        # 创建版本配置文件
        self.createConfig()

    def getTasks(self) -> list[DownloadTask]:
        """获取需下载的任务列表"""
        if not hasattr(self, "MainDownloadProject"):
            self.MainDownloadProject = self.Downloader.createProject()

        self.getVersionSources()
        self.createConfig()
        return self.VersionInfos.checkFull()

    def getVersionSources(self):
        """获取版本元数据 (VersionJson, AssetIndexJson)"""
        if not hasattr(self, "VersionJson"):
            self.VersionJson = self.getVersionJson()

        if not hasattr(self, "AssetIndexJson"):
            self.AssetIndexJson = self.getAssetIndexJson(
                VersionJson=self.VersionJson, MainProjectID=self.MainDownloadProject
            )

    def getVersionJson(self, forceNew: bool = False) -> dict:
        """获取对应版本的 Version json, 自动获取 Version Manifest"""
        if not hasattr(self, "MainDownloadProject"):
            self.MainDownloadProject = self.Downloader.createProject()

        VersionManifestTask = getVersionManifestTask()
        VersionManifestTask.full()
        if dfCheck(Path=VersionManifestTask.OutputPaths, Type="f") and not forceNew:
            VersionManifestFileType = "OLD"
        else:
            self.Downloader.addTask(
                InputTasks=VersionManifestTask, MainProjectID=self.MainDownloadProject
            )
            self.Downloader.waitProject(
                ProjectIDs=self.MainDownloadProject, Raise=DownloadError
            )
            VersionManifestFileType = "NEW"
        VersionManifestFile = loadFile(
            Path=VersionManifestTask.OutputPaths, Type=FileTypes.Json
        )

        # 如版本号为空, 则使用最新的稳定版 Minecraft
        if self.MinecraftVersion is None:
            self.MinecraftVersion = VersionManifestFile["latest"]["release"]
            Logger.debug("Update MinecraftVersion to %s from None", self.MinecraftVersion)

        while True:
            try:
                VersionTask = VersionManifest_To_Version(
                    InitFile=VersionManifestFile, TargetVersion=self.MinecraftVersion
                )
            except TargetVersionNotFound:
                match VersionManifestFileType:
                    case "NEW":
                        raise UnknownVersion(self.MinecraftVersion)
                    case "OLD":
                        Logger.debug("Update old Minectaft version manifest file")
                        self.Downloader.addTask(
                            InputTasks=VersionManifestTask,
                            MainProjectID=self.MainDownloadProject,
                        )
                        self.Downloader.waitProject(
                            ProjectIDs=self.MainDownloadProject, Raise=DownloadError
                        )
                        VersionManifestFile = loadFile(
                            Path=VersionManifestTask.OutputPaths, Type=FileTypes.Json
                        )
                        VersionManifestFileType = "NEW"
            else:
                break

        VersionTask.full()
        self.Downloader.addTask(InputTasks=VersionTask, MainProjectID=self.MainDownloadProject)
        self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)

        self.VersionPath = pathAdder("$VERSION", self.VersionName, self.VersionName + ".json")

        dfCheck(Path=self.VersionPath, Type="fm")
        copyFile(src=VersionTask.OutputPaths, dst=self.VersionPath)
        VersionJson = loadFile(Path=self.VersionPath, Type=FileTypes.Json)
        # 数据保持
        VersionJson["id"] = self.VersionName
        VersionJson["jar"] = self.VersionName
        VersionJson["version"] = self.MinecraftVersion
        Logger.debug("Saveing new version json for %s", self.VersionName)
        saveFile(Path=self.VersionPath, FileContent=VersionJson, Type=FileTypes.Json)

        return VersionJson

    def getAssetIndexJson(self, VersionJson: dict, MainProjectID: int) -> dict:
        """获取对应版本的 AssetIndex json"""
        AssetIndexTask = Version_To_AssetIndex(InitFile=VersionJson)
        AssetIndexTask.full()
        self.Downloader.addTask(InputTasks=AssetIndexTask, MainProjectID=MainProjectID)
        self.Downloader.waitProject(ProjectIDs=self.MainDownloadProject, Raise=DownloadError)
        return loadFile(Path=AssetIndexTask.OutputPaths, Type=FileTypes.Json)

    def createConfig(self) -> None:
        """创建版本配置文件"""
        Configs(
            ID="Instance",
            FilePath=pathAdder("$VERSION", self.VersionName, "ClasetInstanceConfig.json"),
        )
