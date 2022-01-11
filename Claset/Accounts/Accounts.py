# -*- coding: utf-8 -*-
"""管理账户"""

from Claset.Utils import Configs, encodeBase64, decodeBase64

from .Auth import MicrosoftOAuth, Exceptions as Ex_Auth

from .Exceptions import *

ACCOUNT_TYPES = ("OFFLINE", "MICROSOFT", "MOJANG",)


class AccountManager():
    """账户管理器"""
    def __init__(self):
        self.Configs = Configs(ID="Accounts")


    def create(self, Type: str = "OFFLINE", Name: str | None = None, Password: str | None = None) -> None:
        """创建账户"""
        NewAccount = {"Type": Type}
        match Type:
            case "OFFLINE":
                if Name == None:
                    raise ValueError("OFFLINE type Account Name cannot be None")
                else:
                    NewAccount["Name"] = Name
                    NewAccount["Password"] = None
            case "MICROSOFT":
                MicrosoftOAuthTask = MicrosoftOAuth()
                MicrosoftOAuthTask.auth()
                NewAccount["MicrosoftAccountAccessToken"] = MicrosoftOAuthTask.AccessToken
                NewAccount["MicrosoftAccountRefreshToken"] = MicrosoftOAuthTask.RefreshToken
            case "MOJANG":
                if Name == None: raise ValueError("OFFLINE type Account Name cannot be None")
                if Password == None: raise ValueError("Password is None")
                NewAccount["Name"] = Name
                NewAccount["Password"] = encodeBase64(Password)
            case _: UnsupportedAccountType(Type)
        self.Configs["Accounts"].append(NewAccount)


    def remove(self, ID: int) -> None:
        """通过账户ID删除对应的账户"""
        # 若要删除的账户为默认账户, 则设置另一个账户为默认
        if self.Configs["DefaultAccount"] == ID:
            if len(self.Configs["Accounts"]) >= 1:
                self.Configs["DefaultAccount"] = 0
            else:
                self.Configs["DefaultAccount"] = None
        self.Configs["Accounts"].remove(self.Configs["Accounts"][ID])


    def save(self) -> None:
        """保存账户数据"""
        self.Configs.saveConfig()


    def setDefault(self, ID: int) -> None:
        """设置默认账户"""
        if (ID <= -1) or (len(self.Configs["Accounts"]) - 1 < ID): raise AccountNotFound
        self.Configs["DefaultAccount"] = ID


    def refreshMicrosoftToken(self, ID: int) -> None:
        """刷新Microsoft账户访问Token"""
        if self.Configs["Accounts"][ID]["Type"] != "MICROSOFT":
            raise UnsupportedAccountType(self.Configs["Accounts"][ID]["Type"])

        MicrosoftOAuthTask = MicrosoftOAuth(RefreshToken=self.Configs["Accounts"][ID]["MicrosoftAccountRefreshToken"])
        MicrosoftOAuthTask.refresh()
        self.Configs["Accounts"][ID]["MicrosoftAccountAccessToken"] = MicrosoftOAuthTask.AccessToken
        self.Configs["Accounts"][ID]["MicrosoftAccountRefreshToken"] = MicrosoftOAuthTask.RefreshToken
