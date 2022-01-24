# -*- coding: utf-8 -*-

import Claset

if __name__ == "__main__":
    Claset.setLoggerHandler(Stream=False)
    Claset.ProcessLogs()
    Main = Claset.Execution.CommandLineMain()
    Main.cmdloop()

