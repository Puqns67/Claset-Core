#VERSION=1
#
#From Claset/Base/Path.py & Claset/Base/AdvancedPath.py
#Claset/Base/Exceptions/Path.py
#

# Path 错误主类
class Path(Exception): pass

# Prefixs 中无需要的 Key
class PerfixsMissingKey(Path): pass

# 搜素错误
class SearchError(Path): pass

