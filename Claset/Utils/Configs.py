# -*- coding: utf-8 -*-
"""生成, 更新, 降级配置文件"""

from logging import getLogger
from re import compile as reCompile

from .Path import pathAdder
from .File import loadFile, saveFile, dfCheck

from . import Confs
from .Exceptions import Configs as Ex_Configs

Logger = getLogger(__name__)


class Configs():
    """管理日志"""
    reFindTypeAndKey = reCompile(r"([a-zA-Z0-9_]+):(.+)")
    reFindOldAndNew = reCompile(r"(.+)->(.*)")
    reIFStrList = reCompile(r"^\[.*\]")

    def __init__(self):
        # 执行初始任务
        dfCheck(Path="$CONFIG/", Type="dm")
        PathsPath = pathAdder("$CONFIG/", Confs.ConfigIDs["Paths"])
        if dfCheck(Path=PathsPath, Type="f") == False: self.genConfig(ID="Paths", Path=PathsPath)

        SettingsPath = pathAdder("$CONFIG/", Confs.ConfigIDs["Settings"])
        if dfCheck(Path=SettingsPath, Type="f") == False: self.genConfig(ID="Settings", Path=SettingsPath)


    def getConfig(self, ID: str, TargetVersion: int | None = None, FilePath: str | None = None) -> dict:
        """
        通过配置文件 ID 取得配置文件
        * ID: 配置文件ID, 可通过 Claset.Utils.Confs.ConfigIDs.keys() 获取当前已注册的所有ID
        * TargetVersion: 目标版本, 若为 None 则不检查版本, 若为 0 则使用最新版本
        * FilePath: 目标文件路径, 若不为 None 则判断为非全局配置文件
        """
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigUnregistered(ID)

        # 如果指定了文件位置, 类型将判断为非全局
        if FilePath == None:
            FilePath = "$CONFIG/" + Confs.ConfigIDs[ID]

        # 判断配置文件是否存在, 存在则查看是否需要检查更新, 不存在则生成配置文件
        if dfCheck(Path=FilePath, Type="f") == False: self.genConfig(ID=ID, Path=FilePath, OverWrite=False)
        elif TargetVersion != None: self.checkUpdate(ID=ID, TargetVersion=TargetVersion, FilePath=FilePath)
        # 读取文件并返回数据
        return(loadFile(Path=FilePath, Type="json"))


    def checkUpdate(self, ID: str, TargetVersion: int, FilePath: str, Type: str = "!=") -> bool:
        """
        通过配置文件 ID 取得全局类型的配置文件
        * ID: 配置文件ID, 可通过 Claset.Utils.Confs.ConfigIDs.keys() 获取当前已注册的所有ID
        * TargetVersion: 目标版本
        * Type: 判定其是否需要更新的三种类型("!=", ">=", "<="), 当前版本为左值, 目标版本为右值\n
        若更新了配置则返回True, 反之则返回False
        """
        # 获取当前版本号
        NowConfigVersion = loadFile(FilePath, "json")["VERSION"]

        # 判断是否需要更新
        if ((Type == "!=") and (NowConfigVersion != TargetVersion)): pass
        elif ((Type == ">=") and (NowConfigVersion >= TargetVersion)): pass
        elif ((Type == "<=") and (NowConfigVersion <= TargetVersion)): pass
        else: return(False)

        # 尝试进行更新
        try:
            self.updateConfig(ID=ID, Path=FilePath, NowVersion=NowConfigVersion, TargetVersion=TargetVersion)
        except Exception as INFO:
            Logger.warning("Updating Config (%s) Error! INFO: %s", ID, INFO)
            return(False)
        return(True)


    def genConfig(self, ID: str, Path: str, OverWrite: bool = True) -> None:
        """生成配置文件"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigUnregistered(ID)
        if (dfCheck(Path=Path, Type="f") and (OverWrite == False)): raise Ex_Configs.ConfigExist(ID)

        FileContent = self.setVersion(Config=Confs.ConfigInfos["File"][ID], Version=Confs.ConfigInfos["Version"][ID])
        Logger.info("Created Config: %s", ID)
        saveFile(Path=Path, FileContent=FileContent, Type="json")


    def updateConfig(self, ID: str, Path: str, TargetVersion: int, NowVersion: int = None, OverWrite: bool = True) -> None:
        """更新或降级配置文件版本(NowVersion)至目标版本(TargetVersion)"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigUnregistered(ID)
        if (dfCheck(Path=Path, Type="f") and (OverWrite == False)): raise Ex_Configs.ConfigExist(ID)

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
            Type, Key = self.reFindTypeAndKey.search(Difference).groups()
            if Type in ["REPLACE", "DELETE"]:
                NewConfig = self.processConfig(OldConfig=OldConfig, Key=Key, Type=Type)
            else: raise Ex_Configs.UnknownDifferenceType
        NewConfig = self.setVersion(Config=NewConfig, Version=TargetVersion)

        saveFile(Path=Path, FileContent=NewConfig, Type="json")


    def getDifferenceS(self, ID: str, NowVersion: int, TargetVersion: int, Reverse: bool = False) -> list[str]:
        """取得版本之间的所有差异"""
        if ID not in Confs.ConfigIDs.keys(): raise Ex_Configs.ConfigUnregistered(ID)
        Differences = Confs.ConfigInfos["Difference"][ID]
        ChangeList = list()
        DifferenceS = list()

        for DifferentsKey in Differences:
            Old, New = self.reFindOldAndNew.search(DifferentsKey).groups()
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


    def setVersion(self, Config: dict, Version: int | str) -> dict:
        """设置版本"""
        return(self.__SetToDict(Keys=["VERSION"], Dict=Config, Type="REPLACE", Do=int(Version)))


    def processConfig(self, OldConfig: dict, Key: str, Type: str) -> dict:
        """对配置文件的各种操作"""
        match Type:
            case "REPLACE":
                Old, New = self.reFindOldAndNew.search(Key).groups()
            case "DELETE":
                Old = Key
                New = None

        if self.reIFStrList.search(Old.strip()) != None: Old = self.__StrList2List(Old)
        else: Old = [Old]
        return(self.__SetToDict(Keys=Old, Dict=OldConfig, Type=Type, Do=New))


    def __StrList2List(self, Key: str) -> list:
        """转化 String 格式的 List 至 List 格式"""
        return(Key.replace("[", "").replace("]", "").replace(",", " ").split())


    def __SetToDict(self, Keys: list, Dict: dict, Type: str, Do: str | bool | float | int | None = None) -> dict:
        """
        将设置写入 Dict
        * Keys: 字典键的列表
        * Dict: 输入
        * Type: 操作类型
        * Do: 替换为
        """
        if len(Keys) > 1:
            if Dict.get(Keys[0]) == None: Dict[Keys[0]] = dict()
            Dict[Keys[0]] = self.__SetToDict(Keys=Keys[1:], Dict=Dict[Keys[0]], Type=Type, Do=Do)
            return(Dict)
        elif len(Keys) == 1:
            if Type == "REPLACE":
                # 尝试修正输入类型
                if type(Do) == type(str()):
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

