# -*- coding: utf-8 -*-
"""
# Claset-Core
基于 Python 的 Minecraft 启动管理器, 未完成
"""

__author__ = "Puqns67"
__productname__ = "Claset-Core"
__version__ = "0.1.0"
__build__ = 187
__fullversion__ = f"{__version__}_{str(__build__)}"
__all__ = (
    "Accounts",
    "Utils",
    "Instance",
    "LaunchedInstance",
    "waitALLGames",
    "stopALLGames",
    "killALLInstance",
)

LaunchedInstance = list()


def waitALLInstance() -> None:
    """等待所有实例结束"""
    for I in LaunchedInstance:
        I.waitInstance()


def stopALLInstance() -> None:
    """停止所有实例"""
    for I in LaunchedInstance:
        I.stopInstance()


def killALLInstance() -> None:
    """杀死所有实例"""
    for I in LaunchedInstance:
        I.killInstance()


from . import Accounts, Utils, Instance
