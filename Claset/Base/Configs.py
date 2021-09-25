#VERSION=1
#
#Claset\Base\Configs.py
#生成, 更新, 降级配置文件
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
    def getConfig(self, ID: str, TargetLastVersion: str = None) -> dict:
        if ID not in ConfigIDs.keys(): raise Exceptions.Configs.ConfigsUnregistered(ID)
        FilePath = "$CONFIG/" + ConfigIDs[ID]
        if dfCheck("f", FilePath) == False: self.genConfig(ID, FilePath)

        # 在要求特定的版本时检查配置文件版本，如异常则尝试更新配置文件
        if TargetLastVersion != None:
            NowConfigVersion = loadFile(FilePath, "json")["VERSION"]
            if NowConfigVersion != TargetLastVersion:
                if NowConfigVersion > TargetLastVersion: self.downgradeConfig(ID, NowConfigVersion, TargetLastVersion)
                else: self.updateConfig(ID, NowConfigVersion, TargetLastVersion)

        return(loadFile(FilePath, "json"))


    # 生成配置文件
    def genConfig(self, ID: str, Path: str, OverWrite: bool = True) -> None:
        if ID not in ConfigIDs.keys(): raise Exceptions.Configs.ConfigsUnregistered
        if dfCheck("f", Path) and (OverWrite == False): raise Exceptions.Configs.ConfigsExist(ID)

        saveFile(Path, filecontent=self.getInfoFromClass("Paths", "File"), filetype="json")


    def getInfoFromClass(self, ID: str, Type: str):
        if   Type == "Version":
            if   ID == "Paths":    return(Confs.Paths.getLastVersion())
            elif ID == "Download": return(Confs.Download.getLastVersion())
            elif ID == "Settings": return(Confs.Settings.getLastVersion())
            elif ID == "Logs":     return(Confs.Logs.getLastVersion())
            elif ID == "Mirrors":  return(Confs.Mirrors.getLastVersion())
        elif Type == "File":
            if   ID == "Paths":    return(Confs.Paths.getFile())
            elif ID == "Download": return(Confs.Download.getFile())
            elif ID == "Settings": return(Confs.Settings.getFile())
            elif ID == "Logs":     return(Confs.Logs.getFile())
            elif ID == "Mirrors":  return(Confs.Mirrors.getFile())
        elif Type == "Difference":
            if   ID == "Paths":    return(Confs.Paths.getDifference())
            elif ID == "Download": return(Confs.Download.getDifference())
            elif ID == "Settings": return(Confs.Settings.getDifference())
            elif ID == "Logs":     return(Confs.Logs.getDifference())
            elif ID == "Mirrors":  return(Confs.Mirrors.getDifference())


    # 生成所有的正则对象
    def genReCompiles(self):
        if self.reCompiles == None:
            self.reCompiles = {
                "FindType&Key": reCompile(r"([a-zA-Z0-9_]+):(.+)"),
                "FindOld&New": reCompile(r"(.+)->(.*)"),
                "IFStrList": reCompile(r"^\[.*\]")
            }


    # 降级配置文件版本(NowVersion)至目标版本(TargetLastVersion)
    def downgradeConfig(self, ID: str, NowVersion: int, TargetLastVersion: int):
        self.genReCompiles()


    # 更新配置文件版本(NowVersion)至目标版本(TargetLastVersion)
    def updateConfig(self, ID: str, NowVersion: int, TargetLastVersion: int):
        self.genReCompiles()
        NewConfig = loadFile("$CONFIG/" + ConfigIDs[ID], "json")
        DifferenceS = self.getInfoFromClass(ID, "Difference")
        
        for Difference in DifferenceS:
            Type, Key = self.reCompiles["FindType&Key"].search(Difference).groups()

            if   Type == "NEW":         NewConfig = self.__New(NewConfig, Key)
            elif Type == "DEL":         NewConfig = self.__Del(NewConfig, Key)
            elif Type == "CHANGEKEY":   NewConfig = self.__ChangeKey(NewConfig, Key)
            elif Type == "CHANGEVALUE": NewConfig = self.__ChangeValue(NewConfig, Key)
        
        return(NewConfig)


    # 对配置文件的各种操作
    def __New(self, OldConfig: dict, Key: str) -> dict:
        self.genReCompiles()
        Old, New = self.reCompiles["FindOld&New"].search(Key).groups()

        if self.reCompiles["IFStrList"].search(Old.strip()) != None:
            Old = self.__StrList2List(Old)
        else: Old = [Old]
        return(self.__SetToDict(Keys=Old, Dict=OldConfig, Type="Replace", Do=New))

    def __Del(self, OldConfig: dict, Key: str) -> dict:
        self.genReCompiles()
        pass

    def __ChangeKey(self, OldConfig: dict, Key: str) -> dict:
        self.genReCompiles()
        pass

    def __ChangeValue(self, OldConfig: dict, Key: str) -> dict:
        self.genReCompiles()
        pass
    
    def __StrList2List(self, Key: str) -> list:
        print(Key)
        return(Key.replace("[", "").replace("]", "").replace(",", " ").split(" "))

    def __SetToDict(self, Keys: list, Dict: dict, Type: str, Do=None) -> dict:
        if len(Keys) > 1:
            print(Keys, Dict)
            Dict[Keys[0]] = self.__SetToDict(Keys=Keys[1:], Dict=Dict[Keys[0]], Type=Type, Do=Do)
            return(Dict)
        elif len(Keys) == 1:
            if Type == "Replace":
                if Do in ["True", "False"]:
                    if Do == "True": Dict[Keys[0]] = True
                    if Do == "False": Dict[Keys[0]] = False
                else: Dict[Keys[0]] = Do
                return(Dict)
            if Type == "Del":
                Dict.pop(Keys[0])
                return(Dict)

