# -*- coding: utf-8 -*-
"""管理账户"""

from uuid import uuid4

from Claset.Utils import Configs

from .Auth import Auth
from .MinecraftAccountManager import MinecraftAccount

from .Exceptions import *

ACCOUNT_TYPES = ("OFFLINE", "MICROSOFT",)


class AccountManager():
    """账户管理器"""
    def __init__(self):
        self.Configs = Configs(ID="Accounts")


    def create(self, Type: str = "OFFLINE", Name: str | None = None) -> None:
        """创建账户"""
        NewAccount = {"Type": Type}
        match Type:
            case "OFFLINE":
                if Name == None:
                    raise ValueError("OFFLINE type Account Name cannot be None")
                else:
                    NewAccount["Name"] = Name
                    NewAccount["UUID"] = uuid4().hex
            case "MICROSOFT":
                MicrosoftOAuthTask = Auth()
                MicrosoftOAuthTask.auth()
                MicrosoftOAuthTask.authToMinectaft()
                Account = MinecraftAccount(MicrosoftOAuthTask.MinecraftAccessToken)
                NewAccount["Name"] = Account.Name
                NewAccount["UUID"] = Account.UUID.hex
                NewAccount["MicrosoftAccountAccessToken"] = MicrosoftOAuthTask.MicrosoftAccountAccessToken
                NewAccount["MicrosoftAccountRefreshToken"] = MicrosoftOAuthTask.MicrosoftAccountRefreshToken
            case _: UnsupportedAccountType(Type)
        self.Configs["Accounts"].append(NewAccount)

        # 如果新建用户后只有一个账户存在，则使其成为默认账户
        if len(self.Configs["Accounts"]) == 1:
            self.setDefault(ID=0)


    def remove(self, ID: int) -> None:
        """通过账户 ID 删除对应的账户"""
        # 若要删除的账户为默认账户, 则设置另一个账户为默认
        if self.Configs["DefaultAccount"] == ID:
            if len(self.Configs["Accounts"]) >= 1:
                self.Configs["DefaultAccount"] = 0
            else:
                self.Configs["DefaultAccount"] = None

        # 移除账户
        self.Configs["Accounts"].remove(self.Configs["Accounts"][ID])


    def save(self) -> None:
        """保存账户数据"""
        self.Configs.saveConfig()


    def setDefault(self, ID: int) -> None:
        """设置默认账户"""
        if (ID <= -1) or (len(self.Configs["Accounts"]) - 1 < ID): raise AccountNotFound
        self.Configs["DefaultAccount"] = ID


    def refreshMicrosoftToken(self, ID: int) -> Auth:
        """刷新 Microsoft 账户访问 Token"""
        if self.Configs["Accounts"][ID]["Type"] != "MICROSOFT":
            raise UnsupportedAccountType(self.Configs["Accounts"][ID]["Type"])

        MicrosoftOAuthTask = Auth(RefreshToken=self.Configs["Accounts"][ID]["MicrosoftAccountRefreshToken"])
        MicrosoftOAuthTask.refresh()
        self.Configs["Accounts"][ID]["MicrosoftAccountAccessToken"] = MicrosoftOAuthTask.MicrosoftAccountAccessToken
        self.Configs["Accounts"][ID]["MicrosoftAccountRefreshToken"] = MicrosoftOAuthTask.MicrosoftAccountRefreshToken

        return(MicrosoftOAuthTask)


    def getMinectaftAccessToken(self, ID: int) -> str:
        """获取对应 ID 用户的 Minecraft Access Token"""
        match self.Configs["Accounts"][ID]["Type"]:
            case "MICROSOFT":
                MicrosoftOAuthTask = self.refreshMicrosoftToken(ID=ID)
                MicrosoftOAuthTask.authToMinectaft()
                return(MicrosoftOAuthTask.MinecraftAccessToken)
            case _:
                raise UnsupportedAccountType(self.Configs["Accounts"][ID]["Type"])

