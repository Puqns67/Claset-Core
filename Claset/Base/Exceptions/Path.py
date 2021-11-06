# -*- coding: utf-8 -*-

# Path 错误主类
class Path(Exception): pass

# Prefixs 中无需要的 Key
class PrefixsMissingKey(Path): pass

# 搜素错误
class SearchError(Path): pass

