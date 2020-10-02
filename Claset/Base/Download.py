#VERSION=0
#
#Claset/Base/Download.py
#通过url下载数据
#

import re, urllib.request, threading

from queue import Queue
from time import time, sleep

from Claset.Base.Savefile import save
from Claset.Base.Path import path as pathmd
from Claset.Base.Loadjson import loadjson
from Claset.Base.DFCheck import dfcheck

class downloadmanager():
    def __init__(self):
        self.configs = loadjson("$EXEC/Configs/Download.json")
        self.jobqueue = Queue(maxsize=0)

    #简易下载器
    def download(self, fullurl=None, outputpath="$PREFIX", filename=None, size=None, jobbase=None):
        if fullurl == None:
            raise KeyError("DontHaveURL")
        if jobbase == None:
            print(__name__, "DontHave\'jobbase\'")

        outputpath = pathmd(outputpath)

        if filename == None:
            seq = re.match(r"(.*)/(,*)", fullurl).span()
            filename = fullurl[seq[1]:]
        outputpaths = outputpath + "/" + filename

        dfcheck("dm", outputpath)

        #openurl
        url = urllib.request.Request(fullurl, headers=self.configs["Headers"])

        try:
            website = urllib.request.urlopen(url)
        except urllib.error.HTTPError as info:
            self.add(jobbase)
            return(info)
        except http.client.RemoteDisconnected as info:
            self.add(jobbase)
            return(info)
        
        WebSiteInfo = {}
        WebSiteInfo["httpcode"] = website.getcode()
        WebSiteInfo["EndURL"] = website.geturl()

        ReadedWebsite = website.read()

        try:
            OpenedURL = str(ReadedWebsite, encoding="utf8")
        except UnicodeDecodeError:
            OpenedURL = ReadedWebsite
            save(outputpaths, OpenedURL, "bytes")
        else:
            save(outputpaths, OpenedURL, "txt")

        if size != None:
            if dfcheck("fs", outputpaths, size=size) != True:
                self.add(jobbase)


    #下载服务
    def downloadservice(self):
        self.Threads = []
        while True:
            while len(self.jobqueue.queue) != 0:
                job = self.jobqueue.get()
                ThreadID = self.Service_ReturnFirstIdleThreadId()
                if ThreadID == "AppendNewThread":
                    ThreadID = str(len(self.Threads))
                    athread = threading.Thread(target=self.download, kwargs=job, name=f"DownloadThread{ThreadID}", daemon=True)
                    self.Threads.append(athread)
                else:
                    ThreadID = str(ThreadID)
                    athread = threading.Thread(target=self.download, kwargs=job, name=f"DownloadThread{ThreadID}", daemon=True)
                    self.Threads[int(ThreadID)] = athread

                self.Service_StartAllNotActivatedThread()

            self.Service_StartAllNotActivatedThread()

            sleep(self.configs["ServiceSleepTime"])

    def Service_ReturnFirstIdleThreadId(self):
        if len(self.Threads) < self.configs["MaxThread"]:
            return("AppendNewThread")
        while True:
            for i in range(len(self.Threads)):
                if type(self.Threads[i]) == threading.Thread:
                    if self.Threads[i].is_alive() == False:
                        return(i)
            sleep(self.configs["ServiceSleepTime"])

    def Service_StartAllNotActivatedThread(self):
        for i in range(len(self.Threads)):
            if self.Threads[i].is_alive() == False:
                try:
                    self.Threads[i].start()
                except RuntimeError as info:
                    pass


    #向jobqueue放入任务
    def add(self, inputjob):
        if type(inputjob) == type(list()):
            for i in range(len(inputjob)):
                job = inputjob[i]
                jobbase = dict(job)
                job["jobbase"] = job
                self.jobqueue.put(job)
        elif type(inputjob) == type(dict()):
            jobbase = dict(inputjob)
            inputjob["jobbase"] = jobbase
            self.jobqueue.put(inputjob)

    
    #启动服务
    def startservice(self):
        self.DownloadService = threading.Thread(target=self.downloadservice, name="DownloadManager", daemon=True)
        self.DownloadService.start()


