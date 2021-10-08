#VERSION=9
#
#Claset/Base/Logs.py
#日志记录
#

from os import listdir, remove
from os.path import abspath
from tarfile import open as openTar
from time import localtime, strftime
from re import compile as reCompile
from sys import stdout

from .Path import path
from .DFCheck import dfCheck
from .Configs import Configs as ConfigsClass


class Logs():
    def __init__(self, LogPath: str = "$EXEC/Logs/", LogName: str = r"Claset-log-{TIME}.log", Configs: dict = None, ProcessOldLogMode: str = None, LogHeader: list = None, ENABLE: bool = None) -> None:
        if Configs == None:
            self.Configs = ConfigsClass().getConfig("Logs", TargetLastVersion=0)
        else:
            self.Configs = Configs

        if ENABLE != None: self.Configs["ENABLE"] = True
        if self.Configs["ENABLE"] == True:
            if "$" in LogPath:
                LogPath = path(LogPath)
            
            if ProcessOldLogMode != None:
                self.Configs["OldLogProcess"]["Type"] = ProcessOldLogMode
            
            if LogHeader != None:
                self.LogHeader = self.logHeaderAdder(LogHeader, ["Logger"])
            else:
                self.LogHeader = ["Logger"]

            dfCheck("dm" , LogPath)
            self.LogPath = LogPath
            self.LogFileName = self.genLogFileName(LogName)
            if self.Configs["ProgressiveWrite"] == True:
                self.LogContent = None
            else:
                self.LogContent = open(self.LogFileName, mode="w")
            
            self.processOldLog()


    # 日志头合成器
    def logHeaderAdder(self, transferHeader: list | str | int | float, Header: list | str | int | float) -> list:
        if type(transferHeader) != type(list()):
            if type(transferHeader) != type(str()):
                transferHeader = str(transferHeader)
            transferHeader = list(transferHeader)
        if type(Header) != type(list()):
            if type(Header) != type(str()):
                Header = str(Header)
            Header = list(Header)
        return(transferHeader + Header)


    # 生成日志文件文件名
    def genLogFileName(self, LogName: str) -> str:
        if r"{TIME}" in LogName:
            Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            LogName = LogName.replace(r"{TIME}", Time)
        return(LogName)


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


    # 生成日志
    def genLog(self, Perfixs:list = list(), Text:str = str(), Type: str ="INFO", SaveToFile: bool= True) -> None:
        if self.Configs["ENABLE"] == False: return "UnEnabled"
        if not (Type in self.Configs["Types"]): Type == "INFO"
        if (Type == "DEBUG") and (self.Configs["Debug"] == False): return None
        if type(Text) == type(list()):
            try:
                Text = str().join(Text)
            except TypeError:
                for i in range(len(Text)):
                    if type(Text[i]) != type(str()): Text[i] = str(Text[i])
                Text = str().join(Text)
                
        Perfix = str()

        #Perfixs
        if len(Perfixs) != 0:
            for Name in Perfixs:
                Perfix += self.Configs["Format"]["Perfix"].replace(r"{Name}", str(Name))
        
        #Text
        Text = Text.replace(r"{Text}", Text)

        #Time
        Time = strftime(self.Configs["Format"]["Time"], localtime())

        FullLog = self.Configs["Format"]["FullLog"].replace(r"{Time}", Time).replace(r"{Type}", Type).replace(r"{Perfixs}", Perfix).replace(r"{Text}", Text) + "\n"

        if SaveToFile == True:
            if self.Configs["ProgressiveWrite"] == True:
                with open(self.LogPath + self.LogFileName, mode="a") as File: File.write(FullLog)
            else:
                self.LogContent.write(FullLog)

        # 打印日志
        stdout.write(FullLog)

