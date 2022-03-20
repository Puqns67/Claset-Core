# -*- coding: utf-8 -*-

from typing import Any
from base64 import b64encode, b64decode
from re import compile

__all__ = ("getValueFromDict", "setValueFromDict", "fixType", "encodeBase64", "decodeBase64", "formatDollar",)
__fixType_fixs = {"true": True, "false": False, "null": None, "none": None}
__ReMatchFormatDollar = compile(r"^(.*)\${(.*)}(.*)$")


def getValueFromDict(Keys: list[str] | str, Dict: dict) -> Any:
    """使用列表从字典获取数据"""
    if isinstance(Keys, list):
        if len(Keys) > 1:
            return(getValueFromDict(Keys=Keys[1:], Dict=Dict[Keys[0]]))
        else:
            return(Dict[Keys[0]])
    elif isinstance(Keys, str):
        return(Dict[Keys])


def setValueFromDict(Keys: list, Value: Any, Dict: dict | None = None, ) -> dict:
    """使用列表向字典填充数据"""
    if not isinstance(Dict, dict): Dict = dict()
    if len(Keys) > 1:
        if Dict.get(Keys[0]) is None: Dict[Keys[0]] = dict()
        Dict[Keys[0]] = setValueFromDict(Keys=Keys[1:], Value=Value, Dict=Dict[Keys[0]], )
        return(Dict)
    else:
        Dict[Keys[0]] = Value
        return(Dict)


def fixType(Input: str) -> Any:
    """修复类型"""
    Output = Input
    if Input.lower() in __fixType_fixs:
        Output = __fixType_fixs[Input.lower()]
    elif Input == str(): return None
    elif Input[-1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        try: Output = int(Input)
        except ValueError:
            # 若使用整型格式化失败则尝试浮点
            try: Output = float(Input)
            except ValueError: pass
    return(Output)


def encodeBase64(Input: str) -> str:
    """返回Base64编码后的字符串"""
    return(str(b64encode(bytes(Input, encoding="utf8")), encoding="utf8"))


def decodeBase64(Input: str) -> str:
    """返回Base64解码后的字符串"""
    return(str(b64decode(bytes(Input, encoding="utf8")), encoding="utf8"))


def formatDollar(Input: str, **Kwargs: str) -> None:
    """格式化 ${}"""
    try:
        Matched = list(__ReMatchFormatDollar.match(Input).groups())
    except AttributeError:
        return(Input)
    while Matched:
        Matched[1] = Kwargs[Matched[1]]
        try:
            Matched = list(__ReMatchFormatDollar.match(str().join(Matched)).groups())
        except AttributeError:
            break
    return(str().join(Matched))

