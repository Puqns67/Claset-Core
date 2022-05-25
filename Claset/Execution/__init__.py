# -*- coding: utf-8 -*-

try:
    from .CommandLine import ClasetCommandLine, ClasetCommandLineMain
except ModuleNotFoundError:
    ClasetCommandLine = None
    ClasetCommandLineMain = None

__all__ = (
    "ClasetCommandLine",
    "ClasetCommandLineMain",
)
