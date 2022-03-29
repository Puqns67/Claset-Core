# -*- coding: utf-8 -*-

from argparse import Namespace
from gettext import GNUTranslations, NullTranslations, find as FindMo
from os import environ
from sys import exec_prefix
from time import sleep

from cmd2 import Cmd, Cmd2ArgumentParser, with_argparser
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

import Claset

# Argument parsers
InstallGame = Cmd2ArgumentParser()
LaunchGame = Cmd2ArgumentParser()
CreateAccount = Cmd2ArgumentParser()
RemoveAccount = Cmd2ArgumentParser()
SetDefaultAccount = Cmd2ArgumentParser()
SetWorkDir = Cmd2ArgumentParser()
Exit = Cmd2ArgumentParser()


class ClasetCommandLine(Cmd):
    """命令行模式主类"""

    RichConsole = Console()
    AccountManager = Claset.Accounts.AccountManager()
    Configs = Claset.Utils.Configs("Settings")

    # 移除部分内置函数
    delattr(Cmd, "do_shell")
    delattr(Cmd, "do_edit")
    delattr(Cmd, "do_quit")


    def i18n(self) -> None:
        """多国语言支持"""
        match Claset.Utils.OriginalSystem:
            case "Windows":
                EnvironLanguage = None
                for i in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG',):
                    EnvironLanguage = environ.get(i)
                    if EnvironLanguage is not None:
                        EnvironLanguage = EnvironLanguage.split(";")
                        break
                TargetLanguage = self.Configs["Language"] or EnvironLanguage or "zh_CN.UTF-8"
            case _:
                TargetLanguage = self.Configs["Language"]

        if isinstance(TargetLanguage, str): TargetLanguage = [TargetLanguage]

        MoFilePath = FindMo(domain="Default", localedir=Claset.Utils.path(Input=f"{exec_prefix}/Translations", IsPath=True), languages=TargetLanguage)
        if MoFilePath is None:
            MoFilePath = FindMo(domain="Default", localedir=Claset.Utils.path(Input="$PREFIX/Translations", IsPath=True), languages=TargetLanguage)
        if MoFilePath is None:
            self.TranslateObj = NullTranslations()
        else:
            with open(file=MoFilePath, mode="rb") as MoFile:
                self.TranslateObj = GNUTranslations(fp=MoFile)

        self._ = self.TranslateObj.gettext
        self.intro = self._("Claset - 内建命令行模式\n当前版本: {}".format(Claset.__fullversion__))
        self.prompt = self._("> ")

        # 为 Cmd2 进行部分汉化
        self.doc_header = self._("Documented commands (use 'help -v' for verbose/'help <topic>' for details):")
        self.help_error = self._("No help on {}")
        self.default_error = self._("{} is not a recognized command, alias, or macro")


    def addArgumentToParsers(self) -> None:
        """为参数解析器附加参数"""
        InstallGame.add_argument("-V", "--Version", help=self._("游戏版本, 不指定时使用最新的正式版"))
        InstallGame.add_argument("GameName", help=self._("游戏实例名"))
        LaunchGame.add_argument("-S", "--ShowGameLogs", action="store_true", help=self._("输出运行日志至终端"))
        LaunchGame.add_argument("-Un", "--UserName", default=None, help=self._("指定账户的类型为名称, 如有重复则按账户顺序取第一个"))
        LaunchGame.add_argument("-Uu", "--UserUUID", default=None, help=self._("指定账户的类型为 UUID"))
        LaunchGame.add_argument("-Ui", "--UserID", default=None, type=int, help=self._("指定账户 ID, 此 ID 为在配置文件中的序列号"))
        LaunchGame.add_argument("GameName", help=self._("游戏实例名"))
        CreateAccount.add_argument("-N", "--AccountName", help=self._("账户名称, 此选项仅可使用在账户类型为离线时使用"))
        CreateAccount.add_argument("-T", "--Type", default="MICROSOFT", choices=("MICROSOFT", "OFFLINE",), help=self._("账户类型, 现支持 \"OFFLINE\" 和 \"MICROSOFT\" 类型, 默认为 \"MICROSOFT\""))
        RemoveAccount.add_argument("-N", "--Name", default=None, help=self._("指定账户的游戏内名称, 使用此参数时将有可能删除多个账户"))
        RemoveAccount.add_argument("-T", "--Type", default=None, help=self._("指定账户类型, 使用此参数时将有可能删除多个账户"))
        RemoveAccount.add_argument("-i", "--ID", default=None, type=int, help=self._("指定账户 ID, 此 ID 为在配置文件中的序列号"))
        RemoveAccount.add_argument("-I", "--UUID", default=None, help=self._("指定账户 UUID"))
        RemoveAccount.add_argument("-C", "--Confirm", action="store_false", help=self._("由于此命令有危害性, 您可以使用此参数查看使用此命令后的对账户列表的操作"))
        SetDefaultAccount.add_argument("-N", "--Name", default=None, help=self._("指定账户的游戏内名称, 使用此参数时将有可能删除多个账户"))
        SetDefaultAccount.add_argument("-T", "--Type", default=None, help=self._("指定账户类型, 使用此参数时将有可能删除多个账户"))
        SetDefaultAccount.add_argument("-i", "--ID", default=None, type=int, help=self._("指定账户 ID, 此 ID 为在配置文件中的序列号"))
        SetDefaultAccount.add_argument("-I", "--UUID", default=None, help=self._("指定账户 UUID"))
        SetWorkDir.add_argument("NewWorkDir", default=None, help=self._("新的工作目录路径"))
        Exit.add_argument("-W", "--WaitGames", action="store_false", help=self._("等待游戏结束后再退出 Claset, 默认将等待游戏结束"))


    # 命令实现
    @with_argparser(InstallGame)
    def do_InstallGame(self, init: Namespace):
        """安装游戏实例"""
        Downloader = Claset.getDownloader()
        GameInstaller = Claset.Game.GameInstaller(VersionName=init.GameName, MinecraftVersion=init.Version, Downloader=Downloader, WaitDownloader=False)
        GameInstaller.InstallVanilla()

        InstallProgressBar = Progress(
            TextColumn(self._("[yellow]安装游戏实例 [bold blue]\"{task.description}\""), justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            self._("[green]已完成[yellow]/[blue]需下载文件数[white]:[green]{task.completed}[yellow]/[blue]{task.total}"),
            console=self.RichConsole
        )

        if init.Version is not None:
            taskName = init.GameName + "-" + init.Version
        else:
            taskName = init.GameName

        with InstallProgressBar:
            ProgressBarID = InstallProgressBar.add_task(
                description=taskName,
                total=Downloader.getInfoFormProject(GameInstaller.MainDownloadProject, "AllTasksCount"),
                completed=Downloader.getInfoFormProject(GameInstaller.MainDownloadProject, "CompletedTasksCount"),
            )
            while not Downloader.isProjectCompleted(ProjectID=GameInstaller.MainDownloadProject):
                sleep(0.1)
                InstallProgressBar.update(
                    task_id=ProgressBarID,
                    total=Downloader.getInfoFormProject(GameInstaller.MainDownloadProject, "AllTasksCount"),
                    completed=Downloader.getInfoFormProject(GameInstaller.MainDownloadProject, "CompletedTasksCount"),
                )


    @with_argparser(LaunchGame)
    def do_LaunchGame(self, init: Namespace):
        """启动游戏实例"""
        UserID = None
        if init.UserUUID is not None:
            UserID = self.AccountManager.getAccountOtherInfo(Input=init.UserUUID, InputType="UUID", ReturnType="ID")
        elif init.UserName is not None:
            UserID = self.AccountManager.getAccountOtherInfo(Input=init.UserName, InputType="Name", ReturnType="ID")
        elif init.UserID is not None:
            UserID = init.UserID
        TheAccount = self.AccountManager.getAccountObject(UserID)

        try:
            GameLauncher = Claset.Game.GameLauncher(VersionName=init.GameName, Account=TheAccount)
        except Claset.Game.Launch.Exceptions.VersionNotFound:
            self.RichConsole.print("此游戏实例 \"{}\" 未找到".format(init.GameName))
            return

        GameLauncher.launchGame(PrintToTerminal=init.ShowGameLogs)


    def do_ListGame(self, _: Namespace):
        """列出所有游戏实例"""
        GameInfoList = Claset.Game.Utils.getVersionInfoList()
        if len(GameInfoList) == 0:
            self.RichConsole.print(self._("未找到任何游戏实例"))
            return

        GameTable = Table(self._("ID"), self._("实例名"), self._("实例版本"), self._("实例类型"), self._("实例位置"))
        for GameID in range(len(GameInfoList)):
            GameTable.add_row(str(GameID), *GameInfoList[GameID].getInfoList())

        self.RichConsole.print(GameTable)


    @with_argparser(CreateAccount)
    def do_CreateAccount(self, init: Namespace):
        """创建新账户"""
        match init.Type:
            case "MICROSOFT":
                self.AccountManager.create(Type=init.Type)
            case "OFFLINE":
                if init.AccountName is None:
                    raise ValueError(self._("设置账户类型为离线时用户名不应为空"))
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
        AccountTable = Table(self._("ID"), self._("账户名"), self._("UUID"), self._("账户类型"), self._("账户状态"))
        for Account in AccountList:
            AccountTable.add_row(str(Account["ID"]), Account["Name"], Account["UUID"], Account["Type"], Account["Status"])

        self.RichConsole.print(AccountTable)


    @with_argparser(SetDefaultAccount)
    def do_SetDefaultAccount(self, init: Namespace):
        """设定指定的账户为默认账户"""
        try:
            AccountList = self.AccountManager.getAccountList(ID=init.ID, UUID=init.UUID, Name=init.Name, Type=init.Type)
        except ValueError:
            self.RichConsole.print(self._("输入有误"))
            return

        if len(AccountList) == 0:
            self.RichConsole.print(self._("未找到符合输入的账户"))
            return
        elif len(AccountList) >= 2:
            self.RichConsole.print(self._("无法设置多个账户为默认"))
            return

        self.AccountManager.setDefault(AccountList[0]["ID"])
        self.AccountManager.save()


    @with_argparser(RemoveAccount)
    def do_RemoveAccount(self, init: Namespace):
        """删除指定的账户"""
        try:
            AccountList = self.AccountManager.getAccountList(ID=init.ID, UUID=init.UUID, Name=init.Name, Type=init.Type)
        except ValueError:
            self.RichConsole.print(self._("输入有误"))
            return

        if len(AccountList) == 0:
            self.RichConsole.print(self._("未找到符合输入的账户"))
        else:
            if init.Confirm:
                AccountTable = Table(self._("ID"), self._("账户名"), self._("UUID"), self._("账户类型"), self._("账户状态"))
                for Account in AccountList:
                    AccountTable.add_row(str(Account["ID"]), Account["Name"], Account["UUID"], Account["Type"], Account["Status"])
                self.RichConsole.print(self._("[white]由于此命令有一定的[red]危险性[white]，默认不执行，请在确认输出后附加参数 \"--Confirm\" 以确认执行，确认执行后将删除账户:"), AccountTable)
            else:
                for Account in AccountList:
                    self.AccountManager.remove(Account["ID"])
                self.AccountManager.save()


    @with_argparser(SetWorkDir)
    def do_SetWorkDir(self, init: Namespace):
        """指定新的工作目录"""
        try:
            Claset.Utils.setPerfix(init.NewWorkDir)
        except FileNotFoundError:
            self.RichConsole.print(self._("指定的新工作目录 \"{}\" 未找到").format(init.NewWorkDir))


    def do_GetWorkDir(self, _: Namespace):
        """指定新的工作目录"""
        self.RichConsole.print(Claset.Utils.Path.getcwd())


    @with_argparser(Exit)
    def do_Exit(self, init: Namespace):
        """退出程序"""
        Claset.stopALLDownloader()
        if init.WaitGames:
            Claset.waitALLGames()
        raise SystemExit
    do_exit = do_Exit
    do_quit = do_Exit

