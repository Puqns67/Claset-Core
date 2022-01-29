# -*- coding: utf-8 -*-

try:
    from .CommandLine import CommandLineMain
except ModuleNotFoundError:
    CommandLine = None

try:
    from .Tests import TestMain
except ModuleNotFoundError:
    TestMain = None

__all__ = ["CommandLineMain", "TestMain"]

