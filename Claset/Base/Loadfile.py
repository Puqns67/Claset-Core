#VERSION=2
#
#Claset/Base/Loadfile.py
#读取文件
#

from json import load

from Claset.Base.Path import path as pathmd

def loadfile(path, filetype=None):
    if "$" in path:
        path = pathmd(path)

    if filetype == "json":
        with open(path) as openedfile:
            return(load(openedfile))

    elif filetype == "bytes":
        with open(path, "b") as openedfile:
            return(openedfile)

    elif filetype == None:
        with open(path) as openedfile:
            return(openedfile)
            