# -*- coding: utf-8 -*-
"""格式化路径"""


from json import load
from os import getcwd
from os.path import abspath
from re import compile as ReCompile

from .Confs.Paths import File
from .Exceptions import Path as Ex_Path

PathRegex = ReCompile(r"(.*)\$([a-zA-Z]*)(.*)")


def path(Input: str, IsPath: bool = False) -> str:
    """格式化路径"""
    try:
        with open(getcwd() + "/Claset/Paths.json") as ConfigFile:
            Config = load(ConfigFile)["Prefixs"]
    except FileNotFoundError:
        Config = File["Prefixs"]

    ConfigKeys = Config.keys()

    while "$" in Input:
        Match = PathRegex.search(Input)
        if Match == None: raise Ex_Path.SearchError
        Groups = list(Match.groups())
        if Groups[1] == None: raise Ex_Path.SearchError
        elif Groups[1] == "PREFIX": Groups[1] = getcwd()
        elif Groups[1] in ConfigKeys: Groups[1] = Config[Groups[1]]
        else: raise Ex_Path.PrefixsMissingKey(Groups[1])
        Input = str().join(Groups)

    if IsPath == True:
        Input = abspath(Input)

    return(Input)


def pathAdder(*paths: list | tuple | str) -> str:
    """拼接路径片段"""
    PathList = list()
    for i in paths:
        if type(i) == type(str()):
            PathList.append(i)
        elif (type(i) == type(list()) or type(i) == type(tuple())):
            PathList.extend(i)
        elif (type(i) == type(int()) or type(i) == type(float())):
            PathList.append(str(i))
    return(abspath("/".join(PathList)))

