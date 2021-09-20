#VERSION=7
#
#Claset/Base/AdvancedPath.py
#高级地址转换
#

from os import getcwd
from os.path import abspath
from re import compile as recompile

from .Loadfile import loadFile
from .Configs import Configs


class path():
    class rekeys():
        def __init__(self):
            self.SearchFile = recompile(r"&F<(.+)>.+")
            self.SearchVariable = recompile(r".+&V<(.+)>.*")

    def __init__(self, Others=False, OtherTypes=[], DisableabsPath=True):
        self.Configs = Configs().getConfig("Paths")
        self.OthersType = Others
        self.DisableabsPath = DisableabsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]

        if self.OthersType == True:
            self.ReSearch = self.rekeys()
            self.getFromOthersKeys(OtherTypes)


    def loadOtherString(self, Objects, ID=0):
        # 如不存在已加载的 ReSearch 则加载
        if self.ReSearch == None:
            self.ReSearch = self.rekeys()

        FindFile = self.ReSearch.SearchFile.match(Objects[ID])

        if FindFile == None:
            return(Objects[ID])
        else:
            File = Configs().getConfig(FindFile.group(1))
            Variables = []
            OVariables = []

            while True:# 反向读取 Variables
                Finded = self.ReSearch.SearchVariable.match(Objects[ID])
                if Finded == None:
                    break
                else:
                    Variables.append(Finded.group(1))
                    Objects[ID] = Objects[ID].replace("&V<" + Finded.group(1) + ">", "")

            if len(Variables) != 1:# 反转列表
                Variables.reverse()

            for vid in Variables:# 迭代 load id
                try:
                    ivid = int(vid)
                except ValueError:
                    OVariables.append(vid)
                else:
                    print(Objects, ivid)
                    OVariables.append(self.loadOtherString(Objects, ID=ivid))

            for ovid in OVariables:# 获取
                print(File)
                File = File[ovid]

            self.OthersType = True

            return(File)


    def getFromOthersKeys(self, OtherTypes):
        if len(OtherTypes) == 0:
            OthersKeys = self.Configs["Others"]
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

