# -*- coding: utf-8 -*-

from os import listdir
from types import NoneType

from Claset.Utils import Configs, path, pathAdder, dfCheck, loadFile

__all__ = ("VersionInfos", "getVersionInfoList", "getVersionNameList",)


class VersionInfos():
    """实例相关信息的获取与实例的检查"""
    def __init__(self, VersionName: str, FullIt: bool = False):
        self.Name = VersionName
        if FullIt:
            self.full()
        else:
            self.ISFULL = False


    def full(self) -> None:
        """获取更多相关信息"""
        if self.ISFULL:
            return(None)

        self.Dir = pathAdder("$VERSION", self.Name)

        # 配置文件相关处理
        self.ConfigFilePath = pathAdder(self.Dir, "ClasetVersionConfig.json")
        self.Configs = Configs(ID="Game", FilePath=self.ConfigFilePath)

        # 版本 Json
        self.JsonPath = pathAdder(self.Dir, self.Name + ".json")
        self.Json: dict = loadFile(Path=self.JsonPath, Type="json")

        try:
            self.AssetsVersion = self.Json["assets"]
            self.ComplianceLevel = self.Json["complianceLevel"]
            self.MinimumLauncherVersion = self.Json["minimumLauncherVersion"]
            self.MainClass = self.Json["mainClass"]
            self.Type = self.Json["type"]
        except KeyError:
            ValueError("This Version's ({NAME}) version json is broken".format(NAME=self.Name))

        try:
            self.ID = self.Json["id"]
        except KeyError:
            self.ID = None

        try:
            self.JarName = self.Json["jar"]
        except KeyError:
            self.JarName = None

        try:
            self.Version = self.Json["version"]
        except KeyError:
            self.Version = None

        # Natives 文件夹位置
        self.NativesPath = pathAdder(self.Dir, "natives")

        if self.JarName is not None:
            self.JarPath = pathAdder(self.Dir, self.JarName + ".jar")
        else:
            self.JarPath = pathAdder(self.Dir, self.Name + ".jar")

        self.ISFULL = True


    def check(self) -> bool:
        """检查此版本是否可以正常被识别"""
        return(dfCheck(Path=pathAdder("$VERSION", self.Name, self.Name + ".json"), Type="f"))


    def getInfoList(self) -> tuple:
        """获取信息元组"""
        if not self.ISFULL:
            self.full()
        return((self.Name, self.Version, self.Type, self.Dir))


def getVersionNameList() -> list[str]:
    """获取已被识别的版本名列表"""
    Output: list[str] = list()
    VersionNameList = listdir(path=path("$VERSION"))
    for VersionName in VersionNameList:
        VersionInfosObject = VersionInfos(VersionName=VersionName)
        if not VersionInfosObject.check():
            continue
        Output.append(VersionName)
    return(Output)


def getVersionInfoList(VersionNames: list[str] | str | None = None) -> list[VersionInfos]:
    """获取输入的多个版本中已被识别的版本的信息"""
    if isinstance(VersionNames, NoneType):
        VersionNames = listdir(path=path("$VERSION"))
    if isinstance(VersionNames, str):
        VersionNames = [VersionNames]
    Output: list[VersionInfos] = list()
    for VersionName in VersionNames:
        VersionInfosObject = VersionInfos(VersionName=VersionName)
        if not VersionInfosObject.check():
            continue
        VersionInfosObject.full()
        Output.append(VersionInfosObject)
    return(Output)

