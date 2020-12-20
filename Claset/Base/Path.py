#VERSION=4
#
#Claset/Base/Path.py
#地址转换
#

from json import load
from os import getcwd
from os.path import abspath

def path(init, DisableabsPath=True):
    with open(getcwd() + "/Claset/Configs/Paths.json") as config: 
        Config = load(config)["Prefixs"]
    
    ConfigKeys = Config.keys()

    while "$" in init:
        for i in ConfigKeys:
            if "$PREFIX" in init:
                init = init.replace("$PREFIX", getcwd())
                break
            if i in init:
                init = init.replace("$" + i, Config[i])

    if DisableabsPath == False:
        init = abspath(init)

    return(init)
