# -*- coding: utf-8 -*-
"""管理用户"""

from base64 import b64encode, b64decode

from .Configs import Configs
from .File import saveFile
from .Path import path, pathAdder

from .Confs import ConfigIDs
from .Exceptions import User as Ex_User

class User():
    def __init__(self):
        self.UserConfigs = Configs().getConfig(ID="Users", TargetVersion=0)
        self.Users: list = self.UserConfigs["Users"]


    def create(self, Name: str, UserType: str, Password: str | None = None) -> None:
        """创建用户"""
        try:
            self.userID(Name)
        except Ex_User.UserNotFound:
            NewUser = {"Name": Name, "UserType": UserType}
            if len(self.Users) == 0: NewUser["Default"] = True
            else: NewUser["Default"] = False
            if UserType == "Offline": NewUser["Password"] = None
            elif Password != None: NewUser["Password"] = self.encodeBase64(Password)
            else: raise ValueError("Password is None")
            self.Users.append(NewUser)
            return(None)
        raise Ex_User.UserDuplicate(f"Duplicate user: {Name}")


    def remove(self, Name: str) -> None:
        """通过用户名删除用户"""
        self.Users.remove(self.Users[self.userID(Name)])
        # 若要删除的账户为默认账户, 则设置另一个账户为默认
        self.getDefault()


    def save(self) -> None:
        """保存用户数据"""
        ConfigContent = {"Users": self.Users, "VERSION": self.UserConfigs["VERSION"]}
        saveFile(Path=pathAdder("$CONFIG", ConfigIDs["Users"]), FileContent=ConfigContent, Type="json")


    def setDefault(self, Name: str) -> None:
        """设置默认用户"""
        Users = self.Users
        Users[self.getDefault()]["Default"] = False
        Users[self.userID(Name)]["Default"] = True
        self.Users = Users


    def getDefault(self) -> int:
        """返回默认用户的id, 若不存在默认用户则设置 0 号用户为默认账户"""
        for i in range(len(self.Users)):
            if self.Users[i]["Default"] == True:
                return(i)
        if len(self.Users) >= 1:
            self.Users[0]["Default"] = True
            return(0)


    def encodeBase64(self, Input: str) -> str:
        """返回Base64编码后的字符串"""
        return(str(b64encode(bytes(Input, encoding="utf8")), encoding="utf8"))


    def decodeBase64(self, Input: str) -> str:
        """返回Base64解码后的字符串"""
        return(str(b64decode(bytes(Input, encoding="utf8")), encoding="utf8"))


    def userID(self, Name: str) -> int:
        """通过用户名获取用户ID"""
        Output = None
        for i in range(len(self.Users)):
            if self.Users[i]["Name"] == Name:
                Output = i
                break
        if Output == None: raise Ex_User.UserNotFound(f"User \"{Name}\" Not found")
        return(Output)

