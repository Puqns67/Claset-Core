#VERSION=5
#
#Claset/Base/Savefile.py
#保存文件
#

from json import dumps

from .Path import path as Path
from .DFCheck import dfCheck


def saveFile(path: str, filecontent, filetype: str = "json", filename: str = None) -> None:
    if filename != None:
        path += filename

    if "$" in path:
        path = Path(path)

    if filetype == "json":
        with open(path, mode="w+") as thefile:
            thefile.write(dumps(filecontent, indent=4, ensure_ascii=False))

    elif filetype == "bytes":
        with open(path, mode="wb+") as thefile:
            thefile.write(filecontent)

    elif filetype == "log":
        with open(path, mode="a+") as thefile:
            thefile.write(filecontent)

    elif filetype == "txt":
        with open(path, mode="w+") as thefile:
            thefile.write(filecontent)

