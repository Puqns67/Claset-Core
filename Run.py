# -*- coding: utf-8 -*-

import Claset

if __name__ == "__main__":
    Claset.setLoggerHandler(Stream="WARNING")
    Claset.ProcessLogs()
    Main = Claset.Execution.CommandLineMain()
    Main.cmdloop()

