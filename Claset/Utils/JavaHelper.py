# -*- coding: utf-8 -*-
"""获取 Java 的相关信息"""

from os import getenv
from subprocess import run
from re import search

from .Path import path as Pathmd, pathAdder
from .DFCheck import dfCheck


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
    Path = Path + " -version"
    Return = run(args=Path, capture_output=True)
    return(search(pattern=r"^(.+)\s+version\s+\"(.+)\"", string=Return.stderr.decode("utf-8")).groups())