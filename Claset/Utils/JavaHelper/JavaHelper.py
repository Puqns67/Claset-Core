# -*- coding: utf-8 -*-
"""获取 Java 的相关信息"""

from logging import getLogger
from os import getenv
from subprocess import run
from re import compile
from platform import system

from ..Path import path as Pathmd, pathAdder
from ..File import dfCheck
from ..Others import fixType

from .Exceptions import MatchStringError
from ..Exceptions import Claset as Ex_Claset

Logger = getLogger(__name__)
reMatchJavaInfos = compile(r"\s*os\.arch=\"(.+)\"\s*java\.version=\"(.+)\"\s*java\.vendor=\"(.+)\"\s*")
__all__ = ["getJavaPath", "getJavaInfo", "versionFormater", "getJavaInfoList", "reMatchJavaInfos", "fixJavaPath"]


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
                OnePath = pathAdder(OnePath, "java.exe")
            case "Linux":
                OnePath = pathAdder(OnePath, "java")
            case _:
                Ex_Claset.UnsupportSystemHost(system())
        if dfCheck(Path=OnePath, Type="d"):
            if (not (OnePath in Output)):
                Output.append(OnePath)
    return(Output)


def getJavaInfo(Path: str | None) -> tuple[str]:
    """通过 Java 源文件获取 Java 版本"""
    Path = fixJavaPath(Path)
    JarPath = Pathmd("$EXEC/Utils/JavaHelper/GetJavaInfo.jar", IsPath=True)

    if dfCheck(Path=JarPath, Type="f") == False:
        Logger.error("Jar File: \"%s\" missing", JarPath)

    Return = run(args=[Path, "-jar", JarPath], capture_output=True)
    Logger.debug("Java from \"%s\" return: \"%s\"", Path, Return)
    DecodedReturn = Return.stdout.decode("utf-8")
    try:
        return(reMatchJavaInfos.match(DecodedReturn).groups())
    except AttributeError:
        raise MatchStringError(DecodedReturn)


def fixJavaPath(Path: str) -> str:
    """修正路径"""
    if Path == None: Path = str()
    match system():
        case "Windows":
            if Path[-4] == "java":
                Path = Path[:-4] + "java.exe"
        case "Linux":
            if Path[-8:] == "java.exe":
                Path = Path[:-8] + "java"
        case _:
            Ex_Claset.UnsupportSystemHost(system())
    return(Path)


def versionFormater(Version: str) -> list:
    Version = Version.replace(".",  " ").split()
    if Version[0] == "1":
        Version[0] = Version[1]
        Version[1] = "0"
    if Version[-1][:2] == "0_":
        Version[-1] = Version[-1][2:]
    for i in range(len(Version)):
        Version[i] = fixType(Version[i])
    return(Version)


def getJavaInfoList(PathList: list[str] | None = None) -> list[dict[str, str | tuple[int]]]:
    """
    通过版本列表获取字典形式的 Java 信息，如输入为空则通过 Claset.Utils.JavaHelper.getJavaPath() 获取\n
    如获取过程中出现 JavaHelper.MatchStringError 将不在输出中附上出错的信息
    """
    if PathList == None: PathList: list[str] = getJavaPath()
    Outputs = list()
    for Path in PathList:
        try: Infos = getJavaInfo(Path)
        except MatchStringError: continue
        Outputs.append({
            "Path": Path,
            "Arch": Infos[0],
            "Version": versionFormater(Infos[1]),
            "From": Infos[2]
        })
    return(Outputs)

