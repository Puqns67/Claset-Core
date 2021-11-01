#VERSION=9
#
#Claset/Base/Logs.py
#日志记录
#

from os import listdir, remove
from os.path import abspath
from tarfile import open as openTar
from re import compile as reCompile


# 处理老日志
def processOldLog(self) -> None:
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
        self.genLog(Perfixs=self.LogHeader + ["ProcessOldLog"], Text=["Unsupport Type: ", self.Configs["OldLogProcess"]["Type"]])
