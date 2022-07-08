# -*- coding: utf-8 -*-

from typing import Iterable, Any
from base64 import b64encode, b64decode
from re import compile

__all__ = (
    "getValueFromDict",
    "setValueToDict",
    "fixType",
    "encodeBase64",
    "decodeBase64",
    "formatDollar",
)
__fixType_fixs = {"true": True, "false": False, "null": None, "none": None}
ReMatchFormatDollar = compile(r"^(.*)\${([a-zA-Z]+\w*)}(.*)$")
ReMatchStrList = compile(r"^\s*\[([\w\s,]*)\]\s*$")


def getValueFromDict(Keys: Iterable[str] | str, Dict: dict) -> Any:
    """使用列表从字典获取数据"""
    if isinstance(Keys, list | tuple):
        if len(Keys) >= 2:
            return getValueFromDict(Keys=Keys[1:], Dict=Dict[Keys[0]])
        elif len(Keys) == 1:
            return Dict[Keys[0]]
        else:
            raise ValueError("Keys's count must be greater than 0")
    elif isinstance(Keys, str):
        return Dict[Keys]
    else:
        raise TypeError(type(Keys))


def setValueToDict(
    Keys: Iterable[str] | str, Value: Any, Dict: dict | None = None
) -> dict:
    """使用列表向字典填充数据"""
    if not isinstance(Dict, dict):
        Dict = dict()
    if isinstance(Keys, list | tuple):
        if len(Keys) >= 2:
            if Dict.get(Keys[0]) is None:
                Dict[Keys[0]] = dict()
            Dict[Keys[0]] = setValueToDict(
                Keys=Keys[1:], Value=Value, Dict=Dict[Keys[0]]
            )
            return Dict
        elif len(Keys) == 1:
            Dict[Keys[0]] = Value
            return Dict
        else:
            raise ValueError("Keys's count must be greater than 0")
    elif isinstance(Keys, str):
        Dict[Keys] = Value
        return Dict
    else:
        raise TypeError(type(Keys))


def fixType(Input: str) -> Any:
    """
    修复类型\n
    支持的输入输出类型:
    * 符合正则表达式 “^\s*\[([\w\s,]*)\]\s*$” 的字符串将被转化为 list 类型返回
    * 转化所有字符为小写后在此元组 ("true", "false", "null", "none",) 中的字符串将被转换为对应的类型返回
    * 最后一个字符为数字或小数点的字符串将会尝试转换为整型, 无法转为整型后尝试浮点数\n
    若都无法转换则返回原字符串
    """
    if ReMatchStrList.match(Input) is not None:
        Output = ReMatchStrList.match(Input).groups()[0].replace(" ", str()).split(",")
    elif Input.lower() in __fixType_fixs:
        Output = __fixType_fixs[Input.lower()]
    elif Input == str():
        return None
    elif Input[-1] in (
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        ".",
    ):
        try:
            Output = int(Input)
        except ValueError:
            # 若使用整型格式化失败则尝试浮点
            try:
                Output = float(Input)
            except ValueError:
                return Input
    else:
        return Input
    return Output


def encodeBase64(Input: str) -> str:
    """返回Base64编码后的字符串"""
    return str(b64encode(bytes(Input, encoding="utf8")), encoding="utf8")


def decodeBase64(Input: str) -> str:
    """返回Base64解码后的字符串"""
    return str(b64decode(bytes(Input, encoding="utf8")), encoding="utf8")


def formatDollar(Input: str, **Kwargs: str) -> None:
    """格式化 ${}"""
    while True:
        try:
            Perfix, Matched, Suffix = ReMatchFormatDollar.match(Input).groups()
        except (AttributeError, ValueError):
            break
        else:
            Matched = Kwargs[Matched]
            Input = f"{Perfix}{Matched}{Suffix}"
    return Input
