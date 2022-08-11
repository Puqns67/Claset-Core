# -*- coding: utf-8 -*-


class UnsupportSystemHost(SystemError):
    """不支持的系统类型"""


class WorkInProgressThings(SystemError):
    """未完成的部分"""


class Continue(SystemError):
    """用于快速跳出多层循环"""
