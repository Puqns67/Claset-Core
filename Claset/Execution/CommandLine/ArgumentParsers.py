# -*- coding: utf-8 -*-

from typing import Any

from cmd2 import Cmd2ArgumentParser

from .I18n import simpleI18n

InstallGame = Cmd2ArgumentParser()
LaunchGame = Cmd2ArgumentParser()
RemoveGame = Cmd2ArgumentParser()
StopRunningGame = Cmd2ArgumentParser()
CreateAccount = Cmd2ArgumentParser()
RemoveAccount = Cmd2ArgumentParser()
SetDefaultAccount = Cmd2ArgumentParser()
SetWorkDir = Cmd2ArgumentParser()
Exit = Cmd2ArgumentParser()


def addArgumentToParsers(i18nProcessor: Any | None = None) -> None:
    """为参数解析器附加参数"""
    _ = i18nProcessor if i18nProcessor else simpleI18n

    InstallGame.add_argument("-V", "--Version", help=_("游戏版本, 不指定时使用最新的正式版"))
    InstallGame.add_argument("GameName", help=_("游戏实例名"))
    LaunchGame.add_argument(
        "-T",
        "--Type",
        default="SUBPROCESS",
        choices=(
            "SUBPROCESS",
            "SAVESCRIPT",
        ),
        help=_('指定启动模式, 现支持 "SUBPROCESS" 和 "SAVESCRIPT", 默认为 "SUBPROCESS"'),
    )
    LaunchGame.add_argument(
        "-Un", "--UserName", default=None, help=_("指定账户的类型为名称, 如有重复则按账户顺序取第一个")
    )
    LaunchGame.add_argument("-Uu", "--UserUUID", default=None, help=_("指定账户的类型为 UUID"))
    LaunchGame.add_argument(
        "-Ui",
        "--UserID",
        default=None,
        type=int,
        help=_("指定账户 ID, 此 ID 为在配置文件中的序列号"),
    )
    LaunchGame.add_argument("--ShowGameLogs", action="store_true", help=_("输出运行日志至终端"))
    LaunchGame.add_argument("--SaveToFile", default=None, help=_("指定保存运行脚本的路径"))
    LaunchGame.add_argument("GameName", help=_("游戏实例名"))
    RemoveGame.add_argument("GameName", help=_("游戏实例名"))
    CreateAccount.add_argument(
        "-N", "--AccountName", help=_("账户名称, 此选项仅可使用在账户类型为离线时使用")
    )
    CreateAccount.add_argument(
        "-T",
        "--Type",
        default="MICROSOFT",
        choices=(
            "MICROSOFT",
            "OFFLINE",
        ),
        help=_('账户类型, 现支持 "OFFLINE" 和 "MICROSOFT" 类型, 默认为 "MICROSOFT"'),
    )
    RemoveAccount.add_argument(
        "-N", "--Name", default=None, help=_("指定账户的游戏内名称, 使用此参数时将有可能删除多个账户")
    )
    RemoveAccount.add_argument(
        "-T", "--Type", default=None, help=_("指定账户类型, 使用此参数时将有可能删除多个账户")
    )
    RemoveAccount.add_argument(
        "-i",
        "--ID",
        default=None,
        type=int,
        help=_("指定账户 ID, 此 ID 为在配置文件中的序列号"),
    )
    RemoveAccount.add_argument("-I", "--UUID", default=None, help=_("指定账户 UUID"))
    RemoveAccount.add_argument(
        "-C",
        "--Confirm",
        action="store_false",
        help=_("由于此命令有危害性, 您可以使用此参数以确认执行"),
    )
    RemoveAccount.add_argument(
        "--Now", action="store_false", help=_("立即从配置文件中移除已被删除的账户, 默认为下次启动时移除")
    )
    StopRunningGame.add_argument("RUNID", default=None, type=int, help=_("运行 ID"))
    SetDefaultAccount.add_argument(
        "-N", "--Name", default=None, help=_("指定账户的游戏内名称, 使用此参数时将有可能删除多个账户")
    )
    SetDefaultAccount.add_argument(
        "-T", "--Type", default=None, help=_("指定账户类型, 使用此参数时将有可能删除多个账户")
    )
    SetDefaultAccount.add_argument(
        "-i",
        "--ID",
        default=None,
        type=int,
        help=_("指定账户 ID, 此 ID 为在配置文件中的序列号"),
    )
    SetDefaultAccount.add_argument("-I", "--UUID", default=None, help=_("指定账户 UUID"))
    SetWorkDir.add_argument(
        "-R", "--ReloadConfigs", action="store_false", help=_("重载部分配置文件")
    )
    SetWorkDir.add_argument("NewWorkDir", default=None, help=_("新的工作目录路径"))
    Exit.add_argument(
        "-W",
        "--WaitGames",
        action="store_false",
        help=_("等待游戏结束后再退出 Claset, 默认将等待游戏结束"),
    )
