# -*- coding: utf-8 -*-


class InstanceError(Exception):
    """实例错误主类"""


class UndefinedInstanceStatus(InstanceError):
    """未定义的实例状态"""


class InstanceStatusError(InstanceError):
    """实例状态错误"""


class LauncherError(InstanceError):
    """启动器错误主类"""


class VersionNotFound(LauncherError):
    """版本不存在"""


class UnsupportVersion(LauncherError):
    """不支持的版本文件"""


class LauncherVersionError(LauncherError):
    """此版本所要求的启动器版本不被本启动器所满足"""
