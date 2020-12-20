#VERSION=1
#
#Claset/Base/AdvancedPath.py
#高级地址转换
#

from re import compile as recompile
from os import getcwd
from os.path import abspath

from Claset.Base.Path import path as pathmd
from Claset.Base.Loadfile import loadfile

class rekeys():
    def __init__(self):
        self.SearchFile = recompile(r"&F<(.+)>.+")
        self.SearchVariable = recompile(r".+&V<(.+)>.*")

class path():
    def __init__(self, init=None, Others=False, DisableabsPath=True):
        self.Configs = loadfile("$EXEC/Configs/Paths.json", "json")
        self.OthersType = Others
        self.DisableabsPath = DisableabsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]

        if self.OthersType == True:
            self.getFromOthersKeys()

        if init != None:
            pathmd(init)


    def getFromOthersKeys(self):
        def load(self, Objects, ID=0):
            FindFile = self.ReSearch.SearchFile.match(Objects[ID])
            if FindFile == None:
                return(Objects[ID])
            else:
                File = loadfile(FindFile.group(1), "json")
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
                        OVariables.append(load(self, Objects, ID=ivid))

                for ovid in OVariables:#获取
                    File = File[ovid]

                self.OthersType = True

                return(File)

        if self.ReSearch == None:#如不存在已加载的ReSearch就加载他
            self.ReSearch = rekeys()

        for i in self.Configs["Others"]:#顺序获取之后再放入Perfixs
            loaded = load(self, i)
            for ii in loaded.keys():
                self.CompleteConfigs[ii] = loaded[ii]


    def path(self, init, Others=None):
            ConfigKeys = self.Configs["Prefixs"].keys()

            #如果启用了Others且未载过Others则通过getFromOthersKeys取得额外的Key
            if Others == True:
                if self.OthersType == False:
                    self.getFromOthersKeys()

            while "$" in init:
                for i in ConfigKeys:
                    if "$PREFIX" in init:
                        init = init.replace("$PREFIX", getcwd())
                    if i in init:
                        init = init.replace("$" + i, self.Configs["Prefixs"][i])

            if self.DisableabsPath == False:
                init = abspath(init)

            return(init)

    #
    #DEBUG
    #

    def printCompleteConfigs(self):
        print(self.CompleteConfigs)

