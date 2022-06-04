# -*- coding: utf-8 -*-

from argparse import Namespace
from time import sleep
from typing import Any

from cmd2 import Cmd, with_argparser
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

import Claset
from Claset.Accounts.Account import Account

from .ArgumentParsers import *


class ClasetCommandLine(Cmd):
    """命令行模式主类"""

    RichConsole = Console()
    AccountManager = Claset.Accounts.AccountManager()
    Configs = Claset.Utils.Configs("Settings")

    # 移除部分内置函数
    # delattr(Cmd, "do_shell")
    # delattr(Cmd, "do_edit")
    delattr(Cmd, "do_quit")

    def _(self, message: str) -> str:
        """默认 i18n 文字处理器"""
        return message

    def getConsole(self) -> Console:
        """获取用于输出的 Rich Console"""
        return self.RichConsole

    def setI18nProcessor(self, Method: Any) -> None:
        """设置 i18n 文字处理器"""
        self._ = Method
        self.intro = self._("Claset - 内建命令行模式\n当前版本: {}").format(Claset.__fullversion__)
        self.prompt = self._("> ")

        # 使 Cmd2 的部分支持 i18n
        self.doc_header = self._(
            "Documented commands (use 'help -v' for verbose/'help <topic>' for details):"
        )
        self.help_error = self._("No help on {}")
        self.default_error = self._("{} is not a recognized command, alias, or macro")

    def getI18n(self) -> Any:
        """获取 i18n 文字处理器"""
        return self._

    # 命令实现
    @with_argparser(InstallGame)
    def do_InstallGame(self, init: Namespace):
        """安装游戏实例"""
        Downloader = Claset.getDownloader()
        GameInstaller = Claset.Game.GameInstaller(
            VersionName=init.GameName,
            MinecraftVersion=init.Version,
            Downloader=Downloader,
            WaitDownloader=False,
        )
        self.RichConsole.print(self._("正在检查已存在的文件..."))
        try:
            GameInstaller.InstallVanilla()
        except Claset.Game.Install.Exceptions.VanillaInstalled:
            self.RichConsole.print(
                self._('指定的版本名 "{}" 重复, 请使用其他版本名!').format(init.GameName)
            )
            return

        InstallProgressBar = Progress(
            TextColumn(
                self._('[yellow]安装游戏实例 [bold blue]"{task.description}"'),
                justify="right",
            ),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            self._(
                "[green]已完成[yellow]/[blue]需下载[cyan]文件数[white]:[green]{task.completed}[yellow]/[blue]{task.total}"
            ),
            console=self.RichConsole,
        )

        if init.Version is not None:
            taskName = init.GameName + "-" + init.Version
        else:
            taskName = init.GameName

        with InstallProgressBar:
            ProgressBarID = InstallProgressBar.add_task(
                description=taskName,
                total=Downloader.getInfoFormProject(
                    GameInstaller.MainDownloadProject, "AllTasksCount"
                ),
                completed=Downloader.getInfoFormProject(
                    GameInstaller.MainDownloadProject, "CompletedTasksCount"
                ),
            )
            while not Downloader.isProjectCompleted(
                ProjectID=GameInstaller.MainDownloadProject
            ):
                sleep(0.1)
                InstallProgressBar.update(
                    task_id=ProgressBarID,
                    total=Downloader.getInfoFormProject(
                        GameInstaller.MainDownloadProject, "AllTasksCount"
                    ),
                    completed=Downloader.getInfoFormProject(
                        GameInstaller.MainDownloadProject, "CompletedTasksCount"
                    ),
                )

    @with_argparser(LaunchGame)
    def do_LaunchGame(self, init: Namespace):
        """启动游戏实例"""
        UserID = None
        if init.UserUUID is not None:
            UserID = self.AccountManager.getAccountOtherInfo(
                Input=init.UserUUID, InputType="UUID", ReturnType="ID"
            )
        elif init.UserName is not None:
            UserID = self.AccountManager.getAccountOtherInfo(
                Input=init.UserName, InputType="Name", ReturnType="ID"
            )
        elif init.UserID is not None:
            UserID = init.UserID

        try:
            TheAccount = self.AccountManager.getAccountObject(UserID)
            GameLauncher = Claset.Game.GameLauncher(
                VersionName=init.GameName, Account=TheAccount
            )
        except Claset.Accounts.Exceptions.NoAccountsFound:
            self.RichConsole.print('未找到任何可用的账户, 请先使用 "CreateAccount" 命令新建账户')
        except Claset.Game.Launch.Exceptions.VersionNotFound:
            self.RichConsole.print('游戏实例 "{}" 未找到'.format(init.GameName))
        else:
            try:
                GameLauncher.launchGame(
                    Type=init.Type,
                    PrintToTerminal=init.ShowGameLogs,
                    SaveTo=init.SaveToFile,
                )
            except Claset.Game.Launch.Exceptions.UnsupportVersion:
                self.RichConsole.print("")

    def do_ListGame(self, _: Namespace):
        """列出所有游戏实例"""
        GameInfoList = Claset.Game.Utils.getVersionInfoList()
        if len(GameInfoList) == 0:
            self.RichConsole.print(self._("未找到任何游戏实例"))
            return

        GameTable = Table(
            self._("ID"), self._("实例名"), self._("实例版本"), self._("实例类型"), self._("实例位置")
        )
        for GameID in range(len(GameInfoList)):
            GameTable.add_row(
                str(GameID), *GameInfoList[GameID].getInfoStr().split("|")
            )

        self.RichConsole.print(GameTable)

    @with_argparser(RemoveGame)
    def do_RemoveGame(self, init: Namespace):
        """移除指定的游戏实例"""
        try:
            Claset.Game.Utils.removeGame(Name=init.GameName)
        except Claset.Game.Utils.Exceptions.TargetVersionNotFound:
            self.RichConsole.print(self._('游戏实例 "{}" 未找到').format(init.GameName))

    def do_ListLaunchedGame(self, _: Namespace):
        """列出运行过的游戏实例与状态"""
        if len(Claset.LaunchedGames) >= 1:
            GameInfoList = Claset.Game.Utils.getVersionInfoList()
            LaunchedGameTable = Table(
                self._("运行 ID"),
                self._("游戏 ID"),
                self._("实例名"),
                self._("运行状态"),
                self._("实例版本"),
                self._("实例类型"),
                self._("实例位置"),
            )
            for LaunchedGameID in range(len(Claset.LaunchedGames)):
                GameID = None
                for GameInfoID in range(len(GameInfoList)):
                    if (
                        GameInfoList[GameInfoID].Name
                        == Claset.LaunchedGames[LaunchedGameID].VersionInfos.Name
                    ):
                        GameID = GameInfoID
                LaunchedGameTable.add_row(
                    *Claset.LaunchedGames[LaunchedGameID]
                    .VersionInfos.getInfoStr(
                        Format="{LaunchedGameID}|{GameID}|{Name}|{Status}|{Version}|{Type}|{Dir}",
                        OtherKeys={
                            "LaunchedGameID": LaunchedGameID,
                            "GameID": GameID,
                            "Status": Claset.LaunchedGames[LaunchedGameID].getStatus(),
                        },
                    )
                    .split("|")
                )
            self.RichConsole.print(LaunchedGameTable)
        else:
            self.RichConsole.print(self._("无运行过的游戏实例"))

    @with_argparser(StopRunningGame)
    def do_StopLaunchedGame(self, init: Namespace):
        """停止运行中的游戏"""
        Claset.LaunchedGames[init.RUNID].stopGame()

    @with_argparser(CreateAccount)
    def do_CreateAccount(self, init: Namespace):
        """创建新账户"""
        match init.Type:
            case "MICROSOFT":
                Account = self.AccountManager.create(Type=init.Type)
            case "OFFLINE":
                if init.AccountName is None:
                    raise ValueError(self._("设置账户类型为离线时用户名不应为空"))
                else:
                    Account = self.AccountManager.create(
                        Type=init.Type, Name=init.AccountName
                    )
            case _:
                ValueError(init.Type)
        self.AccountManager.add(Account=Account)
        self.AccountManager.save()

    def do_ListAccount(self, _: Namespace):
        """列出所有账户"""
        AccountList = self.AccountManager.getAccountList()
        if len(AccountList) == 0:
            print("账户列表为空")
            return

        # 构建列表
        AccountTable = Table(
            self._("ID"), self._("账户名"), self._("UUID"), self._("账户类型"), self._("账户状态")
        )
        for Account in AccountList:
            AccountTable.add_row(
                str(Account["ID"]),
                Account["Name"],
                Account["UUID"],
                Account["Type"],
                Account["Status"],
            )

        self.RichConsole.print(AccountTable)

    @with_argparser(SetDefaultAccount)
    def do_SetDefaultAccount(self, init: Namespace):
        """设定指定的账户为默认账户"""
        try:
            AccountList = self.AccountManager.getAccountList(
                ID=init.ID, UUID=init.UUID, Name=init.Name, Type=init.Type
            )
        except ValueError:
            self.RichConsole.print(self._("[red]输入有误"))
            return

        if len(AccountList) == 0:
            self.RichConsole.print(self._("[red]未找到符合输入的账户"))
        elif len(AccountList) >= 2:
            self.RichConsole.print(self._("[red]无法设置多个账户为默认"))
        else:
            AccountName = AccountList[0]["Name"]
            self.RichConsole.print(
                self._('[green]已设置账户 "{AccountName}" 为默认账户').format(
                    AccountName=AccountName
                )
            )
            self.AccountManager.setDefault(AccountList[0]["ID"])
            self.AccountManager.save()

    @with_argparser(RemoveAccount)
    def do_RemoveAccount(self, init: Namespace):
        """移除指定的账户"""
        try:
            AccountList = self.AccountManager.getAccountList(
                ID=init.ID, UUID=init.UUID, Name=init.Name, Type=init.Type
            )
        except ValueError:
            self.RichConsole.print(self._("[red]输入有误"))
            return

        if len(AccountList) == 0:
            self.RichConsole.print(self._("[red]未找到符合输入的账户"))
        else:
            if init.Confirm:
                AccountTable = Table(
                    self._("ID"),
                    self._("账户名"),
                    self._("UUID"),
                    self._("账户类型"),
                    self._("账户状态"),
                )
                for Account in AccountList:
                    AccountTable.add_row(
                        str(Account["ID"]),
                        Account["Name"],
                        Account["UUID"],
                        Account["Type"],
                        Account["Status"],
                    )
                self.RichConsole.print(
                    self._(
                        '由于此命令有一定的[red]危险性[white]，默认不执行，请在确认输出后附加参数 "--Confirm" 以确认执行，确认执行后将删除账户:'
                    ),
                    AccountTable,
                )
            else:
                AccountNameList = list()
                for Account in AccountList:
                    self.AccountManager.remove(Account["ID"])
                    AccountNameList.append(Account["Name"])
                if init.Now:
                    self.AccountManager.removeNow()
                    self.RichConsole.print(
                        self._("已移除账户 {}, 并使其立即生效(完全从配置文件中移除)").format(AccountNameList)
                    )
                else:
                    self.RichConsole.print(
                        self._("已移除账户 {}, 将在下次启动时生效(完全从配置文件中移除)").format(
                            AccountNameList
                        )
                    )
                self.AccountManager.save()

    @with_argparser(SetWorkDir)
    def do_SetWorkDir(self, init: Namespace):
        """指定新的工作目录"""
        try:
            Claset.Utils.setPerfix(init.NewWorkDir)
        except FileNotFoundError:
            self.RichConsole.print(self._('指定的新工作目录 "{}" 未找到').format(init.NewWorkDir))
        else:
            # 重载部分配置
            if init.ReloadConfigs:
                self.AccountManager.Configs.reload()
                Claset.Utils.Download.reloadDownloadConfig()

    def do_GetWorkDir(self, _: Namespace):
        """打印当前工作目录"""
        self.RichConsole.print(Claset.Utils.Path.getcwd())

    @with_argparser(Exit)
    def do_Exit(self, init: Namespace):
        """退出程序"""
        Claset.stopALLDownloader()
        if init.WaitGames:
            Claset.waitALLGames()
        self.exit_code
        raise SystemExit

    do_exit = do_Exit
    do_quit = do_Exit
