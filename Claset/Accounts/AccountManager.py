# -*- coding: utf-8 -*-
"""管理账户"""

from logging import getLogger
from uuid import UUID as Class_UUID, uuid4

from Claset.Utils import Configs

from .Auth import Auth
from .Account import Account
from .MinecraftAccount import MinecraftAccount

from .Exceptions import *

ACCOUNT_TYPES = ("OFFLINE", "MICROSOFT",)
ACCOUNT_STATUS = ("DELETE", "NORMAL", "DEFAULT")
Logger = getLogger(__name__)


class AccountManager():
    """账户管理器"""
    def __init__(self):
        self.Configs = Configs(ID="Accounts")

        for Account in self.Configs["Accounts"]:
            if Account["Status"] == "DELETE":
                self.Configs["Accounts"].remove(Account)

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
                MicrosoftOAuthTask = Auth()
                MicrosoftOAuthTask.auth()
                MicrosoftOAuthTask.authToMinectaft()
                Account = MinecraftAccount(MicrosoftOAuthTask.MinecraftAccessToken)
                NewAccount["Name"] = Account.Name
                NewAccount["UUID"] = Account.UUID.hex
                NewAccount["MicrosoftAccountAccessToken"] = MicrosoftOAuthTask.MicrosoftAccountAccessToken
                NewAccount["MicrosoftAccountRefreshToken"] = MicrosoftOAuthTask.MicrosoftAccountRefreshToken
                NewAccount["MicrosoftAccountAccessTokenExpiresTime"] = MicrosoftOAuthTask.MicrosoftAccountAccessTokenExpiresTime
            case _: UnsupportedAccountType(Type)

        self.Configs["Accounts"].append(NewAccount)

        # 如果新建用户后只有一个账户存在，则使其成为默认账户
        if len(self.Configs["Accounts"]) == 1:
            Logger.debug("Set this account's status to \"DEFAULT\"")
            self.setDefault(ID=0)


    def remove(self, ID: int) -> None:
        """通过账户 ID 删除对应的账户"""
        # 若要删除的账户为默认账户, 则设置另一个账户为默认
        match self.Configs["Accounts"][ID]["Status"]:
            case "DEFAULT":
                if len(self.Configs["Accounts"]) >= 2:
                    self.Configs["DefaultAccount"] = 0
                else:
                    self.Configs["DefaultAccount"] = None
            case "DELETE":
                Logger.warning("This account is deleted, Skipping it")
                return(None)

        # 设置移除账户的状态
        self.Configs["Accounts"][ID]["Status"] = "DELETE"


    def save(self) -> None:
        """保存账户数据"""
        self.Configs.saveConfig()


    def setDefault(self, ID: int) -> None:
        """设置默认账户 ID"""
        if (ID <= -1) or (len(self.Configs["Accounts"]) - 1 < ID):
            raise AccountNotFound
        # 将老的默认账户的状态还原
        if self.Configs["DefaultAccount"] != None:
            self.Configs["Accounts"][self.Configs["DefaultAccount"]]["Status"] = "NORMAL"
        self.Configs["DefaultAccount"] = ID
        self.Configs["Accounts"][ID]["Status"] = "DEFAULT"


    def getDefault(self) -> int:
        """获取默认账户 ID"""
        if self.Configs["DefaultAccount"] == None:
            raise NoAccountsFound
        return self.Configs["DefaultAccount"]


    def updateInfo(self, UUID: Class_UUID, New: dict) -> None:
        """通过 UUID 更新对应账户的信息"""
        for i in range(len(self.Configs["Accounts"])):
            if self.Configs["Accounts"][i]["UUID"] == UUID.hex:
                self.Configs["Accounts"][i] = New


    def getAccountObject(self, ID: int | None = None) -> Account:
        """通过用户 ID 获取对应的 AccountObject"""
        if ID == None: ID = self.getDefault()
        return(Account(Account=self.Configs["Accounts"][ID], Manager=self))


    def getAccountList(self, ID: int | None = None, UUID: Class_UUID | str | None = None, Name: str | None = None, Type: str | None = None) -> list[dict]:
        """获取以各种方式过滤后的用户列表"""
        Output = list()
        for AccountID in range(len(self.Configs["Accounts"])):
            Account = self.Configs["Accounts"][AccountID]
            if (ID != None) and (AccountID != ID):
                continue
            if UUID != None:
                if (type(UUID) == type(Class_UUID)) and (UUID.hex != Account["UUID"]):
                    continue
                elif UUID != Account["UUID"]:
                    continue
            if (Name != None) and (Account["Name"] != Name):
                continue
            if (Type != None) and (Account["Type"] != Type):
                continue
            Account["ID"] = AccountID
            Output.append(Account)
        return(Output)

