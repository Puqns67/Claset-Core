# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

from logging import getLogger, DEBUG

from .Utils import Logs

# 初始化全局日志
_Logger = getLogger(__name__)
_Logger.setLevel(DEBUG)

ProcessLogger = Logs.Logs(_Logger)
ProcessLogger.SettingHandler()
ProcessLogger.processOldLog()
ProcessLogger.SettingLevel()

def getLogger():
    return(_Logger)

from . import Utils

# 初始化 Downloader
_Downloader = Utils.Download.DownloadManager()

def getDownloader():
    return(_Downloader)

from . import Game, Tools

__all__ = ["Utils", "Game", "Tools", "getLogger", "getDownloader"]

