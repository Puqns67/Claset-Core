# -*- coding: utf-8 -*-

class LauncherError(Exception):
    """启动器错误主类"""

class VersionNotFound(LauncherError):
    """版本不存在"""

class UnsupportVersion(LauncherError):
    """不支持的版本文件"""

class LauncherVersionError(LauncherError):
    """此版本所要求的启动器版本不被本启动器所满足"""

class UndefinedGameStatus(LauncherError):
    """未定义的游戏状态"""

class GameStatusError(LauncherError):
    """游戏状态错误"""

