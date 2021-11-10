# -*- coding: utf-8 -*-
"""为日志添加文件记录 WIP"""

from logging import getLogger
from time import strftime, localtime
from re import compile as reCompile
from tarfile import open as openTar
from os import listdir, remove
from os.path import abspath

Logger = getLogger(__name__)


# 生成日志文件文件名
def genLogFileName(LogName: str = "Claset-log-{TIME}.log") -> str:
    if r"{TIME}" in LogName:
        Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
        LogName = LogName.replace(r"{TIME}", Time)
    return(LogName)

# 处理老日志
def processOldLog() -> None:
    FilelistForTime = dict()
    LogFileFormat = reCompile(r"(Claset-log-([0-9-_]*)(\.log))")
    for i in listdir(self.LogPath):
        reobj = LogFileFormat.search(i)
        if reobj != None:
            FilelistForTime[reobj.groups()[1].replace("-", "").replace("_", "")] = reobj.groups()[0]
    Filelist = list()
    Temp = list(FilelistForTime.keys())
    Temp.sort()
    for i in Temp:
        Filelist.append(FilelistForTime[i])
    if self.Configs["OldLogProcess"]["Type"] == "Delete":
        Temp = len(Filelist) - self.Configs["OldLogProcess"]["Settings"]["Delete"]["MaxKeepFile"]
        if Temp >= 1:
            for i in range(Temp):
                remove(self.LogPath + Filelist[i])
                self.genLog(Perfixs=self.LogHeader + ["ProcessOldLog"], Text=["Deleted old log file: \"", Filelist[i], "\""])
                Filelist.remove(Filelist[i])
    elif self.Configs["OldLogProcess"]["Type"] == "Archive":
        Temp = len(Filelist) - self.Configs["OldLogProcess"]["Settings"]["Archive"]["MaxKeepFile"]
        if Temp >= 1:
            with openTar(self.LogPath + self.Configs["OldLogProcess"]["Settings"]["Archive"]["ArchiveFileName"], "a") as Archive:
                for i in range(Temp):
                    path = abspath(self.LogPath + Filelist[i])
                    Archive.add(path, arcname=Filelist[i])
                    remove(path)
                    self.genLog(Perfixs=self.LogHeader + ["ProcessOldLog"], Text=["Archived old log file: \"", Filelist[i], "\""])
                    Filelist.remove(Filelist[i])
    else:
        Logger.warning("Unsupport Type: %s", Configs["OldLogProcess"]["Type"])

