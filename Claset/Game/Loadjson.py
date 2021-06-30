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
            "Retry": 3
        })
    
    return(output)


def Version():
    pass

"""
def loadjson(jsonpath, filetype=None):
    if "$" in jsonpath:
        jsonpath = path(jsonpath)
    if filetype == None:
        with open(jsonpath) as openedjson:
            return(json.load(openedjson))
    elif filetype == "MCV":     #整理出libraries和一些其他链接和信息
        jsondict = loadjson(jsonpath)
        libraries = jsondict["libraries"]
        output = []
        os = getplatform("system")

        seqq = {}
        seq = jsondict["assetIndex"]
        seqq["ID"] = seq["id"]
        seqq["Size"] = seq["size"]
        seqq["Url"] = seq["url"]
        seqq["Type"] = "assetIndex"
        output.append(seqq)

        seqq = {}
        seq = jsondict["downloads"]["client"]
        seqq["Size"] = seq["size"]
        seqq["Url"] = seq["url"]
        seqq["Type"] = "client"
        output.append(seqq)

        for seqq in range(len(libraries)):
            seq = "rules" in libraries[seqq]
            if seq == True:#含rules项
                seqw = len(libraries[seqq]["rules"])
                while seqw > 0:
                    seq = "action"
                    if seq == True:
                        pass
        print(output)
    elif filetype == "MCAI":#转换AssetsIndex为list[dict]格式
        seq = loadjson(jsonpath)
        MCAI = seq["objects"]
        MCAIL = list(MCAI)
        output = []
        for i in range(len(MCAIL)):
            pass
"""