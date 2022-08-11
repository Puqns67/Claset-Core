# -*- coding: utf-8 -*-
"""格式化路径"""

from json import load
from os import getcwd, chdir
from os.path import abspath
from re import compile as ReCompile
from typing import Iterable

from .Confs.Paths import File
from .Exceptions.Path import SearchError, PrefixsMissingKey

__all__ = (
    "PathRegex",
    "path",
    "pathAdder",
    "setPerfix",
    "safetyPath",
)
PathRegex = ReCompile(r"^(.*)\$([a-zA-Z]*)(.*)$")
PathConfigs = None


def path(Input: str, IsPath: bool = False) -> str:
    """格式化路径"""
    global PathConfigs

    if PathConfigs is None:
        try:
            with open(getcwd() + "/Claset/Paths.json") as ConfigFile:
                PathConfigs = load(ConfigFile)["Prefixs"]
        except FileNotFoundError:
            PathConfigs = File["Prefixs"]

    while "$" in Input:
        try:
            Perfix, Matched, Suffix = PathRegex.match(Input).groups()
        except (AttributeError, ValueError):
            raise SearchError(Input)
        else:
            match Matched:
                case "PREFIX":
                    Matched = getcwd()
                case Matched if Matched in PathConfigs:
                    Matched = PathConfigs[Matched]
                case _:
                    raise PrefixsMissingKey(Matched)
            Input = f"{Perfix}{Matched}{Suffix}"

    if IsPath:
        Input = abspath(Input)

    return Input


def pathAdder(*Paths: str | Iterable | float | int) -> str:
    """拼接路径片段并格式化"""
    PathList = list()
    for i in Paths:
        if isinstance(i, str):
            PathList.append(i)
        elif isinstance(i, Iterable):
            PathList.extend(i)
        elif isinstance(i, int | float):
            PathList.append(str(i))
        else:
            raise TypeError(type(Paths))
    return path("/".join(PathList), IsPath=True)


def setPerfix(NewPerfix: str) -> None:
    """设置当前工作路径"""
    chdir(abspath(NewPerfix))


def safetyPath(Input: str) -> str:
    """获得更安全的路径"""
    if " " in Input:
        Input = f'"{Input}"'
    return Input
