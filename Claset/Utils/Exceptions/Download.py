# -*- coding: utf-8 -*-

class DownloadExceptions(Exception):
    """下载错误主类"""

class FileExist(DownloadExceptions):
    """文件已存在"""

class Timeout(DownloadExceptions):
    """下载超时"""

class ConnectTimeout(Timeout):
    """链接超时"""

class ReadTimeout(Timeout):
    """读取超时"""

class HashError(DownloadExceptions):
    """哈希验证异常"""

class SizeError(DownloadExceptions):
    """大小异常"""

class SchemaError(DownloadExceptions):
    """格式错误"""

class Stopping(DownloadExceptions):
    """停止 Flag 已经立起"""

class UnpackOutputPathsError(DownloadExceptions):
    """解完整 OutputPaths 时出现的错误"""

class DownloadStatusCodeError(DownloadExceptions):
    """Http 状态码为错误值 4xx, 5xx"""

