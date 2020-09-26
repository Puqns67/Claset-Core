#Version=2
#Claset/Update/Ignorefile.py
#忽略文件
#

from os.path import isfile
from Claset.Base.Path import path

def ignorefile():
    ignore = []
    if isfile(path("$PREFIX/.gitignore")) == True:

        for line in open(path("$PREFIX/.gitignore")):
            if "\n" in line:
                line = line.replace("\n", "")
            if "/" in line:
                line = line.replace("/", "")
            if not line == "":
                ignore.append(line)
        
    else:
        ignore = [".git", "__pycache__"]

    return(ignore)

