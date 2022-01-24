# -*- coding: utf-8 -*-

from argparse import Namespace

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

import Claset


class Main(Cmd):
    prompt = ">"

    delattr(Cmd, "do_shell")
    delattr(Cmd, "do_edit")
    delattr(Cmd, "do_quit")

    ArgumentParser_InstallGame = Cmd2ArgumentParser()
    ArgumentParser_InstallGame.add_argument("-n", "--name", help="实例名")
    ArgumentParser_InstallGame.add_argument("-v", "--version", help="对应的游戏版本")
    @with_argparser(ArgumentParser_InstallGame)
    def do_InstallGame(self, init: Namespace):
        if (init.name == None) or (init.version == None): 
            raise ValueError("Name and Version cant be None")
        GameInstaller = Claset.Game.Install.GameInstaller(VersionName=init.name, MinecraftVersion=init.version)
        GameInstaller.InstallVanilla()


    def do_exit(self, init: Namespace):
        Claset.stopALLDownloader()
        Claset.waitALLGames()
        raise SystemExit
    do_quit = do_exit

