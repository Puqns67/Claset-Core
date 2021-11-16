# -*- coding: utf-8 -*-

class InstallError(Exception):
    """安装错误主类"""


class UnknownVersion(InstallError):
    """未知的版本/找不到对应的版本"""