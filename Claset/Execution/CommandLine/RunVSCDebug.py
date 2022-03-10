# -*- coding: utf-8 -*-

from sys import path
from os import getcwd

path.append(getcwd())

import Claset

if __name__ == "__main__":
    Claset.setLoggerHandler(Stream="WARNING")
    Claset.ProcessLogs()
    Main = Claset.Execution.CommandLineMain()
    Main.i18n()
    Main.addArgumentToParsers()
    Main.cmdloop()

