# -*- coding: utf-8 -*-


class FileExceptions(Exception):
    """文件处理异常主类"""


class UnsupportType(FileExceptions, ValueError):
    """不支持的处理类型"""
