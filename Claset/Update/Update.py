#
#CPML/Update.py
#更新系统
#

def getver():
    return(0)

def check():
    from CPML.Tools import jsonload
    Config = jsonload("CPML.json")

    if Config["Settings"]["CheckUpdate"] == False:
        return("CheckUpdateStop")

    import urllib.request
    import os
    import json

    SetupCwd = os.getcwd()
    seq = SetupCwd + "/CPML/DownloadsConfig.json"
    DConfigs = jsonload(seq)
    DConfig = DConfigs["CPMLUpdate"]
    seq = DConfig["Server"] + DConfig["UpdateVersionJson"]
    #到时候把这个下载写到Tools里去
    seq = urllib.request.urlopen("seq")
    #读出来，bytes转str，再jsonload
    json.loads(str(seq.read(), encoding="utf8"))
    getvers(DConfigs)
    return("aaqqq")


def getvers(DConfigs):
    import CPML.Downloads
    import CPML.Launcher
    import CPML.Tools
    import CPML.User

    NowVerison = {"Files": {}}

    NowVerison["Files"]["Update.py"] = getver()
    NowVerison["Files"]["Launcher.py"] = CPML.Launcher.getver()
    NowVerison["Files"]["Tools.py"] = CPML.Tools.getver()
    NowVerison["Files"]["User.py"] = CPML.User.getver()
    NowVerison["Files"]["DownloadsConfig.json"] = DConfigs["FileVer"]
    
    
