#VERSION=1
#
#Claset\Game\Loadjson.py
#用于解析游戏Json
#

from Claset.Base.Loadfile import loadFile

    
def AssetsIndex(path) -> list:
    initfile = loadFile(path, "json")
    objects = initfile["objects"]
    output = list()

    for i in objects:
        output.append({
            "FileName": objects[i]["hash"],
            "URL": "$Assets/" + objects[i]["hash"][:2] + "/" + objects[i]["hash"],
            "Size": objects[i]["size"],
            "OutputPath": "$ASSETS/objects/" + objects[i]["hash"][:2], 
            "Overwrite": False,
            "Retry": 3,
            "OtherURL": "$OfficialAssets/" + objects[i]["hash"][:2] + "/" + objects[i]["hash"],
            "Sha1": objects[i]["hash"],
            "ConnectTimeout": 3,
            "ReadTimeout": 15
        })
    
    return(output)


def Version():
    pass

