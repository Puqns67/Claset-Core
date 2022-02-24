# -*- coding: utf-8 -*-
"""格式化路径"""

from json import load
from os import getcwd
from os.path import abspath
from re import compile as ReCompile

from .Confs.Paths import File
from .Exceptions.Path import SearchError, PrefixsMissingKey

PathRegex = ReCompile(r"^(.*)\$([a-zA-Z]*)(.*)$")
PathConfigs = None
PathConfigKeys = None


def path(Input: str, IsPath: bool = False) -> str:
    """格式化路径"""
    global PathConfigs
    global PathConfigKeys

    if PathConfigs == None:
        try:
            with open(getcwd() + "/Claset/Paths.json") as ConfigFile:
                PathConfigs = load(ConfigFile)["Prefixs"]
        except FileNotFoundError:
            PathConfigs = File["Prefixs"]
        PathConfigKeys = PathConfigs.keys()

    while "$" in Input:
        Matched = PathRegex.match(Input)
        if Matched == None: raise SearchError
        Groups = list(Matched.groups())
        if Groups[1] == None: raise SearchError
        elif Groups[1] == "PREFIX": Groups[1] = getcwd()
        elif Groups[1] in PathConfigKeys: Groups[1] = PathConfigs[Groups[1]]
        else: raise PrefixsMissingKey(Groups[1])
        Input = str().join(Groups)

    if IsPath == True:
        Input = abspath(Input)

    return(Input)


def pathAdder(*Paths: list | tuple | str) -> str:
    """拼接路径片段并格式化"""
    PathList = list()
    for i in Paths:
        if isinstance(i, str):
            PathList.append(i)
        elif isinstance(i, (list, tuple,)):
            PathList.extend(i)
        elif isinstance(i, (int, float,)):
            PathList.append(str(i))
    Path = "/".join(PathList)
    if "$" in Path: Path = path(Path)
    return(abspath(Path))

