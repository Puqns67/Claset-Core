# -*- coding: utf-8 -*-
"""管理账户"""

from logging import getLogger
from typing import Any
from uuid import UUID as Class_UUID, uuid4
from copy import deepcopy

from Claset.Utils import Configs

from .AccountAPIs import MicrosoftAuthAPI, MinecraftAccountAPI
from .Account import Account

from .Exceptions import *

Logger = getLogger(__name__)
Accounts = dict()


class AccountManager():
    """账户管理器"""
    def __init__(self):
        self.Configs = Configs(ID="Accounts")
        self.removeNow()
        self.save()


    def create(self, Type: str = "OFFLINE", Name: str | None = None) -> None:
        """创建账户"""
        Logger.debug("Create new account by Type: %s", Type)
        NewAccount = {"Type": Type, "Status": "NORMAL"}
        match Type:
            case "OFFLINE":
                if (Name is None) or (Name == str()):
                    raise ValueError("OFFLINE type Account Name cannot be None")
                else:
                    NewAccount["Name"] = Name
                    NewAccount["UUID"] = uuid4().hex
            case "MICROSOFT":
                MicrosoftOAuthTask = MicrosoftAuthAPI()
                MicrosoftOAuthTask.auth()
                MicrosoftOAuthTask.authToMinectaft()
                Account = MinecraftAccountAPI(MicrosoftOAuthTask.MinecraftAccessToken)
                NewAccount["Name"] = Account.Name
                NewAccount["UUID"] = Account.UUID.hex
                NewAccount["MicrosoftAccountAccessToken"] = MicrosoftOAuthTask.MicrosoftAccountAccessToken
                NewAccount["MicrosoftAccountRefreshToken"] = MicrosoftOAuthTask.MicrosoftAccountRefreshToken
                NewAccount["MicrosoftAccountAccessTokenExpiresTime"] = MicrosoftOAuthTask.MicrosoftAccountAccessTokenExpiresTime
            case _: UnsupportedAccountType(Type)

        self.Configs["Accounts"].append(NewAccount)

        # 如果新建用户后只有一个账户存在, 则使其成为默认账户
        if len(self.Configs["Accounts"]) == 1:
            Logger.debug("Set this account's status to \"DEFAULT\"")
            self.setDefault(ID=0)


    def remove(self, ID: int) -> None:
        """通过账户 ID 删除对应的账户(设置账户状态为 DELETE)"""
        # 若要删除的账户为默认账户, 则设置另一个账户为默认
        match self.Configs["Accounts"][ID]["Status"]:
            case "DEFAULT":
                if len(self.Configs["Accounts"]) >= 1:
                    self.Configs["DefaultAccount"] = 0
                else:
                    self.Configs["DefaultAccount"] = None
            case "DELETE":
                Logger.warning("Account ({}) deleted, Skipping it".format(self.Configs["Accounts"][ID]["Name"]))
                return

        # 设置移除账户的状态
        self.Configs["Accounts"][ID]["Status"] = "DELETE"
        Logger.info("Removeing account {}".format(self.Configs["Accounts"][ID]["Name"]))


    def removeNow(self) -> None:
        """立即移除状态为 DELETE 的账户"""
        if self.Configs["DefaultAccount"] is not None:
            DefaultAccount = self.Configs["Accounts"][self.Configs["DefaultAccount"]]
        else:
            DefaultAccount = None

        for Account in deepcopy(self.Configs["Accounts"]):
            if Account["Status"] == "DELETE":
                self.Configs["Accounts"].remove(Account)

        if DefaultAccount:
            self.Configs["DefaultAccount"] = self.Configs["Accounts"].index(DefaultAccount)


    def save(self) -> None:
        """保存账户数据"""
        self.Configs.save()


    def setDefault(self, ID: int, RaiseException=True) -> None:
        """设置默认账户 ID"""
        if (ID <= -1) or (len(self.Configs["Accounts"]) - 1 < ID):
            if RaiseException:
                raise AccountNotFound
            else:
                Logger.warning("Account ({})  not found, Skipping it".format(self.Configs["Accounts"][ID]["Name"]))
                return
        if self.Configs["Accounts"][ID]["Status"] == "DELETE":
            if RaiseException:
                raise AccountDeleted
            else:
                Logger.warning("Account ({}) deleted, Skipping it".format(self.Configs["Accounts"][ID]["Name"]))
                return
        # 将老的默认账户的状态还原
        if self.Configs["DefaultAccount"] is not None:
            self.Configs["Accounts"][self.Configs["DefaultAccount"]]["Status"] = "NORMAL"
        self.Configs["DefaultAccount"] = ID
        self.Configs["Accounts"][ID]["Status"] = "DEFAULT"


    def getDefault(self) -> int:
        """获取默认账户 ID"""
        if self.Configs["DefaultAccount"] is None:
            raise NoAccountsFound
        return(self.Configs["DefaultAccount"])


    def updateInfo(self, UUID: Class_UUID, New: dict) -> None:
        """通过 UUID 更新对应账户的信息"""
        for i in range(len(self.Configs["Accounts"])):
            if self.Configs["Accounts"][i]["UUID"] == UUID.hex:
                self.Configs["Accounts"][i] = New


    def getAccountObject(self, ID: int | None = None) -> Account:
        """通过用户 ID 获取对应的 AccountObject"""
        if ID is None: ID = self.getDefault()
        if ID not in Accounts: Accounts[ID] = Account(Account=self.Configs["Accounts"][ID], Manager=self)
        return(Accounts[ID])


    def getAccountList(self, ID: int | None = None, UUID: Class_UUID | str | None = None, Name: str | None = None, Type: str | None = None) -> list[dict]:
        """获取以各种方式过滤后的用户列表"""
        Output = list()
        for AccountID in range(len(self.Configs["Accounts"])):
            if (ID is not None) and (AccountID != ID):
                continue
            Account = deepcopy(self.Configs["Accounts"][AccountID])
            if UUID is not None:
                if isinstance(UUID, Class_UUID) and (UUID.hex != Account["UUID"]):
                    continue
                elif UUID != Account["UUID"]:
                    continue
            if (Name is not None) and (Account["Name"] != Name):
                continue
            if (Type is not None) and (Account["Type"] != Type):
                continue
            Account["ID"] = AccountID
            Output.append(Account)
        return(Output)


    def getAccountOtherInfo(self, Input: Any, InputType: str, ReturnType: str) -> Any:
        """获取账户相关信息, 如有重复则返回第一个"""
        kwarg = dict()
        kwarg[InputType] = Input
        return(self.getAccountList(**kwarg)[0][ReturnType])

