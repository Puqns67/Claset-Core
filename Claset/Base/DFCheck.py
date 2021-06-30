#VERSION=5
#
#Claset/Base/DFCheck.py
#检测文件夹/文件是否存在和体积是否正常
#

#几种选项
#f：检测文件是否存在
#d：检测文件夹是否存在
#m：在d存在的时候创建文件夹,在检查文件不存在且文件夹没满足时创建文件夹
#s：在d不存在的时候检测文件大小


from os import makedirs
from os.path import exists, getsize
from re import search

from Claset.Base.Path import path as pathmd


def dfcheck(checktype, path, size=None) -> bool:
    if "$" in path:
        path = pathmd(path)

    if "s" in checktype:
        if "f" in checktype:
            tsize = getsize(path)
            if size != tsize:
                return(False)
            return(True)

    if "d" in checktype:
        if "m" in checktype:
            try:
                makedirs(path)
            except FileExistsError:
                pass
        return(exists(path))

    if "f" in checktype:
        if exists(path) == False:
            if "m" in checktype:
                try:
                    makedirs(path.replace(search(r"([a-zA-Z0-9_.-]*)$", path).group(1), ""))
                except FileExistsError:
                    pass
            return(False)
        return(True)

