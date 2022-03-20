# -*- coding: utf-8 -*-

from typing import Any
from uuid import UUID, uuid4
from time import time

from .Auth import Auth

from .Exceptions import UnsupportedAccountType


class Account():
    """通用账户类"""
    def __init__(self, Account: dict, Manager: Any):
        self.Name: str = Account["Name"]
        self.Type: str = Account["Type"]
        self.UUID = UUID(Account["UUID"])
        self.TheAccount = Account
        self.TheManager = Manager

        if self.Type == "MICROSOFT":
            self.MicrosoftOAuthTask = Auth(self.TheAccount["MicrosoftAccountRefreshToken"])


    def refreshToken(self, WithMicrosoft: bool = False) -> None:
        """刷新 Microsoft 账户访问 Token"""
        if self.Type != "MICROSOFT":
            raise UnsupportedAccountType(self.Type)

        if WithMicrosoft:
            self.MicrosoftOAuthTask.refresh()
            self.TheAccount["MicrosoftAccountAccessToken"] = self.MicrosoftOAuthTask.MicrosoftAccountAccessToken
            self.TheAccount["MicrosoftAccountRefreshToken"] = self.MicrosoftOAuthTask.MicrosoftAccountRefreshToken
            self.TheAccount["MicrosoftAccountAccessTokenExpiresTime"] = self.MicrosoftOAuthTask.MicrosoftAccountAccessTokenExpiresTime

        self.MicrosoftOAuthTask.authToMinectaft()
        self.TheAccount["MinecraftAccessToken"] = self.MicrosoftOAuthTask.MinecraftAccessToken
        self.TheAccount["MinecraftAccessTokenExpiresTime"] = self.MicrosoftOAuthTask.MinecraftAccessTokenExpiresTime

        self.TheManager.updateInfo(UUID=self.UUID, New=self.TheAccount)
        self.TheManager.save()


    def getAccessToken(self) -> str:
        """获取对应 ID 用户的 Minecraft Access Token"""
        match self.Type:
            case "MICROSOFT":
                if "MinecraftAccessToken" in self.TheAccount and "MinecraftAccessTokenExpiresTime" in self.TheAccount:
                    if not (self.TheAccount["MinecraftAccessTokenExpiresTime"] >= int(time())):
                        if self.TheAccount["MicrosoftAccountAccessTokenExpiresTime"] >= int(time()):
                            self.refreshToken(WithMicrosoft=False)
                        else:
                            self.refreshToken(WithMicrosoft=True)
                else:
                    if self.TheAccount["MicrosoftAccountAccessTokenExpiresTime"] >= int(time()):
                        self.refreshToken(WithMicrosoft=False)
                    else:
                        self.refreshToken(WithMicrosoft=True)
                return(self.TheAccount["MinecraftAccessToken"])
            case "OFFLINE":
                return(uuid4().hex)
            case _:
                raise UnsupportedAccountType(self.Type)


    def getShortType(self) -> str:
        """获取简短类型"""
        return({"OFFLINE": uuid4().hex, "MICROSOFT": "msa"}[self.Type])

