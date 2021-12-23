# -*- coding: utf-8 -*-

class CheckGameErrors(Exception):
    """检查游戏错误"""

class Sha1VerificationError(CheckGameErrors):
    """验证文件出错"""

class NativesFileError(CheckGameErrors):
    """Natives 文件错误"""

