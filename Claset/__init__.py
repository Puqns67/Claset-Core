# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

__author__ = "Puqns67"
__productname__ = "Claset"
__version__ = "0.1.0"
__build__ = 128
__all__ = [
    "Accounts", "Execution", "Utils", "Game",
    "LaunchedGames", "Downloaders",
    "setLoggerHandler", "processOldLog", "getLogger", "waitALLGames", "stopALLGames"
]

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
from multiprocessing import ProcessError

from . import Accounts, Execution, Utils, Game

GolbalLogger = getLogger(__name__)
GolbalLogger.setLevel(DEBUG)

ProcessLogger = Utils.Logs(GolbalLogger)
ProcessLogger.SettingLevel()

def setLoggerHandler(**kwargs):
    ProcessLogger.SettingHandler(**kwargs)


def ProcessLogs(Type: str | None = None, ThreadMode: bool = True):
    if ThreadMode:
        ProcessLogger.ThreadProcessLogs(Type=Type)
    else:
        ProcessLogger.ProcessLogs(Type=Type)


def getLogger() -> Logger:
    return(GolbalLogger)

