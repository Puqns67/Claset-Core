#VERSION=9
#
#Claset/Base/AdvancedPath.py
#高级地址转换
#

from os import getcwd
from os.path import abspath
from re import compile as reCompile

from .File import loadFile
from .Configs import Configs
from .Logs import Logs

from .Exceptions.Configs import ConfigsUnregistered
from .Exceptions import AdvancedPath as Ex_AdvancedPath


class path():
    def __init__(self, Others: bool = False, OtherTypes: list = list(), DisableabsPath: bool = True, Logger: Logs | None = None, LoggerHeader: list | str | None = None):
        # 定义全局 Logger
        if Logger != None:
            self.Logger = Logger
            self.LogHeader = self.Logger.logHeaderAdder(LoggerHeader, "AdvancedPath")
        else:
            self.Logger = None
            self.LogHeader = "AdvancedPath"

        self.Configs = Configs(Logger=self.Logger, LoggerHeader=self.LogHeader).getConfig("Paths", TargetLastVersion=0)
        self.OthersType = Others
        self.DisableabsPath = DisableabsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]

        if self.OthersType == True:
            self.ReSearch = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>")
            self.getFromOthersKeys(OtherTypes)


    def loadOtherString(self, Objects: str) -> dict:
        if self.ReSearch == None: self.ReSearch = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>")

        try:
            File, Value = self.ReSearch.search(Objects).groups()
            File = Configs(Logger=self.Logger).getConfig(File, TargetLastVersion=0)
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
        self.CompleteConfigs = CompleteConfigs


    def path(self, init: str, Others: bool = False, DisableabsPath: bool = True) -> str:
        # 如果启用了 Others 且未载过 Others 则通过 getFromOthersKeys 取得额外的 Key
        if (Others == True) and (self.OthersType == False):             self.getFromOthersKeys()
        if (DisableabsPath == False) and (self.DisableabsPath == True): self.DisableabsPath = False

        ConfigKeys = self.CompleteConfigs.keys()

        while "$" in init:
            for i in ConfigKeys:
                if "$PREFIX" in init:
                        init = init.replace("$PREFIX", getcwd())
                if i in init:
                    init = init.replace("$" + i, self.CompleteConfigs[i])

        if self.DisableabsPath == False:
            init = abspath(init)
        return(init)

