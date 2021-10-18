#VERSION=4
#
#Claset\Base\Configs.py
#生成, 更新, 降级配置文件
#

from re import compile as reCompile

from . import Confs
from .Exceptions import Configs as Ex_Configs
from .File import loadFile, saveFile
from .DFCheck import dfCheck


ConfigIDs = {
    "Download": "Download.json",
    "Paths": "Paths.json",
    "Logs": "Logs.json",
    "Mirrors": "GameDownloadMirrors.json",
    "Settings": "Settings.json"
}

class Configs():
    def __init__(self, Logger=None, LoggerHeader: list | str | None = None):
        # 定义全局 Logger
        if Logger != None:
            self.Logger = Logger
            if LoggerHeader != None:
                self.LogHeader = self.Logger.logHeaderAdder(LoggerHeader, ["Configs"])
            else: self.LoggerHeader = ["Configs"]
        else: self.Logger = None

        self.reCompiles = None

        # 执行初始任务
        dfCheck(Path="$CONFIG/", Type="dm")
        if dfCheck(Path="$CONFIG/" + ConfigIDs["Paths"], Type="f") == False:    self.genConfig("Paths", "$CONFIG/" + ConfigIDs["Paths"])
        if dfCheck(Path="$CONFIG/" + ConfigIDs["Settings"], Type="f") == False: self.genConfig("Settings", "$CONFIG/" + ConfigIDs["Settings"])


    # 取得配置文件
    def getConfig(self, ID: str, TargetLastVersion: str | None = None) -> dict:
        if ID not in ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered(ID)
        FilePath = "$CONFIG/" + ConfigIDs[ID]
        if dfCheck(Path=FilePath, Type="f") == False: self.genConfig(ID, FilePath)

        # 在要求特定的版本时检查配置文件版本，如异常则尝试更新配置文件
        if TargetLastVersion != None:
            NowConfigVersion = loadFile(FilePath, "json")["VERSION"]
            if NowConfigVersion != TargetLastVersion:
                try:
                    self.updateConfig(ID, FilePath, NowVersion=NowConfigVersion, TargetVersion=TargetLastVersion)
                except Exception as INFO:
                    if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["getConfig"], Text=["Updating Config (", ID, ") Error! INFO: ", INFO], Type="WARN")

        return(loadFile(FilePath, "json"))


    # 生成配置文件
    def genConfig(self, ID: str, Path: str, OverWrite: bool = True) -> None:
        if ID not in ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered
        if dfCheck(Path=Path, Type="f") and (OverWrite == False): raise Ex_Configs.ConfigsExist(ID)

        saveFile(Path=Path, FileContent=self.getInfoFromClass(ID, "File"), Type="json")


    # 从 Confs 类获得相关数据
    def getInfoFromClass(self, ID: str, Type: str):
        match Type:
            case "Version":
                match ID:
                    case "Paths":    return(Confs.Paths.LastVersion)
                    case "Download": return(Confs.Download.LastVersion)
                    case "Settings": return(Confs.Settings.LastVersion)
                    case "Logs":     return(Confs.Logs.LastVersion)
                    case "Mirrors":  return(Confs.Mirrors.LastVersion)
            case "File":
                match ID:
                    case "Paths":    return(Confs.Paths.File)
                    case "Download": return(Confs.Download.File)
                    case "Settings": return(Confs.Settings.File)
                    case "Logs":     return(Confs.Logs.File)
                    case "Mirrors":  return(Confs.Mirrors.File)
            case "Difference":
                match ID:
                    case "Paths":    return(Confs.Paths.Difference)
                    case "Download": return(Confs.Download.Difference)
                    case "Settings": return(Confs.Settings.Difference)
                    case "Logs":     return(Confs.Logs.Difference)
                    case "Mirrors":  return(Confs.Mirrors.Difference)


    # 生成所有的正则对象
    def genReCompiles(self):
        if self.reCompiles == None:
            self.reCompiles = {
                "FindType&Key": reCompile(r"([a-zA-Z0-9_]+):(.+)"),
                "FindOld&New": reCompile(r"(.+)->(.*)"),
                "IFStrList": reCompile(r"^\[.*\]")
            }


    # 更新或降级配置文件版本(NowVersion)至目标版本(TargetVersion)
    def updateConfig(self, ID: str, Path: str, TargetVersion: int, NowVersion: int = None, OverWrite: bool = True) -> None:
        if ID not in ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered
        if dfCheck(Path=Path, Type="f") and (OverWrite == False): raise Ex_Configs.ConfigsExist(ID)

        self.genReCompiles()
        NewConfig = loadFile("$CONFIG/" + ConfigIDs[ID], "json")
        if NowVersion == None: NowVersion = NewConfig["VERSION"]
        if TargetVersion == 0:
            TargetVersion = self.getInfoFromClass(ID, "Version")
            if TargetVersion == NowVersion: return(None)

        if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["updateConfig"], Text=["Update Config (", ID, ") From Version ", NowVersion, " to Version ", TargetVersion])
        if TargetVersion < NowVersion: Reverse = True
        else: Reverse = False

        DifferenceS = self.getDifferenceS(ID=ID, TargetVersion=TargetVersion, NowVersion=NowVersion, Reverse=Reverse)

        for Difference in DifferenceS:
            Type, Key = self.reCompiles["FindType&Key"].search(Difference).groups()
            if Type in ["REPLACE", "DELETE"]:
                NewConfig = self.processConfig(NewConfig, Key, Type)

        saveFile(Path=Path, FileContent=NewConfig, Type="json")


    # 取得版本之间的所有差异
    def getDifferenceS(self, ID: str, NowVersion: int, TargetVersion: int, Reverse: bool = False) -> list:
        if ID not in ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered
        self.genReCompiles()
        Differences = self.getInfoFromClass(ID, Type="Difference")
        ChangeList = list()
        DifferenceS = list()

        for DifferentsKey in Differences:
            Old, New = self.reCompiles["FindOld&New"].search(DifferentsKey).groups()
            ChangeList.append([int(Old), int(New)])
        ChangeList = sorted(ChangeList, key=lambda ChangeList: ChangeList[0], reverse=Reverse)

        for DifferentsKey in ChangeList:
            if Reverse == False:
                if (NowVersion <= DifferentsKey[0]) and (TargetVersion >= DifferentsKey[1]):
                    DifferenceS.extend(Differences[str(DifferentsKey[0]) + "->" + str(DifferentsKey[1])])
            else:
                if (NowVersion >= DifferentsKey[0]) and (TargetVersion <= DifferentsKey[1]):
                    DifferenceS.extend(reversed(Differences[str(DifferentsKey[0]) + "->" + str(DifferentsKey[1])]))
        if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["getDifferenceS"], Text=["Config (", ID, ")'s Differents: ", DifferenceS], Type="DEBUG")
        return(DifferenceS)


    # 对配置文件的各种操作
    def processConfig(self, OldConfig: dict, Key: str, Type: str) -> dict:
        self.genReCompiles()
        if Type == "DELETE":
            Old = Key
            New = str()
        else: Old, New = self.reCompiles["FindOld&New"].search(Key).groups()
        if self.reCompiles["IFStrList"].search(Old.strip()) != None:
            Old = self.__StrList2List(Old)
        else: Old = [Old]
        return(self.__SetToDict(Keys=Old, Dict=OldConfig, Type=Type, Do=New))


    # 转化 String 格式的 List 至 List 格式
    def __StrList2List(self, Key: str) -> list:
        return(Key.replace("[", "").replace("]", "").replace(",", " ").split())


    # 将设置写入 Dict
    def __SetToDict(self, Keys: list, Dict: dict, Type: str, Do=None) -> dict:
        if len(Keys) > 1:
            if Dict.get(Keys[0]) == None: Dict[Keys[0]] = dict()
            Dict[Keys[0]] = self.__SetToDict(Keys=Keys[1:], Dict=Dict[Keys[0]], Type=Type, Do=Do)
            return(Dict)
        elif len(Keys) == 1:
            if Type == "REPLACE":
                # 尝试修正输入类型
                if Do in ["True", "False", "Null", "None"]:
                    if   Do == "True":  Do = True
                    elif Do == "False": Do = False
                    elif Do in ["Null", "None"]:  Do = None
                elif Do[-1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    try: Do = int(Do)
                    except ValueError:
                        try: Do = float(Do)
                        except ValueError: pass
                Dict[Keys[0]] = Do
                return(Dict)
            elif Type == "DELETE":
                try:
                    Dict.pop(Keys[0])
                except KeyError:
                    pass
                return(Dict)

