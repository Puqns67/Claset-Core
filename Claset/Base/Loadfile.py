#VERSION=5
#
#Claset/Base/Loadfile.py
#读取文件
#

from json import load

from .Path import path as Path

def loadFile(path, filetype=None):
    if "$" in path: path = Path(path)

    match filetype:
        case "json":
            with open(path) as openedfile:
                return(load(openedfile))
        case "bytes":
            with open(path, "rb") as openedfile:
                return(openedfile.read())
        case _:
            with open(path) as openedfile:
                return(openedfile)

