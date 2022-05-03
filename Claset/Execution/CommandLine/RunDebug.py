# -*- coding: utf-8 -*-

from sys import path
from os import getcwd

path.append(getcwd())

from Claset.Execution.CommandLine.Run import main


if __name__ == "__main__":
    main(Debug=True)

