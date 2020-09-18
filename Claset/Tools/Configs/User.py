#
#Claset/Tools/Configs/User.py
#管理用户
#

from Claset.Tools.Loadjson import loadjson

class User():
    def __init__(self):
        self.users = loadjson("$EXEC/Configs/Users.json")


    #返回list形式的User列表
    def listt(self):
        users = []
        for i in range(len(self.users)):
            users.append(self.users[i])
        return(users)


    #创建用户,返回修改后的Config["User"]
    def create(self, usertype, name, password=None):
        seq = userid(self, name)
        if seq == "DontFindThisUser":
            pass
        else:
            if self.users[seq]["Name"] == name:
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
            password = str(base64.b64encode(bytes(password, encoding="utf8")), encoding="utf8")
            newuser["Password"] = password

        self.users pass newuser
    
    
    #删除用户,返回修改后的Config["User"]
    def remove(name):
        newconfig = self.users
        seqq = None
    
        for i in range(len(newconfig)):#获得要删除用户的id
            seq = newconfig[i]
            if seq["Name"] == name:
                seqq = i
                break
    
        if seqq == None:
            return("DontHaveThisUserInConfig")#若无此账户则返回
        else:
        #设置另一个default账户且删除要删除的账户
            if newconfig[seqq]["Default"] == True:
                newconfig.remove(newconfig[seqq])
                if len(newconfig) == 0:
                    pass
                else:
                    newconfig[0]["Default"] = True
            else:
                newconfig.remove(newconfig[seqq])
        
            self.users = newconfig


#设置默认用户,返回修改后的Config["User"]
    def setdefault(self, name):
        seq = userid(name)
        seqq = default()
        newusers = self.users
        newusers[seqq]["Default"] = False
        newusers[seq]["Default"] = True
        self.users = newusers


    #返回默认用户信息
    def default(self):
        for i in range(len(self.users)):
            if self.users[i]["Default"] == True:
                return(i)


    #返回解码base64后的密码
    def decode(self, name):
        import base64
        useridd = userid(name)
        password = self.users[useridd]["Password"]
        password = str(base64.b64decode(bytes(password, encoding="utf8")), encoding="utf8")
        return(password)
    #返回id
def userid(self, name):
    user = self.users
    seq = "DontFindThisUser"

    for i in range(len(user)):
        if user[i]["Name"] == name:
            seq = i
            break
    return(seq)



