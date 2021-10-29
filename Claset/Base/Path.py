# VERSION=6
#
# Claset/Base/Path.py
# 地址转换
#

from json import load
from os import getcwd
from os.path import abspath
from re import compile as ReCompile

from .Confs.Paths import File

from .Exceptions import Path as Ex_Path

PathRegex = ReCompile(r"(.*)\$([a-zA-Z]*)(.*)")


def path(Input: str, IsPath: bool = False) -> str:
    try:
        with open(getcwd() + "/Claset/Paths.json") as ConfigFile:
            Config = load(ConfigFile)["Prefixs"]
    except FileNotFoundError:
        Config = File["Prefixs"]

    ConfigKeys = Config.keys()

    while "$" in Input:
        Groups = list(PathRegex.search(Input).groups())
        if Groups[1] == None: raise Ex_Path.SearchError
        elif Groups[1] == "PREFIX": Groups[1] = getcwd()
        elif Groups[1] in ConfigKeys: Groups[1] = Config[Groups[1]]
        else: raise Ex_Path.PerfixsMissingKey(Groups[1])
        Input = str().join(Groups)

    if IsPath == True:
        Input = abspath(Input)

    return(Input)

