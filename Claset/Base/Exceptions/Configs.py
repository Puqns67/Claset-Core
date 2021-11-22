# -*- coding: utf-8 -*-

class ConfigsErrors(Exception):
    """配置文件错误主类"""

class ConfigsUnregistered(ConfigsErrors):
    """配置文件未注册"""

class ConfigsExist(ConfigsErrors, FileExistsError):
    """配置文件已存在"""

class UnknownDifferenceType(ConfigsErrors):
    """不存在的差异类型"""