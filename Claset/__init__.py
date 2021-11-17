# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

import logging

from . import Base

# 初始化 Downloader
Downloader = Base.Download.DownloadManager()

from . import Game
from . import Tools

__all__ = ["Base", "Game", "Tools", "Logger", "Downloader"]

# 初始化全局日志
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.DEBUG)

Logs = Base.Logs.Logs(Logger)
Logs.SettingHandler()
Logs.processOldLog()

