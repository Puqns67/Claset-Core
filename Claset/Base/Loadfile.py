#VERSION=1
#
#Claset/Base/Loadfile.py
#通过url下载数据
#

import json

from Claset.Base.Path import path

def loadfile(path, filetype=None):
    if "$" in jsonpath:
        path = path(path)

    if filetype == "json":
        with open(path) as openedfile:
            return(json.load(openedfile))

    elif filetype == "bytes":
        with open(path, "b") as openedfile:
            return(openedfile)

    elif filetype == None:
        with open(path) as openedfile:
            return(openedfile)
            