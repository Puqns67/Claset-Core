# -*- coding: utf-8 -*-

class ConfigErrors(Exception):
    """配置文件错误主类"""

class ConfigUnregistered(ConfigErrors):
    """配置文件未注册"""

class ConfigExist(ConfigErrors, FileExistsError):
    """配置文件已存在"""

class UnknownDifferenceType(ConfigErrors):
    """不存在的差异类型"""

class ConfigTypeError(ConfigErrors):
    """配置文件类型错误"""

