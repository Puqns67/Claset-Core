#VERSION=6
#
#Claset/Base/File.py
#读取/写入文件
#

from json import load, dumps
from platform import system
from os.path import abspath

from .Path import path as Pathmd


def loadFile(Path: str, Type: str = "text") -> str:
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


def saveFile(Path: str, FileContent: str | bytes, Type: str = "text", FileName: str | None = None) -> None:
    if FileName != None: Path += FileName
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

