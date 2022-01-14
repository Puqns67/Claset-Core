# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

__author__ = "Puqns67"
__productname__ = "Claset"
__version__ = "0.1.0"
__all__ = ["Accounts", "Execution", "Utils", "Game", "getLogger"]

LaunchedGames = list()

from logging import getLogger, Logger, DEBUG

from . import Accounts, Execution, Utils, Game

GolbalLogger = getLogger(__name__)
GolbalLogger.setLevel(DEBUG)

ProcessLogger = Utils.Logs(GolbalLogger)
ProcessLogger.SettingHandler()
ProcessLogger.SettingLevel()
ProcessLogger.processOldLog()

def getLogger() -> Logger:
    return(GolbalLogger)


def waitALLGames() -> None:
    for I in LaunchedGames:
        I.waitGame()

