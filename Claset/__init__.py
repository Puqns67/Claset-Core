# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

import logging

from . import Base
from . import Game
from . import Tools

__all__ = ["Base", "Game", "Tools", "Logger"]

# 全局日志
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.INFO)

# Handlers
LoggerFormatter = logging.Formatter(fmt="[%(asctime)s][%(module)s][%(funcName)s][%(levelname)s]: %(message)s", datefmt="%Y/%m/%d|%H:%M:%S")
StreamHandler = logging.StreamHandler()
StreamHandler.setLevel(logging.DEBUG)
StreamHandler.setFormatter(LoggerFormatter)
# FileHandler = logging.FileHandler(filename="s.log")
# FileHandler.setLevel(logging.DEBUG)
# FileHandler.setFormatter(LoggerFormatter)

Logger.addHandler(StreamHandler)
# Logger.addHandler(FileHandler)
