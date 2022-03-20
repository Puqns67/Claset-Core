# -*- coding: utf-8 -*-

import Claset

def main():
    Claset.setLoggerHandler(Stream="WARNING")
    Claset.ProcessLogs()
    Main = Claset.Execution.ClasetCommandLine()
    Main.i18n()
    Main.addArgumentToParsers()
    Main.cmdloop()

if __name__ == "__main__":
    main()

