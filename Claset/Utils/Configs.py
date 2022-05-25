# -*- coding: utf-8 -*-
"""生成, 更新, 降级配置文件"""

from logging import getLogger
from re import compile as reCompile
from typing import Iterable, Any
from json import JSONDecodeError

from .Path import path
from .File import loadFile, saveFile, dfCheck, removeFile
from .Others import getValueFromDict, fixType, ReMatchStrList

from .Confs import ConfigIDs, ConfigInfos
from .Exceptions import Configs as Ex_Configs

__all__ = ("Configs",)
Logger = getLogger(__name__)
ReFindTypeAndKey = reCompile(r"^\s*([A-Z]+):(.+)\s*$")
ReFindOldAndNew = reCompile(r"^\s*([\w\s,\[\]]+)->(\w+)\s*$")


class Configs:
    """管理日志"""

    def __init__(
        self,
        ID: str,
        TargetVersion: int = 0,
        FilePath: str | None = None,
        ProcessList: list = list(),
    ) -> None:
        if ID not in ConfigIDs:
            raise Ex_Configs.ConfigUnregistered(ID)
        self.ID = ID
        if TargetVersion == 0:
            self.TargetVersion = ConfigInfos["Version"][ID]
        else:
            self.TargetVersion = TargetVersion

        # 如果指定了文件位置, 类型将判断为非全局
        if FilePath is None:
            if ConfigInfos["Path"][ID] == "$NONGLOBAL$":
                raise Ex_Configs.ConfigNonGlobalMissingFilePath
            else:
                self.FilePath = path("$CONFIG/" + ConfigInfos["Path"][ID], IsPath=True)
        else:
            self.FilePath = path(FilePath, IsPath=True)

        self.TheConfig = self.getConfig()
        self.NowVersion = self.TheConfig["VERSION"]

        # 检查更新
        self.checkUpdate()

        if len(ProcessList) >= 1:
            self.updateConfig(Differences=ProcessList)

    def __str__(self) -> str:
        """实现str()"""
        return self.ID

    def __getitem__(self, Key: Any) -> Any:
        """实现下标获取"""
        return self.TheConfig[Key]

    def __setitem__(self, Key: Any, Value: Any) -> None:
        """实现下标写入"""
        self.TheConfig[Key] = Value

    def keys(self):
        """实现来着dict类型的keys()"""
        return self.TheConfig.keys()

    def get(self, Keys: Iterable, Fallback: Any | None = None) -> Any:
        if isinstance(Keys, str):
            Keys = (Keys,)
        try:
            return getValueFromDict(Keys=Keys, Dict=self.TheConfig)
        except KeyError:
            return Fallback

    def getConfig(self) -> dict:
        """取得配置文件"""
        # 判断配置文件是否存在, 存在则查看是否需要检查更新, 不存在则生成配置文件
        if not dfCheck(Path=self.FilePath, Type="f"):
            self.genConfig()
        # 读取文件并返回数据
        try:
            TheConfig = loadFile(Path=self.FilePath, Type="json")
        except JSONDecodeError:
            Logger.warning('Decode Config "%s" error, delete it', self.ID)
            removeFile(self.FilePath)
            self.genConfig()
            TheConfig = loadFile(Path=self.FilePath, Type="json")
        else:
            return TheConfig

    def checkUpdate(self, Type: str = "!=") -> bool:
        """
        通过配置文件 ID 取得全局类型的配置文件
        * Type: 判定其是否需要更新的三种类型("!=", ">=", "<="), 当前版本为左值, 目标版本为右值\n
        若更新了配置文件则返回True, 反之则返回False
        """
        # 判断是否需要更新
        if not (
            (Type == "!=")
            and (self.NowVersion != self.TargetVersion)
            or (Type == ">=")
            and (self.NowVersion >= self.TargetVersion)
            or (Type == "<=")
            and (self.NowVersion <= self.TargetVersion)
        ):
            return False

        # 尝试进行更新
        try:
            self.updateConfig()
        except Exception as INFO:
            Logger.warning("Updating Config (%s) Error! INFO: %s", self.ID, INFO)
            return False
        return True

    def genConfig(self, OverWrite: bool = True) -> None:
        """生成配置文件"""
        if dfCheck(Path=self.FilePath, Type="f") and (OverWrite == False):
            raise Ex_Configs.ConfigExist(self.ID)

        FileContent = self.setVersion(
            Config=ConfigInfos["File"][self.ID], Version=ConfigInfos["Version"][self.ID]
        )

        saveFile(Path=self.FilePath, FileContent=FileContent, Type="json")
        Logger.info("Created Config: %s", self.ID)

    def save(self) -> None:
        """保存配置文件"""
        saveFile(Path=self.FilePath, FileContent=self.TheConfig, Type="json")

    def reload(self) -> None:
        """从文件重载配置文件"""
        self.TheConfig = self.getConfig()

    def updateConfig(
        self, TargetVersion: int | None = None, Differences: Iterable[str] | None = None
    ) -> None:
        """更新或降级配置文件版本至目标版本(TargetVersion), 或是执行差异"""
        if Differences is not None:
            DifferenceS = Differences
        else:
            # 处理版本数据
            if TargetVersion:
                Logger.info(
                    "Update Config (%s) From Version %s to Version %s",
                    self.ID,
                    self.NowVersion,
                    TargetVersion,
                )
            else:
                Logger.info(
                    "Update Config (%s) From Version %s to last Version",
                    self.ID,
                    self.NowVersion,
                )

            if TargetVersion is None:
                TargetVersion = self.TargetVersion

            if TargetVersion == 0:
                TargetVersion = ConfigInfos["Version"][self.ID]
                if TargetVersion == self.NowVersion:
                    return None

            if TargetVersion < self.NowVersion:
                Reverse = True
            else:
                Reverse = False

            # TODO: 优化此处的逻辑(先拆再结合再拆)
            DifferenceS = self.getDifferenceS(
                TargetVersion=TargetVersion, Reverse=Reverse
            )
            self.TheConfig = self.setVersion(
                Config=self.TheConfig, Version=TargetVersion
            )

        for Difference in DifferenceS:
            Type, Key = ReFindTypeAndKey.match(Difference).groups()
            self.processConfig(Key=Key, Type=Type)

        self.save()

    def getDifferenceS(
        self, TargetVersion: int | None = None, Reverse: bool = False
    ) -> list[str]:
        """取得版本之间的所有差异"""
        Differences = ConfigInfos["Difference"][self.ID]
        ChangeList = list()
        DifferenceS = list()

        if TargetVersion is None:
            TargetVersion = self.TargetVersion

        for DifferentsKey in Differences:
            Old, New = ReFindOldAndNew.match(DifferentsKey).groups()
            ChangeList.append([int(Old), int(New)])

        ChangeList = sorted(
            ChangeList, key=lambda ChangeList: ChangeList[0], reverse=Reverse
        )

        for DifferentsKey in ChangeList:
            if Reverse == False:
                if (self.NowVersion <= DifferentsKey[0]) and (
                    TargetVersion >= DifferentsKey[1]
                ):
                    DifferenceS.extend(
                        Differences[
                            str(DifferentsKey[0]) + "->" + str(DifferentsKey[1])
                        ]
                    )
            else:
                if (self.NowVersion >= DifferentsKey[0]) and (
                    TargetVersion <= DifferentsKey[1]
                ):
                    DifferenceS.extend(
                        reversed(
                            Differences[
                                str(DifferentsKey[0]) + "->" + str(DifferentsKey[1])
                            ]
                        )
                    )
        Logger.debug("Config (%s)'s Differents: %s", self.ID, DifferenceS)
        return DifferenceS

    def setVersion(self, Config: dict, Version: int | str) -> dict:
        """设置版本"""
        return self.__SetToDict(
            Keys=["VERSION"], Dict=Config, Type="REPLACE", Do=int(Version)
        )

    def processConfig(self, Key: str, Type: str) -> dict:
        """对配置文件的各种操作"""
        if Type in (
            "REPLACE",
            "RENAME",
        ):
            Old, New = ReFindOldAndNew.match(Key).groups()
        elif Type == "DELETE":
            Old = Key
            New = None
        else:
            raise Ex_Configs.UndefinedDifferenceType(Type)

        # 修正类型
        if ReMatchStrList.match(Old) is not None:
            Old = ReMatchStrList.match(Old).groups()[0].replace(" ", str()).split(",")
        else:
            Old = (Old,)

        return self.__SetToDict(Keys=Old, Dict=self.TheConfig, Type=Type, Do=New)

    def __SetToDict(
        self, Keys: tuple | list, Dict: dict, Type: str, Do: Any | None = None
    ) -> dict:
        """
        将设置写入 Dict
        * Keys: 字典键的列表
        * Dict: 输入
        * Type: 操作类型
        * Do: 替换为
        """
        if len(Keys) > 1:
            if Dict.get(Keys[0]) is None:
                Dict[Keys[0]] = dict()
            Dict[Keys[0]] = self.__SetToDict(
                Keys=Keys[1:], Dict=Dict[Keys[0]], Type=Type, Do=Do
            )
            return Dict
        elif len(Keys) == 1:
            match Type:
                case "REPLACE":
                    # 尝试修正输入类型
                    if isinstance(Do, str):
                        Do = fixType(Do)
                    Dict[Keys[0]] = Do
                    return Dict
                case "DELETE":
                    try:
                        Dict.pop(Keys[0])
                    except KeyError:
                        pass
                    return Dict
                case "RENAME":
                    try:
                        Dict[Do] = Dict.pop(Keys[0])
                    except KeyError:
                        pass
                    return Dict
                case _:
                    ValueError(Type)
