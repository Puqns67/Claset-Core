#
#Claset/Base/Path.py
#地址转换
#

from json import load
from os import getcwd

def path(init):
    with open(getcwd() + "/Claset/Configs/Paths.json") as openedjson: 
        config = load(openedjson)
    
    configkeys = config.keys()
    while "$" in init:
        for i in configkeys:
            if "$PREFIX" in init:
                init = init.replace("$PREFIX", getcwd())
                break
            if i in init:
                init = init.replace("$" + i, config[i])

    return(init)
