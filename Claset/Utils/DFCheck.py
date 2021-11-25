# -*- coding: utf-8 -*-
"""
检测文件夹/文件是否存在和体积是否正常\n
在输入 Type 不存在时触发 ValueError\n
检查选项
* f：检测文件是否存在
* d：检测文件夹是否存在
* m：在选项d存在时创建文件夹, 在选项f存在时建立对应的文件夹
* s：在选项f存在时对比输入的 Size, 在文件不存在时触发 FileNotFoundError, 在 Size 为 None 时触发 ValueError
"""

from os import makedirs
from os.path import exists, getsize, dirname

from .Path import path as Pathmd


def dfCheck(Path: str, Type: str, Size: int | None = None) -> bool:
    """
    检测文件夹/文件是否存在和体积是否正常\n
    在输入 Type 不存在时触发 ValueError\n
    检查选项
    * f：检测文件是否存在
    * d：检测文件夹是否存在
    * m：在选项d存在时创建文件夹, 在选项f存在时建立对应的文件夹
    * s：在选项f存在时对比输入的 Size, 在文件不存在时触发 FileNotFoundError, 在 Size 为 None 时触发 ValueError
    """
    if "$" in Path: Path = Pathmd(Path, IsPath=True)

    if "d" in Type:
        if "m" in Type:
            try: makedirs(Path)
            except FileExistsError:
                return True
            return False
        return(exists(Path))
    elif "f" in Type:
        if "s" in Type:
            if dfCheck(Path=Path, Type="f") == False:
                raise FileNotFoundError(Path)
            FileSize = getsize(Path)
            if Size != FileSize:
                if FileSize == None: raise ValueError
                return(False)
            else: return(True)
        elif "m" in Type:
            try: makedirs(dirname(Path))
            except FileExistsError:
                return True
            return False
        return(exists(Path))
    else:
        raise ValueError(Type)

