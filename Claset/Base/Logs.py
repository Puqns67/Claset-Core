# -*- coding: utf-8 -*-
"""为日志添加文件记录/存档"""

import logging
from os import listdir, remove
from re import compile as reCompile
from tarfile import open as openTar, ReadError
from time import localtime, strftime

from .DFCheck import dfCheck
from .Configs import Configs
from .Path import path as Pathmd


class Logs():
    def __init__(self, TheLogger: logging.Logger):
        self.Configs = Configs().getConfig("Logs")
        self.LogPath = Pathmd(self.Configs["FilePath"], IsPath=True)
        self.TheLogger = TheLogger
        self.Formatter = logging.Formatter(fmt=self.Configs["LogFormats"]["Format"], datefmt=self.Configs["LogFormats"]["Date"])


    # 设置 Handler
    def SettingHandler(self):
        if self.Configs["Handlers"]["Stream"] == True: self.SettingStreamHandler()
        if self.Configs["Handlers"]["File"] == True:   self.SettingFileHandler()


    # 设置日志输出至流
    def SettingStreamHandler(self):
        # 建立 Handler
        StreamHandler = logging.StreamHandler()
        StreamHandler.setLevel(logging.DEBUG)
        StreamHandler.setFormatter(self.Formatter)

        self.TheLogger.addHandler(StreamHandler)


    # 设置日志输出至文件
    def SettingFileHandler(self):
        dfCheck(Path=self.LogPath, Type="dm")
        LogFullPath = Pathmd(self.LogPath + "/" + self.genFileName(), IsPath=True)
        # 建立 Handler
        NewFileHandler = logging.FileHandler(filename=LogFullPath)
        NewFileHandler.setLevel(logging.DEBUG)
        NewFileHandler.setFormatter(self.Formatter)

        self.TheLogger.addHandler(NewFileHandler)
        self.TheLogger.info("Logging to file: \"%s\"", LogFullPath)


    # 生成日志文件文件名
    def genFileName(self, LogName: str = "Claset-log-{TIME}.log") -> str:
        if r"{TIME}" in LogName:
            Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            LogName = LogName.replace(r"{TIME}", Time)
        return(LogName)


    # 处理老日志
    def processOldLog(self) -> None:
        # 让日志文件名以时间排序
        FilelistForTime = dict()
        LogFileFormat = reCompile(r"(Claset-log-([0-9-_]*)\.log)")
        for i in listdir(self.LogPath):
            try:
                ReGroups = LogFileFormat.search(i).groups()
            except AttributeError:
                continue
            FilelistForTime[ReGroups[1]] = ReGroups[0]
        FileList = list()
        Temp = list(FilelistForTime.keys())
        Temp.sort()
        for i in Temp: FileList.append(FilelistForTime[i])

        # 直接删除 
        match self.Configs["ProcessOldLog"]["Type"]:
            case "Delete":
                # 若不满足情况则直接返回
                if (len(FileList) <= self.Configs["ProcessOldLog"]["TypeSettings"]["Delete"]["MaxKeepFile"]): return(None)
                for FileName in FileList:
                    remove(self.LogPath + "/" + FileName)
                    self.TheLogger.info("Deleted old log file: \"%s\"", FileName)
                    FileList.remove(FileName)
                    if (len(FileList) <= self.Configs["ProcessOldLog"]["TypeSettings"]["Delete"]["MaxKeepFile"]): break

            # 进行存档
            case "Archive":
                # 若不满足情况则直接返回
                if (len(FileList) <= self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]["MaxKeepFile"]): return(None)
                TarFilePath = Pathmd(self.LogPath + "/" + self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]["ArchiveFileName"], IsPath=True)
                try:
                    with openTar(TarFilePath, "a") as Archive:
                        for FileName in FileList:
                            FilePath = self.LogPath + "/" + FileName
                            Archive.add(name=FilePath, arcname=FileName)
                            remove(FilePath)
                            self.TheLogger.info("Archived old log file: \"%s\"", FileName)
                            FileList.remove(FileName)
                            if (len(FileList) <= self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]["MaxKeepFile"]): break
                except ReadError:
                    remove(TarFilePath)
                    self.processOldLog()

            case _: self.TheLogger.warning("Unsupport Type: %s", self.Configs["ProcessOldLog"]["Type"])

