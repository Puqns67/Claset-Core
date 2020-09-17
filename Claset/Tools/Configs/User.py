#
#Claset/Tools/Configs/User.py
#管理用户
#
from Claset.Tools.Loadjson import Loadjson

class User():
    def __init__(self):
        loadjson("./Claset/Configs/Users.json")


#返回list形式的User列表
def listt(Config):
    users = []
    for i in range(len(Config["User"])):
       users.append(Config["User"][i])
    return(users)


#创建用户,返回修改后的Config["User"]
def create(usertype, name, Config, password=None):
    
    seq = userid(name, Config)
    if seq == "DontFindThisUser":
        pass
    else:
        if Config["User"][seq]["Name"] == name:
            return("UserNameRepeat")
    
    newuser = {}
    newuser["UserType"] = usertype
    newuser["Name"] = name

    if len(Config["User"]) == 0:
        newuser["Default"] = True
    else:
        newuser["Default"] = False
    
    if usertype == "Offline":
        newuser["Password"] = None
    else:
        import base64
        password = str(base64.b64encode(bytes(password, encoding="utf8")), encoding="utf8")
        newuser["Password"] = password

    newuserconfig = Config["User"]
    newuserconfig.append(newuser)
    return(newuserconfig)


#删除用户,返回修改后的Config["User"]
def remove(name, Config):
    newconfig = Config["User"]
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
        
        return(newconfig)


#保存数据
def save(Config):
    import json

    try:
        del(Config["RData"])
    except KeyError as seq:
        if not seq == "RData":
            return("[Save]Delete 'RData' error!")
    
    write = json.dumps(Config, indent=4, ensure_ascii=False)

    with open("CPML.json", mode="w+") as w:
        w.write(write)

    return("Done")


#设置默认用户,返回修改后的Config["User"]
def setdefault(name, Config):
    seq = userid(name, Config)
    seqq = default(Config)
    newuser = Config["User"]
    newuser[seqq]["Default"] = False
    newuser[seq]["Default"] = True
    return(newuser)


#返回默认用户信息
def default(Config):

    for i in range(len(Config["User"])):
        if Config["User"][i]["Default"] == True:
            return(i)


#返回id
def userid(name, Config):
    user = Config["User"]
    seq = "DontFindThisUser"

    for i in range(len(user)):
        if user[i]["Name"] == name:
            seq = i
            break

    return(seq)
        


#返回解码base64后的密码
def decode(name, Config):
    import base64
    from CPML.User import userid
    useridd = userid(name, Config)
    password = Config["User"][useridd]["Password"]
    password = str(base64.b64decode(bytes(password, encoding="utf8")), encoding="utf8")
    return(password)

