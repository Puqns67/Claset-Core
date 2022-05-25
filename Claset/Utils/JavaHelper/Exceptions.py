# -*- coding: utf-8 -*-


class JavaHelperError(Exception):
    """JavaHelper 错误主类"""


class MatchStringError(JavaHelperError, ValueError):
    """匹配字符串错误"""


class JavaNotFound(JavaHelperError):
    """未找到任何 Java"""
