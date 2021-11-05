# -*- coding: utf-8 -*-
"""高级格式化路径"""

from os import getcwd
from os.path import abspath
from re import compile as reCompile

from .File import loadFile
from .Configs import Configs
from .Path import PathRegex

from Claset.Base.Exceptions.Configs import ConfigsUnregistered
from Claset.Base.Exceptions import Path as Ex_Path, AdvancedPath as Ex_AdvancedPath


class path():
    def __init__(self, Others: list | None = None, IsPath: bool = False):
        self.Configs = Configs().getConfig("Paths", TargetVersion=0)
        self.IsPath = IsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]
        self.CompleteConfigsKeys = self.CompleteConfigs.keys()

        if Others != None:
            self.ReSearch = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>")
            self.getFromOthersKeys(Others)


    def loadOtherString(self, Objects: str) -> dict:
        if self.ReSearch == None: self.ReSearch = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>")

        try:
            File, Value = self.ReSearch.search(Objects).groups()
            File = Configs().getConfig(File, TargetVersion=0)
        except AttributeError:
            raise Ex_AdvancedPath.SearchError
        except ConfigsUnregistered:
            File = loadFile(Path=File, Type="json")

        try:
            Value = self.loadOtherString(Value)
        except Ex_AdvancedPath.SearchError:
            pass

        return(File[Value])


    def getFromOthersKeys(self, OtherTypes: list) -> None:
        if len(self.Configs["Others"]) == 0:
            OthersKeys = OtherTypes
        else:
            OthersKeys = self.Configs["Others"] + OtherTypes

        # 顺序获取之后再放入 Perfixs
        for i in OthersKeys:
            loaded = self.loadOtherString(i)
            for ii in loaded.keys():
                self.CompleteConfigs[ii] = loaded[ii]

        CompleteConfigsList = sorted(self.CompleteConfigs, reverse=True)
        CompleteConfigs = dict()
        for i in CompleteConfigsList:
            CompleteConfigs[i] = self.CompleteConfigs[i]

        self.OthersType = True

        # 刷新数据
        self.CompleteConfigs = CompleteConfigs
        self.CompleteConfigsKeys = self.CompleteConfigs.keys()


    def path(self, Input: str, Others: list | None = None, IsPath: bool | None = None) -> str:
        """高级格式化路径"""
        # 如果启用了 Others 且未载过 Others 则通过 getFromOthersKeys 取得额外的 Key
        if ((Others != None) and (self.OthersType == False)): self.getFromOthersKeys(Others)
        if ((IsPath == False) and (self.IsPath == True)): self.IsPath = False

        while "$" in Input:
            Groups = list(PathRegex.search(Input).groups())
            if Groups[1] == None: raise Ex_Path.SearchError
            elif Groups[1] == "PREFIX": Groups[1] = getcwd()
            elif Groups[1] in self.CompleteConfigsKeys: Groups[1] = self.CompleteConfigs[Groups[1]]
            else: raise Ex_Path.PerfixsMissingKey(Groups[1])
            Input = str().join(Groups)

        if ((IsPath == True) or ((IsPath == None) and (self.IsPath == True))): Input = abspath(Input)

        return(Input)

