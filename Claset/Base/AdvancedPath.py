#VERSION=0
#
#Claset/Base/AdvancedPath.py
#高级地址转换
#

from re import compile as recompile
from json import load
from os import getcwd
from os.path import abspath

from Claset.Base.Path import path as pathmd
from Claset.Base.Loadfile import loadfile


class path():
    def __init__(self, init=None, Others=False, DisableabsPath=True):
        self.Configs = loadfile(":EXEC/Configs/Paths.json", "json")
        self.OthersType = Others
        self.DisableabsPath = DisableabsPath
        self.ReSearch = None
        self.CompleteConfigs = self.Configs["Prefixs"]

        if self.OthersType == True:
            self.getFromOthersKeys()

        if init != None:
            pathmd(init)


    def getFromOthersKeys(self):
        if self.ReSearch == None:
            self.ReSearch = recompile(r".*&<(.*?)\|(.*?)>.*")

        def get(Key, Re=self.ReSearch):
            while True:
                Output = Re.search(Key)
                geted = get(Output.group(2))
                loadfile(Output.group(1), "json")[geted]


        for i in self.Configs["Others"]:
            print(get(i))


    def path(self, init, Others=None, DisableabsPath=None):
        ConfigKeys = self.Configs["Prefixs"].keys()

        #如果启用了Others则通过getFromOthersKeys取得额外的Key
        if Others == True:
            if self.OthersType == False:
                self.getFromOthersKeys()

        while ":" in init:
            for i in ConfigKeys:
                if ":PREFIX" in init:
                    init = init.replace(":PREFIX", getcwd())
                if i in init:
                    init = init.replace(":" + i, self.Configs["Prefixs"][i])

        if DisableabsPath == False:
            init = abspath(init)

        return(init)
