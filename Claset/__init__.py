# -*- coding: utf-8 -*-
"""
# Claset
基于 Python 的 Minecraft 启动管理器, 未完成
"""

import logging

from . import Base, Game, Tools

__all__ = ["Base", "Game", "Tools", "Logger"]

# 全局日志
Logger = logging.getLogger(__name__)
Logger.setLevel(logging.DEBUG)

Logs = Base.Logs.Logs(Logger)
Logs.SettingHandler()
Logs.processOldLog()

