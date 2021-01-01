#VERSION=2
#
#Claset/Base/Savefile.py
#保存文件
#

from json import dumps
from Claset.Base.Path import path as pathmd

def savefile(path, filecontent, filetype="json", filename=None):

    if not filename == None:
        path += filename

    if "$" in path:
        path = pathmd(path)

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

