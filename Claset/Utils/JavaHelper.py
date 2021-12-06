# -*- coding: utf-8 -*-
"""获取 Java 的相关信息"""

from logging import getLogger
from os import getenv
from subprocess import run
from re import match

from .Path import path as Pathmd
from .DFCheck import dfCheck

Logger = getLogger(__name__)


def getJavaPath() -> list[str]:
    """获取 Java 路径列表"""
    Output = list()
    Paths = getenv("Path").split(";")
    for OnePath in Paths:
        OnePath += "\java.exe"
        if dfCheck(Path=OnePath, Type="d"):
            if (not (OnePath in Output)):
                Output.append(Pathmd(Input=OnePath, IsPath=True))
    return(Output)


def getJavaVersionInfo(Path) -> tuple:
    """通过 Java 源文件获取 Java 版本"""
    JarPath = Pathmd("$EXEC/Utils/JavaHelper/GetJavaVersion.jar", IsPath=True)
    Return = run(args=[Path, "-jar", JarPath], capture_output=True)
    Logger.debug("Java from \"%s\" return: \"%s\"", Path, Return)
    ReturnDecoded = Return.stdout.decode("utf-8")
    return(match(r"\s*os\.arch=\"(.+)\"\s*java\.version=\"(.+)\"\s*java\.vendor=\"(.+)\"\s*", ReturnDecoded).groups())

