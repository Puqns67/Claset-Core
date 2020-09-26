#Version=0
#Claset/Update/Listfile.py
#制成文件列表
#

import os, os.path
from Claset.Base.Path import path as pathmd

def listfile(path="$PREFIX", depth=0, previous=None):

    filelist = {}

    for item in os.listdir(pathmd(path)):
        seq = ""

        for dirr in ignore:
            if dirr in item:
                seq += "-"
            else:
                seq += "+"

        if "-" not in seq:
            newitem = path +'/'+ item

            if os.path.isfile(newitem):
                if not previous == None:
                    print(previous + "/" + item)
                
                else:
                    print("./" + item)

            if os.path.isdir(newitem):
                listfile(newitem, depth + 1, newitem)

    return()
