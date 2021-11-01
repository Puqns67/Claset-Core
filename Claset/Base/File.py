# -*- coding: utf-8 -*-
"""用于读取/写入文件"""

from json import load, dumps
from os.path import abspath

from .Path import path as Pathmd


def loadFile(Path: str, Type: str = "text") -> str:
    """
    加载文件
    * Path: 文件路径
    * Type： 类型(json, bytes, text)
    """

    if "$" in Path: Path = Pathmd(Path)

    match Type:
        case "json":
            with open(Path) as openedfile:
                return(load(openedfile))
        case "bytes":
            with open(Path, "rb") as openedfile:
                return(openedfile.read())
        case "text":
            with open(Path) as openedfile:
                return(openedfile)
        case _:
            raise TypeError("loadFile: Unknown Type")


def saveFile(Path: str, FileContent: str | bytes, Type: str = "text") -> None:
    """
    保存文件
    * Path: 文件路径
    * FileContent: 文件内容
    * Type： 类型(json, bytes, log, text)
    * FileName: 文件名
    """

    if "$" in Path: Path = Pathmd(Path)

    Path = abspath(Path)
    match Type:
        case "json":
            with open(Path, mode="w+") as thefile:
                thefile.write(dumps(FileContent, indent=4, ensure_ascii=False))
        case "bytes":
            with open(Path, mode="wb+") as thefile:
                thefile.write(FileContent)
        case "log":
            with open(Path, mode="a+") as thefile:
                thefile.write(FileContent)
        case "text":
            with open(Path, mode="w+") as thefile:
                thefile.write(FileContent)
        case _:
            raise TypeError("saveFile(): Unknown Type")

