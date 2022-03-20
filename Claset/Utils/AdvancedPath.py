# -*- coding: utf-8 -*-
"""高级格式化路径"""

from os import getcwd
from os.path import abspath
from re import compile as reCompile

from .File import loadFile
from .Configs import Configs
from .Path import PathRegex

from .Exceptions import Path as Ex_Path, AdvancedPath as Ex_AdvancedPath
from .Exceptions.Configs import ConfigUnregistered

__all__ = ("ReMatchLoadString", "AdvancedPath",)
ReMatchLoadString = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>$")


class AdvancedPath():
    def __init__(self, Others: list | None = None, IsPath: bool = False):
        self.Configs = Configs(ID="Paths")
        self.IsPath = IsPath
        self.CompleteConfigs: dict = self.Configs["Prefixs"]

        if Others is not None: self.getFromOthersKeys(Others)


    def loadOtherString(self, Objects: str) -> dict:
        """加载 Others 字符串"""
        try:
            File, Value = ReMatchLoadString.match(Objects).groups()
            File = Configs(File)
        except AttributeError:
            raise Ex_AdvancedPath.SearchError
        except ConfigUnregistered:
            File = loadFile(Path=File, Type="json")

        try: Value = self.loadOtherString(Value)
        except Ex_AdvancedPath.SearchError: pass

        return(File[Value])


    def getFromOthersKeys(self, OtherTypes: list) -> None:
        """从 Others 字符串列表取得额外的 Key"""
        if len(self.Configs["Others"]) == 0:
            OthersKeys = OtherTypes
        else:
            OthersKeys = self.Configs["Others"] + OtherTypes

        # 顺序获取之后再放入 Prefixs
        for i in OthersKeys:
            loaded = self.loadOtherString(i)
            for ii in loaded:
                self.CompleteConfigs[ii] = loaded[ii]

        CompleteConfigsList = sorted(self.CompleteConfigs, reverse=True)
        CompleteConfigs = dict()
        for i in CompleteConfigsList:
            CompleteConfigs[i] = self.CompleteConfigs[i]

        self.OthersType = True

        # 刷新数据
        self.CompleteConfigs = CompleteConfigs


    def path(self, Input: str, Others: list | None = None, IsPath: bool | None = None) -> str:
        """高级格式化路径"""
        # 如果启用了 Others 且未载过 Others 则通过 getFromOthersKeys 取得额外的 Key
        if (Others is not None) and (not self.OthersType): self.getFromOthersKeys(Others)
        if (not IsPath) and self.IsPath: self.IsPath = False

        while "$" in Input:
            try:
                Perfix, Matched, Suffix = PathRegex.match(Input).groups()
            except (AttributeError, ValueError):
                raise Ex_Path.SearchError(Input)
            match Matched:
                case "PREFIX": Matched = getcwd()
                case Matched if Matched in self.CompleteConfigs:
                    Matched = self.CompleteConfigs[Matched]
                case _: raise Ex_Path.PrefixsMissingKey(Matched)
            Input = f"{Perfix}{Matched}{Suffix}"

        if (IsPath or (IsPath is None and self.IsPath)):
            Input = abspath(Input)

        return(Input)


    def pathAdder(self, *Paths: list | tuple | str) -> str:
        """拼接路径片段并格式化"""
        PathList = list()
        for i in Paths:
            if isinstance(i, str):
                PathList.append(i)
            elif isinstance(i, (list, tuple,)):
                PathList.extend(i)
            elif isinstance(i, (int, float,)):
                PathList.append(str(i))
        Path = "/".join(PathList)
        if "$" in Path: Path = self.path(Path)
        return(abspath(Path))

