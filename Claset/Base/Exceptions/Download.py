# -*- coding: utf-8 -*-

# 下载错误主类
class DownloadExceptions(Exception): pass

# 文件已存在
class FileExist(DownloadExceptions): pass

# 下载超时
class Timeout(DownloadExceptions): pass

# 链接超时
class ConnectTimeout(Timeout): pass

# 读取超时
class ReadTimeout(Timeout): pass

# 哈希验证异常
class HashError(DownloadExceptions): pass

# 大小异常
class SizeError(DownloadExceptions): pass

# 格式错误
class SchemaError(DownloadExceptions): pass

# 缺少链接
class MissingURL(DownloadExceptions): pass

# 已停止
class Stopping(DownloadExceptions): pass

# 解完整 OutputPaths 时出现的错误
class UnpackOutputPathsError(DownloadExceptions): pass

