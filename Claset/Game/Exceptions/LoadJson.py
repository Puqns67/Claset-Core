# -*- coding: utf-8 -*-

from Claset.Utils.Exceptions.Claset import UnsupportSystemHost as MainUnsupportSystemHost

class LoadGameJsonErrors(Exception):
    """解析游戏 Json 错误主类"""

class FeaturesMissingKey(LoadGameJsonErrors):
    """Features 中缺少对应的键"""

class UnsupportSystemHost(LoadGameJsonErrors, MainUnsupportSystemHost):
    """不支持的系统类型"""

class FeaturesContinue(LoadGameJsonErrors):
    """用于在处理 Features 时 Contiune 的内部错误"""

class TargetVersionNotFound(LoadGameJsonErrors):
    """未找到指定的游戏版本"""

