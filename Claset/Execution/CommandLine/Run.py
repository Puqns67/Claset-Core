# -*- coding: utf-8 -*-

from sys import version, exit
from platform import uname
from time import time

from .I18n import getI18nProcessor
from .ArgumentParsers import addArgumentToParsers
from .ClasetCommandLine import ClasetCommandLine

import Claset


def main(Debug: bool = False):
    # 启动 Claset
    StartTime = time()

    # 启用日志功能
    if Debug:
        Claset.setLoggerHandler(Stream="DEBUG", File="DEBUG")
    else:
        Claset.setLoggerHandler(Stream="WARNING")
    Claset.ProcessLogs()
    Claset.GolbalLogger.info("Starting Claset...")
    Claset.GolbalLogger.info(
        "Claset - Version: %s, Powered By Python %s", Claset.__fullversion__, version
    )
    Claset.GolbalLogger.info('Running in "%s"', " ".join(uname()))

    i18nProcessor = getI18nProcessor()

    addArgumentToParsers(i18nProcessor=i18nProcessor)

    MainClass = ClasetCommandLine()
    MainClass.setI18nProcessor(Method=i18nProcessor)

    # 进入命令循环
    Return = MainClass.cmdloop()

    # 退出程序
    Claset.GolbalLogger.info(
        "Stopping Claset, running time as %s, returned %s", time() - StartTime, Return
    )
    exit(Return)


if __name__ == "__main__":
    main()
