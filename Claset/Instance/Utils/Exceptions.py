# -*- coding: utf-8 -*-

from Claset.Utils.Exceptions.Claset import (
    UnsupportSystemHost as MainUnsupportSystemHost,
)


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


class CheckGameErrors(Exception):
    """检查游戏错误"""


class Sha1VerificationError(CheckGameErrors):
    """验证文件出错"""


class NativesFileError(CheckGameErrors):
    """Natives 文件错误"""


class ProcessInstallProfileError(Exception):
    """处理模组加载器时出现的错误主类"""


class UnsupportedModLoaderType(ProcessInstallProfileError, ValueError):
    """不支持的模组加载器类型"""


class Sha1VerifyError(ProcessInstallProfileError):
    """处理后的 Sha1 不符合预期"""
