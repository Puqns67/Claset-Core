#VERSION=7
#
#Claset/Base/DFCheck.py
#检测文件夹/文件是否存在和体积是否正常
#

# 几种选项
# f：检测文件是否存在
# d：检测文件夹是否存在
# m：在d存在的时候创建文件夹,在检查文件不存在且文件夹没满足时创建文件夹
# s：在d不存在的时候检测文件大小

from os import makedirs
from os.path import exists, getsize
from re import search

from .Path import path as Pathmd


def dfCheck(Path: str, Type: str, Size: int | None = None) -> bool:
    if "$" in Path: Path = Pathmd(Path)

    if ("s" in Type) and ("f" in Type):
        FileSize = getsize(Path)
        if Size != FileSize: return(False)
        else: return(True)
    elif "d" in Type:
        if "m" in Type:
            try: makedirs(Path)
            except FileExistsError: pass
        else: return(exists(Path))
    elif "f" in Type:
        if exists(Path) == False:
            if "m" in Type:
                try: makedirs(Path.replace(search(r"([a-zA-Z0-9_.-]*)$", Path).group(1), ""))
                except FileExistsError: pass
            else: return(False)
        else: return(True)

