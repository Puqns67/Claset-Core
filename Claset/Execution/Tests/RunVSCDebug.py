# -*- coding: utf-8 -*-

from sys import path
from os import getcwd

path.append(getcwd())

import Claset

if __name__ == "__main__":
    Claset.setLoggerHandler()
    Claset.ProcessLogs()
    Claset.Execution.TestMain()

