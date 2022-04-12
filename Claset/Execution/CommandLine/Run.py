# -*- coding: utf-8 -*-

from sys import version
from platform import uname
import Claset

def main():
    Claset.setLoggerHandler(Stream="WARNING")
    Claset.ProcessLogs()
    Claset.GolbalLogger.info("Claset - Version: %s, Powered By Python %s", Claset.__fullversion__, version)
    Claset.GolbalLogger.info("Running in \"%s\"", " ".join(uname()))
    Main = Claset.Execution.ClasetCommandLine()
    Main.i18n()
    Main.addArgumentToParsers()
    Main.cmdloop()

if __name__ == "__main__":
    main()

