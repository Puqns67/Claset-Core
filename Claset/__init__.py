# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

from logging import getLogger, Logger, DEBUG

from . import Utils, Game, Tools

GolbalLogger = getLogger(__name__)
GolbalLogger.setLevel(DEBUG)

ProcessLogger = Utils.Logs.Logs(GolbalLogger)
ProcessLogger.SettingHandler()
ProcessLogger.SettingLevel()
ProcessLogger.processOldLog()

def getLogger() -> Logger:
    return(GolbalLogger)

__all__ = ["Utils", "Game", "Tools", "getLogger", "getDownloader"]

