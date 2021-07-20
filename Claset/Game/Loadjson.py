#VERSION=1
#
#Claset\Game\Loadjson.py
#用于解析游戏Json
#

from Claset.Base.Loadfile import loadfile

    
def AssetsIndex(path) -> list:
    initfile = loadfile(path, "json")
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
            "OfficialURL": "$OfficialAssets/" + objects[i]["hash"][:2] + "/" + objects[i]["hash"]
        })
    
    return(output)


def Version():
    pass

