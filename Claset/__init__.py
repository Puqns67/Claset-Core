# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

import logging

from . import Base
from . import Game
from . import Tools

__all__ = ["Base", "Game", "Tools"]

# 全局日志
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

Logger.addHandler(ch)

def getLogger() -> Logger:
    return(Logger)