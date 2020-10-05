#Version=1
#
#Claset/Update/Listfile.py
#制成文件列表
#

import os, os.path

from Claset.Update.Ignorefile import ignorefile
from Claset.Base.Path import path as pathmd

def listfile(path="$PREFIX"):

    something = {"Dirs": [path], "Files": []}
    ignores = ignorefile()
    output = []

    while something["Dirs"]:

        newDirs = []
        newFiles = []
        dirr = pathmd(something["Dirs"].pop())

        for item in os.listdir(dirr):

            item = dirr + "/" + item
            seq = "+"

            for ignore in ignores:
                if ignore in item:
                    seq += "-"
                    
            if "-" in seq:
                continue

            if os.path.isdir(item):
                newDirs.append(item)
            elif os.path.isfile(item):
                newFiles.append(item)

        for item in newDirs:
            something["Dirs"].append(item)
        while newFiles:
            something["Files"].append(newFiles.pop())
    
    for i in something["Files"]:
        i = i.replace(os.getcwd(), "")
        output.append(i)

    return(output)

