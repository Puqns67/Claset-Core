# -*- coding: utf-8 -*-

from argparse import Namespace

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

import Claset


# ArgumentParsers
AP_InstallGame = Cmd2ArgumentParser()
AP_InstallGame.add_argument("-V", "--Version", help="游戏版本, 不指定时使用最新的正式版")
AP_InstallGame.add_argument("GameName", help="游戏实例名")

AP_LaunchGame = Cmd2ArgumentParser()
AP_LaunchGame.add_argument("-S", "--ShowGameLogs", action="store_true", help="输出运行日志至终端")
AP_LaunchGame.add_argument("GameName", help="游戏实例名")

AP_CreateAccount = Cmd2ArgumentParser()
AP_CreateAccount.add_argument("-N", "--AccountName", help="账户名称, 此选项仅可使用在账户类型为离线时使用")
AP_CreateAccount.add_argument("Type", default="MICROSOFT" , help="账户类型, 现支持 \"OFFLINE\" 和 \"MICROSOFT\" 类型, 默认为 \"MICROSOFT\"")

AP_RemoveAccount = Cmd2ArgumentParser()
AP_RemoveAccount.add_argument("-N", "--Name", help="指定账户的名称")
AP_RemoveAccount.add_argument("-T", "--Type", help="指定账户类型")
AP_RemoveAccount.add_argument("-i", "--ID", help="指定账户 ID")
AP_RemoveAccount.add_argument("-I", "--UUID", help="指定账户 UUID")


class Main(Cmd):
    intro = "Claset - Builtin Command Line Client\nVersion: " + Claset.__fullversion__
    prompt = "> "

    # 移除部分内置函数
    delattr(Cmd, "do_shell")
    delattr(Cmd, "do_edit")
    delattr(Cmd, "do_quit")


    @with_argparser(AP_InstallGame)
    def do_InstallGame(self, init: Namespace):
        """安装游戏"""
        GameInstaller = Claset.Game.GameInstaller(VersionName=init.GameName, MinecraftVersion=init.Version)
        GameInstaller.InstallVanilla()


    @with_argparser(AP_LaunchGame)
    def do_LaunchGame(self, init: Namespace):
        """启动游戏"""
        GameLauncher = Claset.Game.GameLauncher(init.GameName)
        GameLauncher.launchGame(PrintToTerminal=init.ShowGameLogs)


    @with_argparser(AP_CreateAccount)
    def do_CreateAccount(self, init: Namespace):
        """创建新账户"""
        AccountManager = Claset.Accounts.AccountManager()
        AccountManager.create(Type=init.Type, Name=init.Name)


    def do_ListAccount(self, _: Namespace):
        """列出所有账户"""


    @with_argparser(AP_RemoveAccount)
    def do_RemoveAccount(self, init: Namespace):
        """删除指定的账户"""


    def do_Exit(self, _: Namespace):
        """退出程序"""
        Claset.stopALLDownloader()
        Claset.waitALLGames()
        raise SystemExit

