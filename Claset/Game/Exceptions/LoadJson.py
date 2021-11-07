# -*- coding: utf-8 -*-

# 解析游戏 Json 错误主类
class LoadGameJsonErrors(Exception): pass

# Features 中缺少对应的键
class FeaturesMissingKey(LoadGameJsonErrors): pass

# 不支持的系统类型
class UnsupportSystemHost(LoadGameJsonErrors): pass

# 用于在处理 Features 时 Contiune 的内部错误
class FeaturesContinue(LoadGameJsonErrors): pass

# 未找到指定的游戏版本
class TargetVersionNotFound(LoadGameJsonErrors): pass

# Classifiers 文件错误
class ClassifiersFileError(LoadGameJsonErrors): pass

