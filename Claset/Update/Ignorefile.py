#Version=4
#
#Claset/Update/Ignorefile.py
#忽略文件
#

from os.path import isfile

from Claset.Base.Path import path

def ignorefile():
    ignore = [".git/", "__pycache__/", "Cache/", "Claset/Configs/", ".vscode/", ".history/", "LICENSE", ".gitignore", "README.md"]
    return(ignore)

