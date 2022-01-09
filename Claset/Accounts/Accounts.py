# -*- coding: utf-8 -*-
"""管理账户"""

from Claset.Utils import Configs, encodeBase64, decodeBase64

from .Auth import MicrosoftOAuth

from .Exceptions import *
from .Auth import Exceptions as Ex_Auth

ACCOUNT_TYPES = ("OFFLINE", "MICROSOFT", "MOJANG",)

class AccountManager():
    def __init__(self):
        self.UserConfigs = Configs(ID="Users", TargetVersion=0)


    def create(self, Name: str, Type: str = "OFFLINE", Password: str | None = None) -> None:
        """创建账户"""
        if not Type in ACCOUNT_TYPES: raise UnsupportedAccountType(Type)
        try:
            self.getAccountID(Name)
        except AccountNotFound:
            NewUser = {"Name": Name, "UserType": Type}

            if len(self.UserConfigs["Users"]) == 0: NewUser["Default"] = True
            else: NewUser["Default"] = False

            match Type:
                case "OFFLINE":
                    NewUser["Password"] = None
                case "MICROSOFT":
                    NewUser["Token"] = MicrosoftOAuth.GameToken
                case "MOJANG":
                    if Password == None: raise ValueError("Password is None")
                    NewUser["Password"] = encodeBase64(Password)

            self.UserConfigs["Users"].append(NewUser)
            return(None)
        raise AccountDuplicate(f"Duplicate user: {Name}")


    def remove(self, Name: str) -> None:
        """通过账户名删除账户"""
        self.UserConfigs["Users"].remove(self.UserConfigs["Users"][self.userID(Name)])
        # 若要删除的账户为默认账户, 则设置另一个账户为默认
        self.getDefault()


    def save(self) -> None:
        """保存账户数据"""
        self.UserConfigs.saveConfig()


    def setDefault(self, Name: str) -> None:
        """设置默认账户"""
        Users = self.UserConfigs["Users"]
        Users[self.getDefault()]["Default"] = False
        Users[self.userID(Name)]["Default"] = True
        self.UserConfigs["Users"] = Users


    def getDefault(self) -> int:
        """返回默认账户的id, 若不存在默认账户则设置 0 号账户为默认账户"""
        for i in range(len(self.UserConfigs["Users"])):
            if self.UserConfigs["Users"][i]["Default"] == True:
                return(i)
        if len(self.UserConfigs["Users"]) >= 1:
            self.UserConfigs["Users"][0]["Default"] = True
            return(0)


    def getAccountID(self, Name: str) -> int:
        """通过账户名获取账户ID"""
        Output = None
        for i in range(len(self.UserConfigs["Users"])):
            if self.UserConfigs["Users"][i]["Name"] == Name:
                Output = i
                break
        if Output == None: raise AccountNotFound(f"User \"{Name}\" Not found")
        return(Output)

