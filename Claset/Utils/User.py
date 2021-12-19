#VERSION=3
#
#Claset/Base/User.py
#管理用户
#

from base64 import b64encode, b64decode

from .File import loadFile, saveFile

class user():
    def __init__(self):
        self.users = loadFile("$CONFIG/Users.json", "json")


    # 返回list形式的User列表
    def listt(self) -> list:
        users = []
        for i in range(len(self.users)):
            users.append(self.users[i])
        return(users)


    # 创建用户
    def create(self, usertype, name, password=None):

        if not self.userid(name) == "DontFindThisUser":
            if self.users[self.userid(name)]["Name"] == name:
                return("UserNameRepeat")

        newuser = {}
        newuser["UserType"] = usertype
        newuser["Name"] = name

        if len(self.users) == 0:
            newuser["Default"] = True
        else:
            newuser["Default"] = False

        if usertype == "Offline":
            newuser["Password"] = None
        else:
            import base64
            password = str(b64encode(bytes(password, encoding="utf8")), encoding="utf8")
            newuser["Password"] = password

        self.users.append(newuser)


    #删除用户
    def remove(self, name):
        newconfig = self.users

        if self.userid(name) == "DontFindThisUser":
            return("DontHaveThisUserInConfig")#若无此账户则返回

        #设置另一个default账户且删除要删除的账户
        if newconfig[self.userid(name)]["Default"] == True:
            newconfig.remove(newconfig[self.userid(name)])
            if not len(newconfig) == 0:
                newconfig[0]["Default"] = True
        else:
            newconfig.remove(newconfig[self.userid(name)])

        self.users = newconfig


    #设置默认用户
    def setdefault(self, name):
        newusers = self.users
        newusers[self.default()]["Default"] = False
        newusers[self.userid(name)]["Default"] = True
        self.users = newusers


    #返回默认用户的id
    def default(self):
        for i in range(len(self.users)):
            if self.users[i]["Default"] == True:
                return(i)


    #返回解码base64后的密码
    def decode(self, name):
        password = self.users[self.userid(name)]["Password"]
        password = str(b64decode(bytes(password, encoding="utf8")), encoding="utf8")
        return(password)


    #返回id
    def userid(self, name):
        output = "DontFindThisUser"
        for i in range(len(self.users)):
            if self.users[i]["Name"] == name:
                output = i
                break
        return(output)


    #保存到文件
    def save(self):
        saveFile(self.path, self.users)


    #重新从文件加载数据
    def reload(self):
        self.users = loadFile(self.path, "json")

