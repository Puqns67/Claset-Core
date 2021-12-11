# -*- coding: utf-8 -*-
"""用于读取/写入/检查文件"""

from json import load, dumps
from logging import getLogger
from os import makedirs, remove
from os.path import exists, getsize, dirname, basename, isdir
from shutil import move

from .Path import path as Pathmd, pathAdder

__all__ = ["loadFile", "saveFile", "moveFile", "dfCheck"]
Logger = getLogger(__name__)


def loadFile(Path: str, Type: str = "text") -> str | dict:
    """
    加载文件
    * Path: 文件路径
    * Type: 类型(json, bytes, text)
    """

    if "$" in Path: Path = Pathmd(Path)

    match Type:
        case "json":
            with open(file=Path, mode="r", encoding="UTF-8") as openedfile:
                return(load(openedfile))
        case "bytes":
            with open(file=Path, mode="rb") as openedfile:
                return(openedfile.read())
        case "text":
            with open(file=Path, mode="r", encoding="UTF-8") as openedfile:
                return(openedfile.read())
        case _:
            raise TypeError("loadFile: Unknown Type")


def saveFile(Path: str, FileContent: str | bytes, Type: str = "text") -> None:
    """
    保存文件
    * Path: 文件路径
    * FileContent: 文件内容
    * Type: 类型(json, bytes, log, text)
    """

    Logger.debug("Path: \"%s\", Type: \"%s\", FileContent Type: %s", Path, Type, type(FileContent))

    if "$" in Path: Path = Pathmd(Path, IsPath=True)
    dfCheck(Path=Path, Type="fm")

    match Type:
        case "json":
            with open(Path, mode="w+", encoding="UTF-8") as thefile:
                thefile.write(dumps(FileContent, indent=4, ensure_ascii=False))
        case "bytes":
            with open(Path, mode="wb+") as thefile:
                thefile.write(FileContent)
        case "log":
            with open(Path, mode="a+", encoding="UTF-8") as thefile:
                thefile.write(FileContent)
        case "text":
            with open(Path, mode="w+", encoding="UTF-8") as thefile:
                thefile.write(FileContent)
        case _:
            raise TypeError("saveFile(): Unknown Type")


def dfCheck(Path: str, Type: str, Size: int | None = None) -> bool:
    """
    检测文件夹/文件是否存在和体积是否正常\n
    在输入 Type 不存在时触发 ValueError\n
    检查选项
    * f: 检测文件是否存在, 也可检测文件夹
    * d: 检测文件夹是否存在, 也可检测文件
    * dm: 创建文件夹
    * fm: 建立对应的文件夹
    * fs: 对比输入的 Size, 在文件不存在时触发 FileNotFoundError, Size 为空时触发 ValueError\n
    若选项有误则触发 ValueError
    """
    if "$" in Path: Path = Pathmd(Path, IsPath=True)

    if "d" in Type:
        if "m" in Type:
            try: makedirs(Path)
            except FileExistsError:
                return True
            return False
        return(exists(Path))
    elif "f" in Type:
        if "s" in Type:
            if dfCheck(Path=Path, Type="f") == False:
                raise FileNotFoundError(Path)
            FileSize = getsize(Path)
            if Size != FileSize:
                if FileSize == None: raise ValueError
                return(False)
            else: return(True)
        elif "m" in Type:
            try: makedirs(dirname(Path))
            except FileExistsError:
                return True
            return False
        return(exists(Path))
    else:
        raise ValueError(Type)


def moveFile(File: str, ToDir: str, OverWrite: bool = True):
    if dfCheck(Path=File, Type="f") == False:
        raise FileNotFoundError(File)
    
    dfCheck(Path=ToDir, Type="dm")

    if (dfCheck(Path=pathAdder(ToDir, basename(File)), Type="f") == True):
        if (OverWrite == False):
            raise FileExistsError
        else: remove(pathAdder(ToDir, basename(File)))

    move(src=File, dst=ToDir)

