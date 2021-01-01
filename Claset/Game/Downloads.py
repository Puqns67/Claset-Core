#VERSION=0
#
#Claset/Game/Download.py
#下载游戏
#


"""
def urlreplace(url, urltype, Config=None, DConfig=None):

    if Config == None:
        Config = CPML.Tools.getconfig("CPML")

    if DConfig == None:
        DConfig = CPML.Tools.getconfig("DConfig")

    DS = Config["Settings"]["DownloadServer"]
    MS = DConfig["MinecraftServers"]

    if urltype == "launchermeta":
        return(url.replace(MS["Vanilla"]["LauncherMeta"], MS[DS]["LauncherMeta"]))
    elif urltype == "launcher":
        return(url.replace(MS["Vanilla"]["Lancher"], MS[DS]["Lancher"]))
    elif urltype == "libraries":
        return(url.replace(MS["Vanilla"]["Libraries"], MS[DS]["Libraries"]))


def getfile(filetype):
    import os, os.path
    Config = CPML.Tools.getconfig("CPML")
    DConfig = CPML.Tools.getconfig("DConfig")
    CachePath = Config["RData"]["NowCwd"] + Config["Settings"]["DefaultPath"]["Cache"]
    if filetype == "MCVersionMetaList":
        url = DConfig["MinecraftServers"][Config["Settings"]["DownloadServer"]]["LauncherMeta"] + "/mc/game/version_manifest.json"
        path = CachePath + DConfig["DownloadCachePath"]["MCVersionManifest"] + "/"
        filename = "version_manifest.json"
    else:
        return("End")

    urldownload(url, path, filename)


def downloadgame(iverison, saveame):
    startime = time.time()
    import threading, os, os.path, re
    from queue import Queue

    Config = CPML.Tools.getconfig("CPML")
    DConfig = CPML.Tools.getconfig("DConfig")
    CachePath = Config["RData"]["NowCwd"] + Config["Settings"]["DefaultPath"]["Cache"]
    DownloadQ = Queue(maxsize=0)
    #更新version_manifest.json
    getfile("MCVersionMetaList")
    #解析相关的数据
    seq = CachePath + DConfig["DownloadCachePath"]["MCVersionManifest"] + "/version_manifest.json"
    seq = os.path.abspath(seq)
    MCVML = CPML.Tools.loadjson(seq)
    pversion = None

    for i in range(len(MCVML["versions"])):
        if MCVML["versions"][i]["id"] == iverison:
            pversion = MCVML["versions"][i]
            break

    if not Config["Settings"]["DownloadServer"] == "Vanilla":
        pversion["url"] = urlreplace(pversion["url"], "launchermeta", Config, DConfig)

    seq = CachePath + DConfig["DownloadCachePath"]["MCVersion"]

    #thread1 = threading.Thread(target=urldownload, args=(pversion["url"], seq, ))
    name = iverison + ".json"
    seqq = seq + "/" + name

    if CPML.Tools.dfcheck("file", seqq) == False:
        urldownload(pversion["url"], seq, name)

    List = CPML.Tools.loadjson(seqq, "MCV")

    for i in range(len(List)):
        if List[i]["Type"] == "libraries":
            seq = {}
            seqq = re.match(r"(.*)/(,*)", List[i]["Path"]).span()
            seqq = List[i]["Path"][seqq[1]:]
            seq["Name"] = seqq
            seq["Url"] =  DConfig["MinecraftServers"][Config["Settings"]["DownloadServer"]]["Libraries"] + "/" + List[i]["Path"]
            seq["Size"] = List[i]["Size"]
            seqq = "/" + seqq
            seqq = List[i]["Path"].replace(seqq, "")
            seq["Path"] = os.getcwd() + Config["Settings"]["DefaultPath"]["Libraries"] + "/" + seqq
            DownloadQ.put(seq)
        elif List[i]["Type"] == "assetIndex":
            seq = urlreplace(List[i]["Url"], "launchermeta", Config, DConfig)
            seqq = CachePath + DConfig["DownloadCachePath"]["MCAssetIndex"]
            seqqq = List[i]["Size"]
            assetIndex = threading.Thread(target=urldownload, args=(seq, seqq), kwargs={"size":seqqq})
            assetIndex.start()
        elif List[i]["Type"] == "client":
            pass

    assetIndex.join()

    print(DownloadQ.queue)
    print("UsedTime:", time.time() - startime)


"""