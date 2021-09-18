#VERSION=1
#
#From Claset/Base/Download.py
#Claset/Base/Exceptions/Download.py
#

class DownloadExceptions(Exception): pass
class FileExist(DownloadExceptions): pass
class Timeout(DownloadExceptions): pass
class ConnectTimeout(Timeout): pass
class ReadTimeout(Timeout): pass
class HashError(DownloadExceptions): pass
class SizeError(DownloadExceptions): pass
class SchemaError(DownloadExceptions): pass
class MissingURL(DownloadExceptions): pass
class Stopping(DownloadExceptions): pass