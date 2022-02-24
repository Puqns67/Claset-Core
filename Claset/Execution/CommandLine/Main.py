# -*- coding: utf-8 -*-

from argparse import Namespace

from rich.console import Console
from rich.table import Table
from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser

import Claset


# Argument parsers
AP_InstallGame = Cmd2ArgumentParser()
AP_InstallGame.add_argument("-V", "--Version", help="游戏版本, 不指定时使用最新的正式版")
AP_InstallGame.add_argument("GameName", help="游戏实例名")

AP_LaunchGame = Cmd2ArgumentParser()
AP_LaunchGame.add_argument("-S", "--ShowGameLogs", action="store_true", help="输出运行日志至终端")
AP_LaunchGame.add_argument("-Un", "--UserName", default=None, help="指定账户的类型为名称, 如有重复则按账户顺序取第一个")
AP_LaunchGame.add_argument("-Uu", "--UserUUID", default=None, help="指定账户的类型为 UUID")
AP_LaunchGame.add_argument("GameName", help="游戏实例名")

AP_CreateAccount = Cmd2ArgumentParser()
AP_CreateAccount.add_argument("-N", "--AccountName", help="账户名称, 此选项仅可使用在账户类型为离线时使用")
AP_CreateAccount.add_argument("-T", "--Type", default="MICROSOFT" , help="账户类型, 现支持 \"OFFLINE\" 和 \"MICROSOFT\" 类型, 默认为 \"MICROSOFT\"")

AP_RemoveAccount = Cmd2ArgumentParser()
AP_RemoveAccount.add_argument("-N", "--Name", help="指定账户的游戏内名称, 使用此参数时将有可能删除多个账户")
AP_RemoveAccount.add_argument("-T", "--Type", help="指定账户类型, 使用此参数时将有可能删除多个账户")
AP_RemoveAccount.add_argument("-i", "--ID", help="指定账户 ID, 此 ID 为在配置文件中的序列号")
AP_RemoveAccount.add_argument("-I", "--UUID", help="指定账户 UUID")
AP_RemoveAccount.add_argument("Target", help="对应的目标")


class Main(Cmd):
    """命令行模式下的主函数"""

    intro = "Claset - Builtin Command Line Client\nVersion: " + Claset.__fullversion__
    prompt = "> "
    RichConsole = Console()
    AccountManager = Claset.Accounts.AccountManager()

    # 移除部分内置函数
    delattr(Cmd, "do_shell")
    delattr(Cmd, "do_edit")
    delattr(Cmd, "do_quit")


    # 命令实现
    @with_argparser(AP_InstallGame)
    def do_InstallGame(self, init: Namespace):
        """安装游戏实例"""
        GameInstaller = Claset.Game.GameInstaller(VersionName=init.GameName, MinecraftVersion=init.Version)
        GameInstaller.InstallVanilla()


    @with_argparser(AP_LaunchGame)
    def do_LaunchGame(self, init: Namespace):
        """启动游戏实例"""
        UserID = None
        if init.UserUUID:
            UserID = self.AccountManager.getAccountOtherInfo(Input=init.UserUUID, InputType="UUID", ReturnType="ID")
        elif init.UserName:
            UserID = self.AccountManager.getAccountOtherInfo(Input=init.UserName, InputType="Name", ReturnType="ID")
        TheAccount = self.AccountManager.getAccountObject(UserID)
        GameLauncher = Claset.Game.GameLauncher(VersionName=init.GameName, Account=TheAccount)
        GameLauncher.launchGame(PrintToTerminal=init.ShowGameLogs)


    def do_ListGame(self, _: Namespace):
        """列出所有游戏实例"""


    @with_argparser(AP_CreateAccount)
    def do_CreateAccount(self, init: Namespace):
        """创建新账户"""
        match init.Type:
            case "MICROSOFT":
                self.AccountManager.create(Type=init.Type)
            case "OFFLINE":
                if init.AccountName == None:
                    raise ValueError("设置账户类型为离线时用户名不应为空")
                else:
                    self.AccountManager.create(Type=init.Type, Name=init.AccountName)
            case _:
                ValueError(init.Type)
        self.AccountManager.save()


    def do_ListAccount(self, _: Namespace):
        """列出所有账户"""
        AccountList = self.AccountManager.getAccountList()
        if len(AccountList) == 0:
            print("账户列表为空")
            return

        # 构建列表
        AccountTable = Table("ID", "账户名", "UUID", "账户类型", "账户状态")
        for Account in AccountList:
            AccountTable.add_row(str(Account["ID"]), Account["Name"], Account["UUID"], Account["Type"], Account["Status"])

        self.RichConsole.print(AccountTable)


    @with_argparser(AP_RemoveAccount)
    def do_RemoveAccount(self, init: Namespace):
        """删除指定的账户"""


    def do_Exit(self, _: Namespace):
        """退出程序"""
        Claset.stopALLDownloader()
        Claset.waitALLGames()
        raise SystemExit
    do_exit = do_Exit
    do_quit = do_Exit

