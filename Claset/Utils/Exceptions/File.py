# -*- coding: utf-8 -*-


class FileExceptions(Exception):
    """文件处理异常主类"""


class UnknownType(FileExceptions, ValueError):
    """未知的处理类型"""
