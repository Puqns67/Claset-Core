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

        self.AssetsVersion = self.Json.get("assets")
        self.ComplianceLevel = self.Json.get("complianceLevel")
        self.MinimumLauncherVersion = self.Json.get("minimumLauncherVersion")
        self.MainClass = self.Json.get("mainClass")
        self.Type = self.Json.get("type")
        self.Version = self.Json.get("version")

        # 兼容来自 HMCL 的配置文件
        if "patches" in self.Json:
            for i in self.Json["patches"]:
                if i.get("id") == "game":
                    if self.AssetsVersion is None: self.AssetsVersion = i.get("assets")
                    if self.ComplianceLevel is None: self.ComplianceLevel = i.get("complianceLevel")
                    if self.MinimumLauncherVersion is None: self.MinimumLauncherVersion = i.get("minimumLauncherVersion")
                    if self.MainClass is None: self.MainClass = i.get("mainClass")
                    if self.Type is None: self.Type = i.get("type")
                    if self.Version is None: self.Version = i.get("version")
                    break

        self.ID = self.Json.get("id")
        self.JarName = self.Json.get("jar")

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
        self.full()
        return((self.Name, self.Version, self.Type, self.Dir,))


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
        try:
            VersionNames = listdir(path=path("$VERSION"))
        except FileNotFoundError:
            return(list())
    elif isinstance(VersionNames, str):
        VersionNames = [VersionNames]
    Output: list[VersionInfos] = list()
    for VersionName in VersionNames:
        VersionInfosObject = VersionInfos(VersionName=VersionName)
        if not VersionInfosObject.check():
            continue
        VersionInfosObject.full()
        Output.append(VersionInfosObject)
    return(Output)

