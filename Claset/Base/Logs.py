#VERSION=7
#
#Claset/Base/Logs.py
#日志记录
#

from time import localtime, strftime

from . import Loadfile
from . import Path


class Logs():
    def __init__(self, LogPath="$EXEC/Logs/Log.log", Configs=None):
        if Configs == None:
            self.Configs = Loadfile.loadfile("$EXEC/Configs/Logs.json", "json")
        else:
            self.Configs = Configs

        if "$" in LogPath:
            LogPath = Path.path(LogPath)

        if self.Configs["ProgressiveWrite"] == True:
            self.LogPath = LogPath
            with open(self.LogPath, mode="w") as File:
                pass
        else:
            self.LogFile = open(LogPath, mode="w")



    def GenLog(self, Perfixs=[], Text="", Type="INFO", SaveToFile=True) -> None:
        if not (Type in self.Configs["Types"]): Type == "INFO"
        if (Type == "DEBUG") and (self.Configs["Debug"] == False): return None

        Perfix = ""

        #Perfixs
        if len(Perfixs) != 0:
            for Name in Perfixs:
                Perfix += self.Configs["Format"]["Perfix"].replace(r"{Name}", str(Name))
        
        #Text
        Text.replace(r"{Text}", Text)

        #Time
        Time = strftime(self.Configs["Format"]["Time"], localtime())

        FullLog = self.Configs["Format"]["FullLog"].replace(r"{Time}", Time).replace(r"{Type}", Type).replace(r"{Perfixs}", Perfix).replace(r"{Text}", Text) + "\n"

        if SaveToFile == True:
            if self.Configs["ProgressiveWrite"] == True:
                with open(self.LogPath, mode="a") as File:
                    File.write(FullLog)
            else:
                self.LogFile.write(FullLog)

        print(FullLog, end="")

        return None