# -*- coding: utf-8 -*-
"""生成, 更新, 降级配置文件"""

from logging import getLogger
from re import compile as reCompile
from typing import Any

from .File import loadFile, saveFile, dfCheck
from .Others import getValueFromDict, fixType

from .Confs import ConfigIDs, ConfigInfos
from .Exceptions import Configs as Ex_Configs

Logger = getLogger(__name__)


class Configs():
    """管理日志"""
    reFindTypeAndKey = reCompile(r"^([a-zA-Z0-9_]+):(.+)$")
    reFindOldAndNew = reCompile(r"^(.+)->(.*)$")
    reIFStrList = reCompile(r"^\[.*\]")

    def __init__(self, ID: str, TargetVersion: int = 0, FilePath: str | None = None, ProcessList: list = list()) -> None:
        if ID not in ConfigIDs: raise Ex_Configs.ConfigUnregistered(ID)
        self.ID = ID
        if TargetVersion == 0:
            self.TargetVersion = ConfigInfos["Version"][ID]
        else:
            self.TargetVersion = TargetVersion

        # 如果指定了文件位置, 类型将判断为非全局
        if FilePath == None:
            if ConfigInfos["Path"][ID] == "$NONGLOBAL$":
                raise Ex_Configs.ConfigNonGlobalMissingFilePath
            else:
                self.FilePath = "$CONFIG/" + ConfigInfos["Path"][ID]
        else: self.FilePath = FilePath

        self.TheConfig = self.getConfig()
        self.NowVersion = self.TheConfig["VERSION"]

        # 检查更新
        self.checkUpdate()

        if len(ProcessList) >= 1:
            self.updateConfig(Differences=ProcessList)


    def __str__(self) -> str:
        """实现str()"""
        return(self.ID)


    def __getitem__(self, Key) -> Any:
        """实现下标获取"""
        return(self.TheConfig[Key])


    def __setitem__(self, Key, Value) -> None:
        """实现下标写入"""
        self.TheConfig[Key] = Value


    def keys(self) -> list:
        return(list(self.TheConfig.keys()))


    def get(self, Keys: list | str) -> Any:
        if type(Keys) == type(str()): Keys = [Keys]
        try: return(getValueFromDict(Keys=Keys, Dict=self.TheConfig))
        except KeyError: return(None)


    def getConfig(self) -> dict:
        """取得配置文件"""
        # 判断配置文件是否存在, 存在则查看是否需要检查更新, 不存在则生成配置文件
        if dfCheck(Path=self.FilePath, Type="f") == False: self.genConfig(OverWrite=False)
        # 读取文件并返回数据
        return(loadFile(Path=self.FilePath, Type="json"))


    def checkUpdate(self, Type: str = "!=") -> bool:
        """
        通过配置文件 ID 取得全局类型的配置文件
        * Type: 判定其是否需要更新的三种类型("!=", ">=", "<="), 当前版本为左值, 目标版本为右值\n
        若更新了配置文件则返回True, 反之则返回False
        """
        # 判断是否需要更新
        if ((Type == "!=") and (self.NowVersion != self.TargetVersion)): pass
        elif ((Type == ">=") and (self.NowVersion >= self.TargetVersion)): pass
        elif ((Type == "<=") and (self.NowVersion <= self.TargetVersion)): pass
        else: return(False)

        # 尝试进行更新
        # try:
        self.updateConfig()
        # except Exception as INFO:
        #     Logger.warning("Updating Config (%s) Error! INFO: %s", self.ID, INFO)
        #     return(False)
        return(True)


    def genConfig(self, OverWrite: bool = True) -> None:
        """生成配置文件"""
        if (dfCheck(Path=self.FilePath, Type="f") and (OverWrite == False)): raise Ex_Configs.ConfigExist(self.ID)

        FileContent = self.setVersion(Config=ConfigInfos["File"][self.ID], Version=ConfigInfos["Version"][self.ID])

        saveFile(Path=self.FilePath, FileContent=FileContent, Type="json")
        Logger.info("Created Config: %s", self.ID)


    def saveConfig(self):
        """保存配置文件"""
        saveFile(Path=self.FilePath, FileContent=self.TheConfig, Type="json")


    def updateConfig(self, TargetVersion: int | None = None, Differences: list | None = None) -> None:
        """更新或降级配置文件版本至目标版本(TargetVersion)"""
        # 处理版本数据
        Logger.info("Update Config (%s) From Version %s to Version %s", self.ID, self.NowVersion, TargetVersion)

        if Differences != None:
            DifferenceS = Differences
        else:
            if TargetVersion == None:
                TargetVersion = self.TargetVersion
            if TargetVersion == 0:
                TargetVersion = ConfigInfos["Version"][self.ID]
                if TargetVersion == self.NowVersion: return(None)
            if TargetVersion < self.NowVersion:
                Reverse = True
            else:
                Reverse = False
            DifferenceS = self.getDifferenceS(TargetVersion=TargetVersion, Reverse=Reverse)

        for Difference in DifferenceS:
            Type, Key = self.reFindTypeAndKey.match(Difference).groups()
            NewConfig = self.processConfig(Key=Key, Type=Type)

        if Differences == None: NewConfig = self.setVersion(Config=NewConfig, Version=TargetVersion)

        saveFile(Path=self.FilePath, FileContent=NewConfig, Type="json")
        self.TheConfig = NewConfig


    def getDifferenceS(self, TargetVersion: int | None = None, Reverse: bool = False) -> list[str]:
        """取得版本之间的所有差异"""
        Differences = ConfigInfos["Difference"][self.ID]
        ChangeList = list()
        DifferenceS = list()

        if TargetVersion == None:
            TargetVersion = self.TargetVersion

        for DifferentsKey in Differences:
            Old, New = self.reFindOldAndNew.match(DifferentsKey).groups()
            ChangeList.append([int(Old), int(New)])
        ChangeList = sorted(ChangeList, key=lambda ChangeList: ChangeList[0], reverse=Reverse)

        for DifferentsKey in ChangeList:
            if Reverse == False:
                if (self.NowVersion <= DifferentsKey[0]) and (TargetVersion >= DifferentsKey[1]):
                    DifferenceS.extend(Differences[str(DifferentsKey[0]) + "->" + str(DifferentsKey[1])])
            else:
                if (self.NowVersion >= DifferentsKey[0]) and (TargetVersion <= DifferentsKey[1]):
                    DifferenceS.extend(reversed(Differences[str(DifferentsKey[0]) + "->" + str(DifferentsKey[1])]))
        Logger.debug("Config (%s)'s Differents: %s", self.ID, DifferenceS)
        return(DifferenceS)


    def setVersion(self, Config: dict, Version: int | str) -> dict:
        """设置版本"""
        return(self.__SetToDict(Keys=["VERSION"], Dict=Config, Type="REPLACE", Do=int(Version)))


    def processConfig(self, Key: str, Type: str) -> dict:
        """对配置文件的各种操作"""
        match Type:
            case "REPLACE":
                Old, New = self.reFindOldAndNew.search(Key).groups()
            case "DELETE":
                Old = Key
                New = None
            case _:
                raise Ex_Configs.UnknownDifferenceType

        if self.reIFStrList.search(Old.strip()) != None: Old = self.__StrList2List(Old)
        else: Old = [Old]
        return(self.__SetToDict(Keys=Old, Dict=self.TheConfig, Type=Type, Do=New))


    def __StrList2List(self, Key: str) -> list:
        """转化 String 格式的 List 至 List 格式"""
        return(Key.replace("[", str()).replace("]", str()).replace(",", " ").split())


    def __SetToDict(self, Keys: list, Dict: dict, Type: str, Do: Any | None = None) -> dict:
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
                    Do = fixType(Do)
                Dict[Keys[0]] = Do
                return(Dict)
            elif Type == "DELETE":
                try:
                    Dict.pop(Keys[0])
                except KeyError:
                    pass
                return(Dict)

