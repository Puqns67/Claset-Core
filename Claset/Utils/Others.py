# -*- coding: utf-8 -*-

from typing import Any

fixType_fixs = {"true": True, "false": False, "null": None, "none": None}


def getValueFromDict(Keys: list, Dict: dict) -> Any:
    """使用列表从字典中获取数据"""
    if len(Keys) == 1:
        return(Dict[Keys[0]])
    else:
        return(getValueFromDict(Keys=Keys[1:], Dict=Dict[Keys[0]]))


def fixType(Input: str) -> Any:
    """修复类型"""
    if Input.lower() in fixType_fixs.keys():
        Output = fixType_fixs[Input.lower()]
    elif Input[-1] in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        try: Output = int(Input)
        except ValueError:
            # 若使用整型格式化失败则尝试浮点
            try: Output = float(Input)
            except ValueError: pass
    else: Output = Input

    return(Output)

