# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

import logging

from . import Game, Tools, Utils

# 初始化全局日志
_Logger = logging.getLogger(__name__)
_Logger.setLevel(logging.DEBUG)

Logs = Utils.Logs.Logs(_Logger)
Logs.SettingHandler()
Logs.processOldLog()

# 初始化 Downloader
_Downloader = Utils.Download.DownloadManager()

def getLogger():
    return(_Logger)

def getDownloader():
    return(_Downloader)

__all__ = ["Utils", "Game", "Tools", "getLogger", "getDownloader"]

