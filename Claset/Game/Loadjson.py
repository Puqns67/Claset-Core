#VERSION=3
#
#Claset/Game/Loadjson.py
#用于解析游戏Json
#

from Claset.Base.File import loadFile


def AssetsIndex(Path: str) -> list:
    InitFile = loadFile(Path, "json")
    Objects = InitFile["objects"]
    Tasks = list()

    for i in Objects:
        Tasks.append({
            "FileName": Objects[i]["hash"],
            "URL": "$Assets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"],
            "Size": Objects[i]["size"],
            "OutputPath": "$ASSETS/objects/" + Objects[i]["hash"][:2], 
            "Overwrite": False,
            "Retry": 3,
            "OtherURL": "$OfficialAssets/" + Objects[i]["hash"][:2] + "/" + Objects[i]["hash"],
            "Sha1": Objects[i]["hash"],
            "ConnectTimeout": 3,
            "ReadTimeout": 15
        })
    
    return(Tasks)


def Version():
    pass

