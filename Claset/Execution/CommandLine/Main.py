# -*- coding: utf-8 -*-

from argparse import Namespace

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

import Claset


# ArgumentParsers
AP_InstallGame = Cmd2ArgumentParser()
AP_InstallGame.add_argument("-v", "--Version", help="游戏版本, 不指定时使用最新的正式版")
AP_InstallGame.add_argument("GameName", help="游戏实例名")

AP_LaunchGame = Cmd2ArgumentParser()
AP_LaunchGame.add_argument("-S", "--ShowGameLogs", action='store_true', help="输出运行日志至终端")
AP_LaunchGame.add_argument("GameNames", nargs="+", help="游戏实例名")


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
        for i in init.GameNames:
            GameLauncher = Claset.Game.GameLauncher(i)
            GameLauncher.launchGame(PrintToTerminal=init.ShowGameLogs)


    def do_exit(self, _: Namespace):
        """退出程序"""
        Claset.stopALLDownloader()
        Claset.waitALLGames()
        raise SystemExit
    do_quit = do_exit
    do_stop = do_exit

