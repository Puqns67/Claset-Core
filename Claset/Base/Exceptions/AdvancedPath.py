# -*- coding: utf-8 -*-

from .Path import Path


# 高级路径错误主类, 继承于 Path
class AdvancedPathErrors(Path): pass

# 搜寻错误
class SearchError(AdvancedPathErrors): pass

