# -*- coding: utf-8 -*-


class ConfigErrors(Exception):
    """配置文件错误主类"""


class ConfigUnregistered(ConfigErrors):
    """配置文件未注册"""


class ConfigExist(ConfigErrors, FileExistsError):
    """配置文件已存在"""


class UndefinedDifferenceType(ConfigErrors):
    """未定义的差异类型"""


class ConfigTypeError(ConfigErrors):
    """配置文件类型错误"""


class ConfigNonGlobalMissingFilePath(ConfigErrors):
    """配置文件强制私有时, 对应路径不能为空"""
