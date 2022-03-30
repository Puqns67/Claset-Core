# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

__author__ = "Puqns67"
__productname__ = "Claset"
__version__ = "0.1.0"
__build__ = 174
__fullversion__ = __version__ + "_" + str(__build__)
__all__ = (
    "Accounts", "Execution", "Utils", "Game",
    "LaunchedGames", "Downloaders",
    "waitALLGames", "stopALLGames", "getDownloader", "stopALLDownloader",
    "setLoggerHandler", "ProcessOldLog", "getLogger", 
)

LaunchedGames = list()
Downloaders = list()

def waitALLGames() -> None:
    for I in LaunchedGames:
        I.waitGame()


def stopALLGames() -> None:
    for I in LaunchedGames:
        I.stopGame()


def getDownloader(ID: int = 0):
    try:
        Downloader = Downloaders[ID]
    except IndexError:
        if ID != 0:
            Downloader = Downloaders[0]
        else:
            Downloader = Utils.DownloadManager()
            Downloaders.append(Downloader)
    return(Downloader)


def stopALLDownloader() -> None:
    for I in Downloaders:
        I.stop()


from logging import getLogger, Logger, DEBUG

from . import Accounts, Execution, Utils, Game


GolbalLogger = getLogger(__name__)
GolbalLogger.setLevel(DEBUG)

LoggerProcesser = Utils.Logs(GolbalLogger)
LoggerProcesser.SettingLevel()


def setLoggerHandler(**Types: str | None):
    """设置日志句柄"""
    LoggerProcesser.SettingHandler(**Types)


def ProcessLogs(Type: str | None = None, ThreadMode: bool = True) -> None:
    """处理旧日志"""
    if ThreadMode:
        LoggerProcesser.ThreadProcessLogs(Type=Type)
    else:
        LoggerProcesser.ProcessLogs(Type=Type)


def getLogger() -> Logger:
    """获得原全局日志"""
    return(GolbalLogger)

