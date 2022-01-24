# -*- coding: utf-8 -*-
"""日志相关的处理方案"""

from logging import Logger, Formatter, StreamHandler, FileHandler, getLevelName
from os import listdir, remove
from re import compile as reCompile
from shutil import make_archive, unpack_archive, rmtree
from time import localtime, strftime
from threading import Thread

from .File import dfCheck, moveFile
from .Configs import Configs
from .Path import path as Pathmd, pathAdder


class Logs():
    """日志相关的处理方案"""
    def __init__(self, TheLogger: Logger):
        self.TheLogger = TheLogger
        self.Configs = Configs(ID="Logs")
        self.LogPath = Pathmd(self.Configs["FilePath"], IsPath=True)
        self.Formatter = Formatter(fmt=self.Configs["LogFormats"]["Format"], datefmt=self.Configs["LogFormats"]["Date"])


    def SettingHandler(self, Stream: bool = True, File: bool = True):
        """设置 Handler"""
        if Stream and self.Configs["Handlers"]["Stream"]:
            self.SettingStreamHandler()
        if File and self.Configs["Handlers"]["File"]:
            self.SettingFileHandler()


    def SettingStreamHandler(self, LevelName: str | None = None):
        """设置日志输出至命令行流"""
        if LevelName == None: LevelName = self.Configs["LoggingLevel"]
        # 建立 Handler
        CommandLineHandler = StreamHandler()
        CommandLineHandler.setLevel(getLevelName(LevelName))
        CommandLineHandler.setFormatter(self.Formatter)

        self.TheLogger.addHandler(CommandLineHandler)


    def SettingFileHandler(self, LevelName: str | None = None):
        """设置日志输出至文件"""
        dfCheck(Path=self.LogPath, Type="dm")
        LogFullPath = pathAdder(self.LogPath, self.genFileName())
        if LevelName == None: LevelName = self.Configs["LoggingLevel"]
        # 建立 Handler
        NewFileHandler = FileHandler(filename=LogFullPath)
        NewFileHandler.setLevel(getLevelName(LevelName))
        NewFileHandler.setFormatter(self.Formatter)

        self.TheLogger.addHandler(NewFileHandler)
        self.TheLogger.info("Logging to file: \"%s\"", LogFullPath)


    def SettingLevel(self, LevelName: str | None = None):
        """设置日志级别, 若为空则使用默认配置"""
        if LevelName == None: LevelName = self.Configs["LoggingLevel"]
        Level: int = getLevelName(LevelName.upper())
        self.TheLogger.info("Setting logging level to: %s", getLevelName(Level))
        self.TheLogger.setLevel(Level)


    def genFileName(self, LogName: str = "Claset-log-{TIME}.log") -> str:
        """生成日志文件文件名"""
        if r"{TIME}" in LogName:
            Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            LogName = LogName.replace(r"{TIME}", Time)
        return(LogName)


    def ThreadProcessLogs(self, Type: str | None = None):
        """使用独立线程处理老日志"""
        Thread(target=self.ProcessLogs, kwargs={"Type": Type}).start()


    def ProcessLogs(self, Type: str | None = None) -> None:
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
        Temp = list(FilelistForTime.keys())
        Temp.sort()
        for i in Temp: LogFileList.append(FilelistForTime[i])
        del(Temp)

        if Type == None: Type = self.Configs["ProcessOldLog"]["Type"]

        # 直接删除
        match Type:
            case "Delete":
                TypeConfigs = self.Configs["ProcessOldLog"]["TypeSettings"]["Delete"]
                # 若不满足情况则直接返回
                if (len(LogFileList) <= TypeConfigs["MaxKeepFile"]): return(None)
                for FileName in LogFileList:
                    remove(self.LogPath + "/" + FileName)
                    self.TheLogger.info("Deleted old log file: \"%s\"", FileName)
                    LogFileList.remove(FileName)
                    if (len(LogFileList) <= TypeConfigs["MaxKeepFile"]): break

            # 进行存档
            case "Archive":
                TypeConfigs = self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]

                # 若不满足情况则直接返回
                if (len(LogFileList) <= TypeConfigs["MaxKeepFile"]): return(None)

                ArchiveFilePath = pathAdder(self.LogPath, TypeConfigs["ArchiveFileName"])
                TempDir = pathAdder("$CACHE", TypeConfigs["TempDirName"])
                dfCheck(Path=TempDir, Type="dm")

                if (dfCheck(Path=ArchiveFilePath + ".tar.xz", Type="f")):
                    try:
                        unpack_archive(filename=ArchiveFilePath + ".tar.xz", extract_dir=TempDir, format="xztar")
                    except EOFError:
                        self.TheLogger.error("Archive File (%s) EOF!", ArchiveFilePath)
                        remove(ArchiveFilePath + ".tar.xz")

                for LogFileName in LogFileList:
                    LogFilePath = pathAdder(self.LogPath, LogFileName)
                    moveFile(File=LogFilePath, To=TempDir)
                    self.TheLogger.info("Archived old log file: \"%s\"", LogFileName)
                    LogFileList.remove(LogFileName)
                    if (len(LogFileList) <= TypeConfigs["MaxKeepFile"]): break

                try:
                    make_archive(base_name=ArchiveFilePath, format="xztar", root_dir=TempDir, base_dir=None)
                except PermissionError:
                    self.TheLogger.error("Make archive error")
                rmtree(path=TempDir)

            case _: self.TheLogger.warning("Unsupport Type: %s", self.Configs["ProcessOldLog"]["Type"])

