# VERSION=6
#
# Claset/Base/Path.py
# 地址转换
#

from json import load
from os import getcwd
from os.path import abspath

from .Confs.Paths import File


def path(input: str, DisableabsPath: bool = True) -> str:
    try:
        with open(getcwd() + "/Claset/Paths.json") as ConfigFile:
            Config = load(ConfigFile)["Prefixs"]
    except FileNotFoundError:
        Config = File

    ConfigKeys = Config.keys()

    while "$" in input:
        for i in ConfigKeys:
            if "$PREFIX" in input:
                input = input.replace("$PREFIX", getcwd())
                break
            if i in input:
                input = input.replace("$" + i, Config[i])

    if DisableabsPath == False:
        input = abspath(input)

    return(input)

