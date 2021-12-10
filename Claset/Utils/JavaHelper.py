# -*- coding: utf-8 -*-
"""获取 Java 的相关信息"""

from logging import getLogger
from os import getenv
from subprocess import run
from re import match
from platform import system

from .Path import path as Pathmd
from .File import dfCheck

from .Exceptions import JavaHelper as Ex_JavaHelper, Claset as Ex_Claset

Logger = getLogger(__name__)


def getJavaPath() -> list[str]:
    """获取 Java 路径列表"""
    Output = list()
    match system():
        case "Windows":
            Paths = getenv("PATH").split(";")
        case "Linux":
            Paths = getenv("PATH").split(":")
        case _:
            Ex_Claset.UnsupportSystemHost(system())
    for OnePath in Paths:
        match system():
            case "Windows":
                OnePath += "/java.exe"
            case "Linux":
                OnePath += "/java"
            case _:
                Ex_Claset.UnsupportSystemHost(system())
        OnePath = Pathmd(OnePath, IsPath=True)
        if dfCheck(Path=OnePath, Type="d"):
            if (not (OnePath in Output)):
                Output.append(OnePath)
    return(Output)


def getJavaInfoList(PathList: list[str] | None = None) -> dict[str, tuple[str]]:
    """
    通过版本列表获取字典形式的 Java 信息，如输入为空则通过 Claset.Utils.JavaHelper.getJavaPath() 获取\n
    如获取过程中出现 JavaHelper.MatchStringError 将不在输出中附上出错的信息
    """
    if PathList == None: PathList: list[str] = getJavaPath()
    Output = dict()
    for Path in PathList:
        try:
            Output[Path] = getJavaInfo(Path)
        except Ex_JavaHelper.MatchStringError:
            pass
    return(Output)


def getJavaInfo(Path: str) -> tuple[str]:
    """通过 Java 源文件获取 Java 版本"""
    JarPath = Pathmd("$EXEC/Utils/JavaHelper/GetJavaInfo.jar", IsPath=True)
    Return = run(args=[Path, "-jar", JarPath], capture_output=True)
    Logger.debug("Java from \"%s\" return: \"%s\"", Path, Return)
    DecodedReturn = Return.stdout.decode("utf-8")
    try:
        return(match(r"\s*os\.arch=\"(.+)\"\s*java\.version=\"(.+)\"\s*java\.vendor=\"(.+)\"\s*", DecodedReturn).groups())
    except AttributeError:
        raise Ex_JavaHelper.MatchStringError(DecodedReturn)


