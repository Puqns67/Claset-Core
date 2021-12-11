# -*- coding: utf-8 -*-

class LauncherError(Exception):
    """启动器错误主类"""

class VersionNotFound(LauncherError):
    """版本不存在"""

