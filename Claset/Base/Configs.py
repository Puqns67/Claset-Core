# -*- coding: utf-8 -*-
"""生成, 更新, 降级配置文件"""

from logging import getLogger
from re import compile as reCompile

from .File import loadFile, saveFile
from .DFCheck import dfCheck

from . import Confs
from .Exceptions import Configs as Ex_Configs

Logger = getLogger(__name__)


class Configs():
    """管理\获取日志"""
    def __init__(self):
        self.reCompiles = {
            "FindType&Key": reCompile(r"([a-zA-Z0-9_]+):(.+)"),
            "FindOld&New": reCompile(r"(.+)->(.*)"),
            "IFStrList": reCompile(r"^\[.*\]")
        }

        # 执行初始任务
        dfCheck(Path="$CONFIG/", Type="dm")
        if dfCheck(Path="$CONFIG/" + Confs.ConfigIDs["Paths"], Type="f") == False:    self.genConfig("Paths", "$CONFIG/" + Confs.ConfigIDs["Paths"])
        if dfCheck(Path="$CONFIG/" + Confs.ConfigIDs["Settings"], Type="f") == False: self.genConfig("Settings", "$CONFIG/" + Confs.ConfigIDs["Settings"])


    def getConfig(self, ID: str, TargetVersion: int | None = None) -> dict:
        """取得配置文件"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered(ID)
        FilePath = "$CONFIG/" + Confs.ConfigIDs[ID]
        if dfCheck(Path=FilePath, Type="f") == False: self.genConfig(ID, FilePath)

        # 在要求特定的版本时检查配置文件版本，如异常则尝试更新配置文件
        if TargetVersion != None:
            NowConfigVersion = loadFile(FilePath, "json")["VERSION"]
            if NowConfigVersion != TargetVersion:
                try:
                    self.updateConfig(ID, FilePath, NowVersion=NowConfigVersion, TargetVersion=TargetVersion)
                except Exception as INFO:
                    Logger.warning("Updating Config (%s) Error! INFO: %s", ID, INFO)

        return(loadFile(FilePath, "json"))


    def genConfig(self, ID: str, Path: str, OverWrite: bool = True) -> None:
        """生成配置文件"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered
        if dfCheck(Path=Path, Type="f") and (OverWrite == False): raise Ex_Configs.ConfigsExist(ID)

        Logger.info("Created Config: %s", ID)
        saveFile(Path=Path, FileContent=Confs.ConfigInfos["File"][ID], Type="json")


    def updateConfig(self, ID: str, Path: str, TargetVersion: int, NowVersion: int = None, OverWrite: bool = True) -> None:
        """更新或降级配置文件版本(NowVersion)至目标版本(TargetVersion)"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered
        if dfCheck(Path=Path, Type="f") and (OverWrite == False): raise Ex_Configs.ConfigsExist(ID)

        OldConfig = self.getConfig(ID=ID, TargetVersion=None)
        if NowVersion == None: NowVersion = OldConfig["VERSION"]
        if TargetVersion == 0:
            TargetVersion = Confs.ConfigInfos["Version"][ID]
            if TargetVersion == NowVersion: return(None)

        Logger.info("Update Config (%s) From Version %s to Version %s", ID, NowVersion, TargetVersion)
        if TargetVersion < NowVersion: Reverse = True
        else: Reverse = False

        DifferenceS = self.getDifferenceS(ID=ID, TargetVersion=TargetVersion, NowVersion=NowVersion, Reverse=Reverse)

        for Difference in DifferenceS:
            Type, Key = self.reCompiles["FindType&Key"].search(Difference).groups()
            if Type in ["REPLACE", "DELETE"]:
                NewConfig = self.processConfig(OldConfig=OldConfig, Key=Key, Type=Type)
            else: raise Ex_Configs.UnknownDifferenceType

        saveFile(Path=Path, FileContent=NewConfig, Type="json")


    def getDifferenceS(self, ID: str, NowVersion: int, TargetVersion: int, Reverse: bool = False) -> list:
        """取得版本之间的所有差异"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigsUnregistered
        Differences = Confs.ConfigInfos["Difference"][ID]
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
        Logger.debug("Config (%s)'s Differents: %s", ID, DifferenceS)
        return(DifferenceS)


    def processConfig(self, OldConfig: dict, Key: str, Type: str) -> dict:
        """对配置文件的各种操作"""
        if Type == "DELETE":
            Old = Key
            New = None
        else: Old, New = self.reCompiles["FindOld&New"].search(Key).groups()

        if self.reCompiles["IFStrList"].search(Old.strip()) != None: Old = self.__StrList2List(Old)
        else: Old = [Old]
        return(self.__SetToDict(Keys=Old, Dict=OldConfig, Type=Type, Do=New))


    def __StrList2List(self, Key: str) -> list:
        """转化 String 格式的 List 至 List 格式"""
        return(Key.replace("[", "").replace("]", "").replace(",", " ").split())


    def __SetToDict(self, Keys: list, Dict: dict, Type: str, Do: str | None = None) -> dict:
        """将设置写入 Dict"""
        if len(Keys) > 1:
            if Dict.get(Keys[0]) == None: Dict[Keys[0]] = dict()
            Dict[Keys[0]] = self.__SetToDict(Keys=Keys[1:], Dict=Dict[Keys[0]], Type=Type, Do=Do)
            return(Dict)
        elif len(Keys) == 1:
            if Type == "REPLACE":
                # 尝试修正输入类型
                if Do in ["True", "False", "Null", "None"]:
                    if    Do == "True":  Do = True
                    elif  Do == "False": Do = False
                    else: Do = None
                elif Do[-1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    try: Do = int(Do)
                    except ValueError:
                        # 若使用整型格式化失败则尝试浮点
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

