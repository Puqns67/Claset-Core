#VERSION=3
#
#Claset/Base/Loadfile.py
#读取文件
#

from json import load

from . import Path

def loadfile(path, filetype=None):
    if "$" in path:
        path = Path.path(path)

    if filetype == "json":
        with open(path) as openedfile:
            return(load(openedfile))

    elif filetype == "bytes":
        with open(path, "b") as openedfile:
            return(openedfile)

    elif filetype == None:
        with open(path) as openedfile:
            return(openedfile)

