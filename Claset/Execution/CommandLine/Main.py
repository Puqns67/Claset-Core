# -*- coding: utf-8 -*-

from argparse import Namespace

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

import Claset


class Main(Cmd):
    intro = "Claset\nBuiltin Command Line Client\nVersion: " + Claset.__version__
    prompt = "> "

    delattr(Cmd, "do_shell")
    delattr(Cmd, "do_edit")
    delattr(Cmd, "do_quit")

    ArgumentParser_InstallGame = Cmd2ArgumentParser()
    ArgumentParser_InstallGame.add_argument("-v", "--version", help="游戏版本, 不指定时使用最新的正式版")
    ArgumentParser_InstallGame.add_argument('GameName', help="游戏实例名")
    @with_argparser(ArgumentParser_InstallGame)
    def do_InstallGame(self, init: Namespace):
        """安装游戏"""
        GameInstaller = Claset.Game.Install.GameInstaller(VersionName=init.GameName, MinecraftVersion=init.version)
        GameInstaller.InstallVanilla()


    def do_exit(self, _: Namespace):
        """退出程序"""
        Claset.stopALLDownloader()
        Claset.waitALLGames()
        raise SystemExit
    do_quit = do_exit

