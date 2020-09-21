
#From https://blog.csdn.net/albertsh/article/details/77886876

import os
import os.path

if os.path.isfile("./.gitignore") == True:
    ignore = []
    for line in open("./.gitignore"):
        if "\n" in line:
            line = line.replace("\n", "")
        if "/" in line:
            line = line.replace("/", "")
        if not line == "":
            ignore.append(line)
else:
    ignore = [".git", "__pycache__"]


def dfs_showdir(path, depth, previous=None):
    for item in os.listdir(path):
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
                dfs_showdir(newitem, depth + 1, newitem)

dfs_showdir('.', 0)

