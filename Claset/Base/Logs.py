#VERSION=7
#
#Claset/Base/Logs.py
#日志记录
#

from os import listdir, remove
from lzma import open as openLzma
from time import localtime, strftime
from re import compile as reCompile

from . import Loadfile
from . import Path
from . import DFCheck


class Logs():
    def __init__(self, LogPath="$EXEC/Logs/", LogName=r"Claset-log-{TIME}.log", Configs=None, ProcessOldLogMode=None, LogHeader=None) -> None:
        if Configs == None:
            self.Configs = Loadfile.loadfile("$EXEC/Configs/Logs.json", "json")
        else:
            self.Configs = Configs

        if "$" in LogPath:
            LogPath = Path.path(LogPath)
        
        if ProcessOldLogMode != None:
            self.Configs["OldLogProcess"]["Type"] = ProcessOldLogMode
        
        if LogHeader != None:
            self.LogHeader = self.logHeaderAdder(LogHeader, ["Logger"])
        else:
            self.LogHeader = ["Logger"]

        DFCheck.dfcheck("dm" , LogPath)
        self.LogPath = LogPath
        self.LogFileName = self.genLogFileName(LogName)
        if self.Configs["ProgressiveWrite"] == True:
            self.LogContent = None
        else:
            self.LogContent = open(self.LogFileName, mode="w")
        
        self.processOldLog()

    def logHeaderAdder(self, transferHeader, Header) -> list:
        if type(transferHeader) != type(list()):
            if type(transferHeader) != type(str()):
                transferHeader = str(transferHeader)
            transferHeader = list(transferHeader)
        if type(Header) != type(list()):
            if type(Header) != type(str()):
                Header = str(Header)
            Header = list(Header)
        return(transferHeader + Header)

    def genLogFileName(self, LogName) -> str:
        if r"{TIME}" in LogName:
            Time = strftime("%Y-%m-%d_%H-%M-%S", localtime())
            LogName = LogName.replace(r"{TIME}", Time)
        return(LogName)
    
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
        """
        elif self.Configs["OldLogProcess"]["Type"] == "Archive":
            pass

            print(FilelistForTime, "\n", Filelist)
            with openLzma(self.LogPath + self.Configs["OldLogProcess"]["Settings"]["Archive"]["ArchiveFileName"]) as Archive:
                

        elif self.Configs["OldLogProcess"]["Type"] == "Archive + Delete":
            print("WIP")
        else:
            self.genLog(Perfixs=self.LogHeader + ["ProcessOldLog"], Text="Unused Type")
        """

    def genLog(self, Perfixs=[], Text="", Type="INFO", SaveToFile=True) -> None:
        if not (Type in self.Configs["Types"]): Type == "INFO"
        if (Type == "DEBUG") and (self.Configs["Debug"] == False): return None
        if type(Text) == type(list()): Text = str().join(Text)

        Perfix = ""

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
        print(FullLog, end="")
