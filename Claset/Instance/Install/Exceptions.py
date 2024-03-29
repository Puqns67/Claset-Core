# -*- coding: utf-8 -*-


class InstallError(Exception):
    """安装错误主类"""


class UnknownVersion(InstallError):
    """未知的版本/找不到对应的版本"""


class DownloadError(InstallError):
    """下载出现错误"""


class UndefinedMirror(InstallError):
    """未定义的镜像源"""


class VanillaInstalled(InstallError):
    """原版已安装"""
