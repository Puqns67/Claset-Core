#VERSION=0
#
#Claset\Base\Configs.py
#

from re import compile as reCompile

from . import Confs
from . import Exceptions
from .Savefile import saveFile
from .Loadfile import loadFile
from .DFCheck import dfCheck

ConfigIDs = {
    "Download": "Download.json",
    "Paths": "Paths.json",
    "Logs": "Logs.json",
    "Mirrors": "GameDownloadMirrors.json",
    "Settings": "Settings.json"
}

class Configs():
    def __init__(self):
        self.reCompiles = None
        dfCheck("dm", "$CONFIG/")
        if dfCheck("f", "$CONFIG/" + ConfigIDs["Paths"]) == False:    self.genConfig("Paths", "$CONFIG/" + ConfigIDs["Paths"])
        if dfCheck("f", "$CONFIG/" + ConfigIDs["Settings"]) == False: self.genConfig("Settings", "$CONFIG/" + ConfigIDs["Settings"])


    # 取得配置文件
    def getConfig(self, ID: str, TargetVersion: str = None) -> dict:
        if ID not in ConfigIDs.keys(): raise Exceptions.Configs.ConfigsUnregistered(ID)
        FilePath = "$CONFIG/" + ConfigIDs[ID]
        if dfCheck("f", FilePath) == False: self.genConfig(ID, FilePath)
            
        # 在要求特定的版本时检查配置文件版本，如异常则尝试更新配置文件
        if TargetVersion != None:
            NowConfigVersion = loadFile(FilePath, "json")["VERSION"]
            if NowConfigVersion != TargetVersion:
                if NowConfigVersion < TargetVersion: self.updateConfig(ID, NowConfigVersion, TargetVersion)
                else: self.downgradeConfig(ID, NowConfigVersion, TargetVersion)

        return(loadFile(FilePath, "json"))


    # 生成配置文件
    def genConfig(self, ID: str, Path: str, OverWrite: bool = True) -> None:
        if ID not in ConfigIDs.keys(): raise Exceptions.Configs.ConfigsUnregistered
        if dfCheck("f", Path) and (OverWrite == False): raise Exceptions.Configs.ConfigsExist(ID)

        if   ID == "Paths":    saveFile(Path, filecontent=Confs.Paths.getFile(), filetype="json")
        elif ID == "Download": saveFile(Path, filecontent=Confs.Download.getFile(), filetype="json")
        elif ID == "Settings": saveFile(Path, filecontent=Confs.Settings.getFile(), filetype="json")
        elif ID == "Logs":     saveFile(Path, filecontent=Confs.Logs.getFile(), filetype="json")
        elif ID == "Mirrors":  saveFile(Path, filecontent=Confs.Mirrors.getFile(), filetype="json")


    # 降级配置文件版本(NowVersion)至目标版本(TargetVersion)
    def downgradeConfig(self, ID, NowVersion, TargetVersion):
        if self.reCompiles == None: self.reCompiles = { "FindType&Key": reCompile(r"(a-zA-Z0-9_):(a-zA-Z0-9_)"), "FindOld&New": reCompile(r"(a-zA-Z0-9_)->([a-zA-Z0-9_]+)")}


    # 更新配置文件版本(NowVersion)至目标版本(TargetVersion)
    def updateConfig(self, ID, NowVersion, TargetVersion):
        if self.reCompiles == None: self.reCompiles = { "FindType&Key": reCompile(r"(a-zA-Z0-9_):(a-zA-Z0-9_)"), "FindOld&New": reCompile(r"(a-zA-Z0-9_)->([a-zA-Z0-9_]+)")}
