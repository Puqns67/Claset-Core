# -*- coding: utf-8 -*-
"""为日志添加文件记录/存档"""

import logging
from os import listdir, remove
from os.path import abspath
from re import compile as reCompile
from tarfile import open as openTar
from time import localtime, strftime

from .DFCheck import dfCheck
from .Configs import Configs
from .Path import path as Pathmd

Logger = logging.getLogger(__name__)
Formatter = logging.Formatter(fmt="[%(asctime)s][%(module)s][%(funcName)s][%(levelname)s]: %(message)s", datefmt="%Y/%m/%d|%H:%M:%S")


class Logs():
    def __init__(self):
        self.Configs = Configs().getConfig("Logs")
        self.LogPath = Pathmd(self.Configs["FilePath"])


    # 设置保存日志至文件
    def SettingFileHandler(self):
        dfCheck(Path=self.Configs["FilePath"], Type="dm")
        LogFullPath = Pathmd(self.LogPath + self.genFileName())
        # 建立 Handler
        NewFileHandler = logging.FileHandler(filename=LogFullPath)
        NewFileHandler.setLevel(logging.DEBUG)
        NewFileHandler.setFormatter(Formatter)
        Logger.addHandler(NewFileHandler)
        Logger.info("Logging to file: \"%s\"", LogFullPath)


    # 生成日志文件文件名
    def genFileName(self, LogName: str = "Claset-log-{TIME}.log") -> str:
        if r"{TIME}" in LogName:
            Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            LogName = LogName.replace(r"{TIME}", Time)
        return(LogName)


    # 处理老日志
    def processOldLog(self) -> None:
        # 让日志文件以时间排序
        FilelistForTime = dict()
        LogFileFormat = reCompile(r"(Claset-log-([0-9-_])*\.log)")
        for i in listdir(self.LogPath):
            ReObject = LogFileFormat.search(i)
            if ReObject != None:
                FilelistForTime[ReObject.groups()[1].replace("-", "").replace("_", "")] = ReObject.groups()[0]
        Filelist = list()
        Temp = list(FilelistForTime.keys())
        Temp.sort()
        for i in Temp: Filelist.append(FilelistForTime[i])

        # 直接删除 
        if self.Configs["ProcessOldLog"]["Type"] == "Delete":
            Temp = len(Filelist) - self.Configs["ProcessOldLog"]["TypeSettings"]["Delete"]["MaxKeepFile"]
            if Temp >= 1:
                for i in range(Temp):
                    remove(self.LogPath + Filelist[i])
                    Logger.info("Deleted old log file: \"%s\"", Filelist[i])
                    Filelist.remove(Filelist[i])

        # 进行存档
        elif self.Configs["ProcessOldLog"]["Type"] == "Archive":
            Temp = len(Filelist) - self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]["MaxKeepFile"]
            if Temp >= 1:
                with openTar(self.LogPath + self.Configs["ProcessOldLog"]["TypeSettings"]["Archive"]["ArchiveFileName"], "a") as Archive:
                    for i in range(Temp):
                        path = abspath(self.LogPath + Filelist[i])
                        Archive.add(path, arcname=Filelist[i])
                        remove(path)
                        Logger.info("Archived old log file: \"%s\"", Filelist[i])
                        Filelist.remove(Filelist[i])

        else: Logger.warning("Unsupport Type: %s", self.Configs["ProcessOldLog"]["Type"])

