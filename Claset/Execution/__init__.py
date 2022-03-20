# -*- coding: utf-8 -*-

try:
    from .CommandLine import ClasetCommandLine, ClasetCommandLineMain
except ModuleNotFoundError:
    ClasetCommandLine = None
    ClasetCommandLineMain = None

try:
    from .Tests import TestMain
except ModuleNotFoundError:
    TestMain = None

__all__ = ("ClasetCommandLine", "ClasetCommandLineMain", "TestMain")

