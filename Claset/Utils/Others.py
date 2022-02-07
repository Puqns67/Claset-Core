# -*- coding: utf-8 -*-

from typing import Any
from base64 import b64encode, b64decode

fixType_fixs = {"true": True, "false": False, "null": None, "none": None}


def getValueFromDict(Keys: list, Dict: dict) -> Any:
    """使用列表从字典获取数据"""
    if len(Keys) > 1:
        return(getValueFromDict(Keys=Keys[1:], Dict=Dict[Keys[0]]))
    else:
        return(Dict[Keys[0]])


def setValueFromDict(Keys: list, Value: Any, Dict: dict | None = None, ) -> dict:
    """使用列表向字典填充数据"""
    if type(Dict) != type(dict()): Dict = dict()
    if len(Keys) > 1:
        if Dict.get(Keys[0]) == None: Dict[Keys[0]] = dict()
        Dict[Keys[0]] = setValueFromDict(Keys=Keys[1:], Value=Value, Dict=Dict[Keys[0]], )
        return(Dict)
    else:
        Dict[Keys[0]] = Value
        return(Dict)


def fixType(Input: str) -> Any:
    """修复类型"""
    if Input.lower() in fixType_fixs.keys():
        Output = fixType_fixs[Input.lower()]
    # elif Input == str(): return None
    elif Input[-1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        try: Output = int(Input)
        except ValueError:
            # 若使用整型格式化失败则尝试浮点
            try: Output = float(Input)
            except ValueError: pass
    else: Output = Input
    return(Output)


def encodeBase64(Input: str) -> str:
    """返回Base64编码后的字符串"""
    return(str(b64encode(bytes(Input, encoding="utf8")), encoding="utf8"))


def decodeBase64(Input: str) -> str:
    """返回Base64解码后的字符串"""
    return(str(b64decode(bytes(Input, encoding="utf8")), encoding="utf8"))

