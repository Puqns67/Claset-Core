#VERSION=7
#
#Claset/Base/Savefile.py
#保存文件
#

from json import dumps

from .Path import path as Path


def saveFile(path: str, filecontent: str | bytes, filetype: str = "json", filename: str = None) -> None:
    if filename != None: path += filename
    if "$" in path: path = Path(path)

    match filetype:
        case "json":
            with open(path, mode="w+") as thefile:
                thefile.write(dumps(filecontent, indent=4, ensure_ascii=False))
        case "bytes":
            with open(path, mode="wb+") as thefile:
                thefile.write(filecontent)
        case "log":
            with open(path, mode="a+") as thefile:
                thefile.write(filecontent)
        case "txt":
            with open(path, mode="w+") as thefile:
                thefile.write(filecontent)

