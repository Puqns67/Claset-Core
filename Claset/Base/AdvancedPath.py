#VERSION=8
#
#Claset/Base/AdvancedPath.py
#高级地址转换
#

from os import getcwd
from os.path import abspath
from re import compile as reCompile

from .Loadfile import loadFile
from .Configs import Configs

from .Exceptions import Configs as Ex_Configs
from .Exceptions import AdvancedPath as Ex_AdvancedPath


class path():
    def __init__(self, Others=False, OtherTypes=[], DisableabsPath=True):
        self.Configs = Configs().getConfig("Paths")
        self.OthersType = Others
        self.DisableabsPath = DisableabsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]

        if self.OthersType == True:
            self.ReSearch = self.ReSearch = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>")
            self.getFromOthersKeys(OtherTypes)


    def loadOtherString(self, Objects):
        if self.ReSearch == None: self.ReSearch = reCompile(r"^&F<([a-zA-Z0-9_]+)>&V<(.+)>")

        try:
            File, Value = self.ReSearch.search(Objects).groups()
            File = Configs().getConfig(File)
        except AttributeError:
            raise Ex_AdvancedPath.SearchError
        except Ex_Configs.ConfigsUnregistered:
            File = loadFile(File, "json")
        
        try:
            Value = self.loadOtherString(Value)
        except Ex_AdvancedPath.SearchError:
            pass

        return(File[Value])


    def getFromOthersKeys(self, OtherTypes):
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


    def path(self, init, Others=False, DisableabsPath=True) -> str:
        # 如果启用了 Others 且未载过 Others 则通过 getFromOthersKeys 取得额外的 Key
        if Others == True:
            if self.OthersType == False:
                self.getFromOthersKeys()

        if DisableabsPath == False:
            if self.DisableabsPath == True:
                self.DisableabsPath = False

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

