#
#Claset\Tools\Tools.py
#工具包
#

def getver():
    return(0)


def getconfig(ctype):
    if ctype == "CPML":
        import os
        seq = os.getcwd() + "/CPML.json"
        seq = loadjson(seq)
        seq["RData"] = {}
        seq["RData"]["NowCwd"] = os.getcwd()
        return(seq)
    elif ctype == "DConfig":
        Config = getconfig("CPML")
        seq = Config["RData"]["NowCwd"] + Config["Settings"]["DefaultPath"]["Execs"] + "/DownloadsConfig.json"
        seq = loadjson(seq)
        seq["RData"] = Config["RData"]
        return(seq)


def getplatform(gettype):
    import platform
    if gettype == "System":
        return(platform.system())
    elif gettype == "system":
        os = platform.system()
        if os == "Linux":
            os = "linux"
        elif os == "Windows":
            os = "windows"
        return(os)
    elif gettype == "Machine":
        return(platform.machine())
    elif gettype == "machine":
        seq = platform.machine()
        types = {'AMD64':64, 'x86_64': 64, 'i386': 32, 'x86': 32, "aarch64": 64, "aarch32": 32, "arm64": 64, "arm32": 32}
        return(types[seq])


def dfcheck(checktype, path, MCver=None, size=None):
    import os, os.path
    if checktype == "objects_dir":
        spath = path + "/assets/objects/"
        for ii in range(256):
            seq = hex(ii)[2:]
            if len(seq) == 1:
                seq = "0" + seq
            seqq = spath + seq + "/"
            dfcheck("dir", seqq)
    elif checktype == "objects":
        pass
    elif checktype == "libraries":
        pass
    elif checktype == "dir":
        seq = os.path.exists(path)
        if seq == False:
            os.makedirs(path)
    elif checktype == "filesize":
        tsize = os.path.getsize(path)
        if not size == tsize:
            return(False)
        return(True)
    elif checktype == "file":
        return(os.path.exists(path))

def urldownload(fullurl, outputpath="./", filename=None, size=None, headers=None, DConfig=None):
    import time
    starttime = time.time()
    import urllib.request
    import re, os, os.path

    if DConfig == None:
        DConfig = getconfig("DConfig")

    dfcheck("dir", outputpath)
    #openurl

    if headers == None:
        url = urllib.request.Request(fullurl, headers=DConfig["Headers"])
    else:
        url = urllib.request.Request(fullurl, headers=headers)

    try:
        seq = urllib.request.urlopen(url)
    except urllib.error.HTTPError as seq:
        return(seq)
    except http.client.RemoteDisconnected as seq:
        return(seq)

    httpcode = seq.getcode()
    endurl = seq.geturl()
    seq = seq.read()

    try:
        openedurl = str(seq, encoding="utf8")
        ifopen = False
    except UnicodeDecodeError:
        openedurl = seq
        ifopen = True
    
    if filename == None:
        seq = re.match(r"(.*)/(,*)", fullurl).span()
        filename = fullurl[seq[1]:]

    outputpath = os.path.abspath(outputpath)
    output = outputpath + "/" + filename

    if ifopen == False:
        with open(output, mode="w+") as w:
            w.write(openedurl)
    else:
        with open(output, mode="wb") as w:
            w.write(openedurl)

    if not size == None:
        seq = dfcheck("filesize", output, size=size)
        if seq == False:
            return("SizeError")

    print("[UrlDownload][FileInfo]", output, size)
    print("[UsedTime]", time.time() - starttime)


def jsondump(jsonpath):
    import json, os.path

    jsonpath = os.path.abspath(jsonpath)
    loadedjson = loadjson(jsonpath)
    write = json.dumps(loadedjson, indent=4, ensure_ascii=False)

    with open(jsonpath, mode="w+") as w:
        w.write(write)

