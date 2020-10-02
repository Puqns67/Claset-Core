#VERSION=1
#
#Claoset\Tools\Loadjson.py
#用于解析Json
#

import json

from Claset.Base.Path import path

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
