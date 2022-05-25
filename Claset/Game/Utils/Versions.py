# -*- coding: utf-8 -*-

from os import listdir
from types import NoneType
from typing import Iterable, Any

from Claset.Utils import (
    Configs,
    DownloadTask,
    dfCheck,
    loadFile,
    getValueFromDict,
    setValueToDict,
)

from .Others import Pather, genNativeDirName
from .LoadJson import Version_Client_DownloadTasks, AssetIndex_DownloadTasks


__all__ = (
    "VersionInfos",
    "getVersionInfoList",
    "getVersionNameList",
)


class VersionInfos:
    """实例相关信息的获取与实例的检查"""

    def __init__(self, VersionName: str, FullIt: bool = False):
        self.Name = VersionName
        if FullIt:
            self.full()
        else:
            self._FULL = False

    def full(self) -> None:
        """获取更多此版本的相关信息"""
        if self._FULL is True:
            return

        self.Dir = Pather.pathAdder("$VERSION", self.Name)

        # 配置文件相关处理
        self.GlobalConfig = Configs(ID="Settings")
        self.ConfigPath = Pather.pathAdder(self.Dir, "ClasetVersionConfig.json")
        self.Configs = Configs(ID="Game", FilePath=self.ConfigPath)

        # 版本 Json
        self.VersionJsonPath = Pather.pathAdder(self.Dir, self.Name + ".json")
        self.VersionJson: dict = loadFile(Path=self.VersionJsonPath, Type="json")

        self.ID = self.VersionJson.get("id")
        self.JarName = self.VersionJson.get("jar")
        self.AssetIndexVersion = self.VersionJson.get("assets")
        self.ComplianceLevel = self.VersionJson.get("complianceLevel")
        self.MinimumLauncherVersion = self.VersionJson.get("minimumLauncherVersion")
        self.MainClass = self.VersionJson.get("mainClass")
        self.Type = self.VersionJson.get("type")
        self.Version = self.VersionJson.get("version")

        # 兼容来自 HMCL 的配置文件
        if "patches" in self.VersionJson:
            for i in self.VersionJson["patches"]:
                if i.get("id") == "game":
                    if self.AssetIndexVersion is None:
                        self.AssetIndexVersion = i.get("assets")
                    if self.ComplianceLevel is None:
                        self.ComplianceLevel = i.get("complianceLevel")
                    if self.MinimumLauncherVersion is None:
                        self.MinimumLauncherVersion = i.get("minimumLauncherVersion")
                    if self.MainClass is None:
                        self.MainClass = i.get("mainClass")
                    if self.Type is None:
                        self.Type = i.get("type")
                    if self.Version is None:
                        self.Version = i.get("version")
                    break

        # AssetIndex Json
        if self.AssetIndexVersion is not None:
            self.AssetIndexJsonPath = Pather.pathAdder(
                "$MCAssetIndex", self.AssetIndexVersion + ".json"
            )
            if dfCheck(Path=self.AssetIndexJsonPath, Type="d"):
                self.AssetIndexJson = loadFile(
                    Path=self.AssetIndexJsonPath, Type="json"
                )
            else:
                self.AssetIndexJson = None
        else:
            self.AssetIndexVersion = None
            self.AssetIndexJson = None

        # Natives 文件夹位置
        self.NativesPath = Pather.pathAdder(
            self.Dir,
            genNativeDirName()
            if self.Configs["UnableGlobal"]["NativesDir"] == "AUTOSET"
            else self.Configs["UnableGlobal"]["NativesDir"],
        )

        if self.JarName is not None:
            self.JarPath = Pather.pathAdder(self.Dir, self.JarName + ".jar")
        else:
            self.JarPath = Pather.pathAdder(self.Dir, self.Name + ".jar")

        self._FULL = True

    def getInfoStr(
        self, Format: str = "{Name}|{Version}|{Type}|{Dir}", OtherKeys: dict = {}
    ) -> str:
        """
        获取信息字符串
        * Format: 格式字符串, 默认为 "{Name}|{Version}|{Type}|{Dir}"
        * OtherKeys: 其他的格式化键\n
        默认格式化键
        * Name: 版本名
        * Version: 游戏版本
        * Type: 版本类型
        * Dir: 所在文件夹
        """
        self.full()
        return Format.format(
            Name=self.Name,
            Version=self.Version,
            Type=self.Type,
            Dir=self.Dir,
            **OtherKeys
        )

    def check(self) -> bool:
        """检查此版本是否可以正常被识别"""
        return dfCheck(
            Path=Pather.pathAdder("$VERSION", self.Name, self.Name + ".json"),
            Type="f",
            NotFormat=True,
        )

    def checkFull(self) -> list[DownloadTask]:
        """检查此版本的内容缺失情况, 返回缺失文件的 DownloadTask 列表"""
        self.full()
        DownloadTasks = list()
        TempTasks = Version_Client_DownloadTasks(
            InitFile=self.VersionJson, Name=self.Name
        )
        TempTasks.extend(AssetIndex_DownloadTasks(InitFile=self.AssetIndexJson))
        for DownloadTask in TempTasks:
            if not (DownloadTask.checkExists() and DownloadTask.checkSha1()):
                DownloadTasks.append(DownloadTask)
        return DownloadTasks

    def getConfig(self, Keys: str | Iterable[str]) -> Any:
        """获取配置"""
        self.full()
        BaseKeys = Keys if isinstance(Keys, str) else Keys[0]

        if BaseKeys in self.Configs["Global"]:
            if self.Configs["UseGlobalConfig"]:
                return getValueFromDict(
                    Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]
                )
            else:
                Return = getValueFromDict(Keys=Keys, Dict=self.Configs["Global"])
                if Return is not None:
                    return Return
                return getValueFromDict(
                    Keys=Keys, Dict=self.GlobalConfig["GlobalConfig"]
                )
        else:
            return getValueFromDict(Keys=Keys, Dict=self.Configs["UnableGlobal"])

    def setConfig(
        self, Keys: str | Iterable[str], Value: Any, Save: bool = True
    ) -> None:
        """设置配置"""
        self.full()
        BaseKeys = Keys if isinstance(Keys, str) else Keys[0]

        if BaseKeys in self.Configs["Global"]:
            if self.Configs["UseGlobalConfig"]:
                self.Configs["UseGlobalConfig"] = False
            self.Configs["Global"] = setValueToDict(
                Keys=Keys, Value=Value, Dict=self.Configs["Global"]
            )
        else:
            self.Configs["UnableGlobal"] = setValueToDict(
                Keys=Keys, Value=Value, Dict=self.Configs["UnableGlobal"]
            )

        if Save:
            self.Configs.save()

    def reloadConfig(self) -> None:
        """重载配置文件"""
        self.Configs.reload()
        self.GlobalConfig.reload()


def getVersionNameList() -> list[str]:
    """获取已被识别的版本名列表"""
    Output: list[str] = list()
    VersionNameList = listdir(path=Pather.path("$VERSION"))
    for VersionName in VersionNameList:
        VersionInfosObject = VersionInfos(VersionName=VersionName)
        if not VersionInfosObject.check():
            continue
        Output.append(VersionName)
    return Output


def getVersionInfoList(
    VersionNames: Iterable[str] | str | None = None,
) -> list[VersionInfos]:
    """获取输入的多个版本中已被识别的版本的信息"""
    if isinstance(VersionNames, NoneType):
        try:
            VersionNames = listdir(path=Pather.path("$VERSION"))
        except FileNotFoundError:
            return tuple()
    elif isinstance(VersionNames, str):
        VersionNames = (VersionNames,)
    Output: list[VersionInfos] = list()
    for VersionName in VersionNames:
        VersionInfosObject = VersionInfos(VersionName=VersionName)
        if not VersionInfosObject.check():
            continue
        VersionInfosObject.full()
        Output.append(VersionInfosObject)
    return Output
