# -*- coding: utf-8 -*-


class Path(Exception):
    """Path 错误主类"""


class PrefixsMissingKey(Path):
    """Prefixs 中无需要的 Key"""


class SearchError(Path):
    """搜素错误"""
