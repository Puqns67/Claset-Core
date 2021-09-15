#VERSION=5
#
#Claset/Base/AdvancedPath.py
#高级地址转换, 也许也可以用来转配置文件？
#

from os import getcwd
from os.path import abspath
from re import compile as recompile

from . import Loadfile


class path():
    class rekeys():
        def __init__(self):
            self.SearchFile = recompile(r"&F<(.+)>.+")
            self.SearchVariable = recompile(r".+&V<(.+)>.*")

    def __init__(self, Others=False, OtherTypes=[], DisableabsPath=True):
        self.Configs = Loadfile.loadFile("$EXEC/Configs/Paths.json", "json")
        self.OthersType = Others
        self.DisableabsPath = DisableabsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]

        if self.OthersType == True:
            self.ReSearch = self.rekeys()
            self.getFromOthersKeys(OtherTypes)


    def loadOtherString(self, Objects, ID=0):
        if self.ReSearch == None:#如不存在已加载的ReSearch就加载他
            self.ReSearch = self.rekeys()

        FindFile = self.ReSearch.SearchFile.match(Objects[ID])

        if FindFile == None:
            return(Objects[ID])
        else:
            File = Loadfile.loadFile(FindFile.group(1), "json")
            Variables = []
            OVariables = []

            while True:#反向读取Variables
                Finded = self.ReSearch.SearchVariable.match(Objects[ID])
                if Finded == None:
                    break
                else:
                    Variables.append(Finded.group(1))
                    Objects[ID] = Objects[ID].replace("&V<" + Finded.group(1) + ">", "")

            if len(Variables) != 1:#反转列表
                Variables.reverse()

            for vid in Variables:#迭代load id
                try:
                    ivid = int(vid)
                except ValueError:
                    OVariables.append(vid)
                else:
                    OVariables.append(self.loadOtherString(Objects, ID=ivid))

            for ovid in OVariables:#获取
                File = File[ovid]

            self.OthersType = True

            return(File)


    def getFromOthersKeys(self, OtherTypes):
        if len(OtherTypes) == 0:
            OthersKeys = self.Configs["Others"]
        else:
            OthersKeys = self.Configs["Others"] + OtherTypes

        for i in OthersKeys:#顺序获取之后再放入Perfixs
            loaded = self.loadOtherString(i)
            for ii in loaded.keys():
                self.CompleteConfigs[ii] = loaded[ii]

        CompleteConfigsList = sorted(self.CompleteConfigs, reverse=True)
        CompleteConfigs = dict()
        for i in CompleteConfigsList:
            CompleteConfigs[i] = self.CompleteConfigs[i]

        self.CompleteConfigs = CompleteConfigs


    def path(self, init, Others=False, DisableabsPath=True) -> str:
        #如果启用了Others且未载过Others则通过getFromOthersKeys取得额外的Key
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

    #
    #DEBUG
    #

    def printCompleteConfigs(self):
        print(self.CompleteConfigs)
        return(self.CompleteConfigs)

