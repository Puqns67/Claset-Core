# -*- coding: utf-8 -*-

from typing import Any
from uuid import UUID, uuid4

from .Auth import Auth

from .Exceptions import UnsupportedAccountType


class Account():
    def __init__(self, Account: dict, Manager: Any):
        self.Name: str = Account["Name"]
        self.Type: str = Account["Type"]
        self.UUID = UUID(Account["UUID"])
        self.TheAccount = Account
        self.TheManager = Manager

        if self.Type == "MICROSOFT":
            self.MicrosoftOAuthTask = Auth(self.TheAccount["MicrosoftAccountRefreshToken"])


    def refreshToken(self) -> None:
        """刷新 Microsoft 账户访问 Token"""
        if self.Type != "MICROSOFT":
            raise UnsupportedAccountType(self.Type)

        self.MicrosoftOAuthTask.refresh()
        self.TheAccount["MicrosoftAccountAccessToken"] = self.MicrosoftOAuthTask.MicrosoftAccountAccessToken
        self.TheAccount["MicrosoftAccountRefreshToken"] = self.MicrosoftOAuthTask.MicrosoftAccountRefreshToken
        self.TheManager.updateInfo(UUID=self.UUID, Key="MicrosoftAccountAccessToken", To=self.MicrosoftOAuthTask.MicrosoftAccountAccessToken)
        self.TheManager.updateInfo(UUID=self.UUID, Key="MicrosoftAccountRefreshToken", To=self.MicrosoftOAuthTask.MicrosoftAccountRefreshToken)
        self.TheManager.save()


    def getAccessToken(self) -> str:
        """获取对应 ID 用户的 Minecraft Access Token"""
        match self.Type:
            case "MICROSOFT":
                self.refreshToken()
                self.MicrosoftOAuthTask.authToMinectaft()
                return(self.MicrosoftOAuthTask.MinecraftAccessToken)
            case "OFFLINE":
                return(uuid4().hex)
            case _:
                raise UnsupportedAccountType(self.Type)

