# -*- coding: utf-8 -*-
"""日志相关的处理方案"""

from logging import Logger, Formatter, StreamHandler, FileHandler, getLevelName
from os import listdir
from re import compile as reCompile
from time import localtime, strftime
from threading import Thread

try:
    from rich.logging import RichHandler
except ModuleNotFoundError:
    RichHandler = None

from .File import FileTypes, dfCheck, removeFile, makeArchive, addFileIntoArchive
from .Configs import Configs
from .Path import path as Pathmd, pathAdder

__all__ = ("Logs",)


class Logs:
    """日志相关的处理方案"""

    def __init__(self, TheLogger: Logger):
        self.TheLogger = TheLogger
        self.Configs = Configs(ID="Logs")
        self.LogPath = Pathmd(self.Configs["FilePath"], IsPath=True)
        self.Formatter = Formatter(
            fmt=self.Configs["LogFormats"]["Format"],
            datefmt=self.Configs["LogFormats"]["Date"],
        )

    def SettingHandler(self, **Types: dict[str, str | None]):
        """设置 Handler"""
        self.SettingStreamHandler(LevelName=Types.get("Stream"))
        self.SettingFileHandler(LevelName=Types.get("File"))

    def SettingStreamHandler(self, LevelName: str | None = None):
        """设置日志输出至命令行流"""
        if LevelName is None:
            LevelName = self.Configs["LoggingLevel"]
        # 建立 Handler
        if RichHandler is not None and self.Configs["UseRich"]:
            CommandLineHandler = RichHandler()
        else:
            CommandLineHandler = StreamHandler()
            CommandLineHandler.setFormatter(self.Formatter)
        CommandLineHandler.setLevel(getLevelName(LevelName))

        self.TheLogger.addHandler(CommandLineHandler)

    def SettingFileHandler(self, LevelName: str | None = None):
        """设置日志输出至文件"""
        dfCheck(Path=self.LogPath, Type="dm")
        LogFullPath = pathAdder(self.LogPath, self.genFileName())
        if LevelName is None:
            LevelName = self.Configs["LoggingLevel"]
        # 建立 Handler
        NewFileHandler = FileHandler(filename=LogFullPath)
        NewFileHandler.setLevel(getLevelName(LevelName))
        NewFileHandler.setFormatter(self.Formatter)

        self.TheLogger.addHandler(NewFileHandler)
        self.TheLogger.info('Logging to file: "%s"', LogFullPath)

    def SettingLevel(self, LevelName: str | None = None):
        """设置日志级别, 若为空则使用默认配置"""
        if LevelName is None:
            LevelName = self.Configs["LoggingLevel"]
        Level: int = getLevelName(LevelName.upper())
        self.TheLogger.info("Setting logging level to: %s", getLevelName(Level))
        self.TheLogger.setLevel(Level)

    def genFileName(self, LogName: str = "Claset-log-{TIME}.log") -> str:
        """生成日志文件文件名"""
        if r"{TIME}" in LogName:
            Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            LogName = LogName.replace(r"{TIME}", Time)
        return LogName

    def threadProcessLogs(self, Type: str | None = None) -> None:
        """使用独立线程处理老日志"""
        Thread(target=self.processLogs, kwargs={"Type": Type}).start()

    def processLogs(self, Type: str | None = None) -> None:
        """处理老日志"""
        # 让日志文件名以时间排序
        FilelistForTime = dict()
        LogFileFormat = reCompile(r"(Claset-log-([0-9-_]*)\.log)")
        for i in listdir(self.LogPath):
            try:
                ReGroups = LogFileFormat.search(i).groups()
            except AttributeError:
                continue
            FilelistForTime[ReGroups[1]] = ReGroups[0]
        LogFileList = list()
        Temp = list(FilelistForTime)
        Temp.sort()
        for i in Temp:
            LogFileList.append(FilelistForTime[i])
        del Temp

        if Type is None:
            Type = self.Configs["ProcessOldLog"]["Type"]

        match Type:
            # 直接删除
            case "Delete":
                TypeConfigs = self.Configs["ProcessOldLog"]["TypeSettings"]["Delete"]
                # 若不满足情况则直接返回
                if len(LogFileList) <= TypeConfigs["MaxKeepFile"]:
                    return None

                for FileName in LogFileList:
                    removeFile(self.LogPath + "/" + FileName)
                    self.TheLogger.info('Deleted old log file: "%s"', FileName)
                    LogFileList.remove(FileName)
                    if len(LogFileList) <= TypeConfigs["MaxKeepFile"]:
                        break

            # 进行存档
            case "Archive":
                TypeConfigs = self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]
                NeedArchivePaths = list()
                # 若不满足情况则直接返回
                if len(LogFileList) <= TypeConfigs["MaxKeepFile"]:
                    return None

                ArchiveFilePath = pathAdder(self.LogPath, TypeConfigs["ArchiveFileName"])

                for LogFileName in LogFileList:
                    self.TheLogger.info('Archiveing old log file: "%s"', LogFileName)
                    NeedArchivePaths.append(pathAdder(self.LogPath, LogFileName))
                    LogFileList.remove(LogFileName)
                    if len(LogFileList) <= TypeConfigs["MaxKeepFile"]:
                        break

                if not dfCheck(Path=ArchiveFilePath, Type="f"):
                    makeArchive(
                        SourcePaths=NeedArchivePaths.pop(),
                        ArchivePath=ArchiveFilePath,
                        Type=FileTypes.Zstandard,
                    )

                if len(NeedArchivePaths) >= 1:
                    addFileIntoArchive(
                        ArchivePath=ArchiveFilePath,
                        SourcePaths=NeedArchivePaths,
                        Type=FileTypes.Zstandard,
                    )
                    for i in NeedArchivePaths:
                        removeFile(path=i)

            case _:
                self.TheLogger.warning(
                    "Unsupport Type: %s", self.Configs["ProcessOldLog"]["Type"]
                )
