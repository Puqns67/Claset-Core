#VERSION=3
#
#Claset/Base/Download.py
#通过url下载数据
#

import urllib.request, threading

from queue import Queue
from time import time, sleep
from io import BytesIO
from re import match

from Claset.Base.Savefile import save
from Claset.Base.Path import path as pathmd
from Claset.Base.Loadjson import loadjson
from Claset.Base.DFCheck import dfcheck

class downloadmanager():
    def __init__(self, DoType=None):
        self.Configs = loadjson("$EXEC/Configs/Download.json")
        self.jobqueue = Queue(maxsize=0)
        self.DownloadStatus = False
        self.DownloadServiceStatus = False
        self.Threads = []
        self.ThreadINFOs = []

        for i in range(self.Configs["MaxThread"]):
            self.ThreadINFOs.append({"ID": i})

        if DoType != None:
            if DoType == "Start":
                self.StartService()


    #简易下载器
    def download(self, ThreadID, URL=None, OutputPath="$PREFIX", FileName=None, Size=None, Job=None):
        if URL == None:
            raise KeyError("DontHaveURL")
        if Job == None:
            print("DontHave\'Job\'")

        OutputPath = pathmd(OutputPath)

        if FileName == None:
            FileName = URL[match(r"(.*)/(,*)", URL).span()[1]:]

        OutputPaths = OutputPath + "/" + FileName
        dfcheck("dm", OutputPath)

        url = urllib.request.Request(URL, headers=self.Configs["Headers"])
        
        try:
            with urllib.request.urlopen(url) as Response:
                File = BytesIO()
                NowSize = 0
                Length = Response.getheader('content-length')

                if Length:
                    BlockSize = int(Length) // 50
                else:
                    BlockSize = 9999999

                while True:
                    OneWhile = Response.read(BlockSize)
                    if not OneWhile:
                        break
                    File.write(OneWhile)
                    NowSize += len(OneWhile)
                    if Length:
                        self.ThreadINFOs[ThreadID]["Percent"] = int((NowSize / int(Length)) * 100)
                if Size != None:
                    if NowSize != Size:
                        self.add(Job)
                        raise ValueError("SizeError")

                save(OutputPath, File.getbuffer())

        except urllib.error.HTTPError as info:
            self.add(Job)
            return(info)


    #下载服务
    def downloadservice(self):
        self.ServiceStartTime = int(time())
        while True:
            while len(self.jobqueue.queue) != 0:
                job = self.jobqueue.get()
                ThreadID = self.Service_ReturnFirstIdleThreadId()

                if ThreadID == "AppendNewThread":
                    ThreadID = len(self.Threads)
                    job["ThreadID"] = ThreadID
                    ThreadID = str(ThreadID)
                    athread = threading.Thread(target=self.download, kwargs=job, name=f"DownloadThread{ThreadID}", daemon=True)
                    self.Threads.append(athread)
                    self.Threads[-1].start()
                else:
                    job["ThreadID"] = ThreadID
                    ThreadID = str(ThreadID)
                    athread = threading.Thread(target=self.download, kwargs=job, name=f"DownloadThread{ThreadID}", daemon=True)
                    self.Threads[int(ThreadID)] = athread
                    self.Threads[int(ThreadID)].start()

                if self.DownloadStatus == False:
                    self.DownloadStatus = True

                self.ServiceStartTime = int(time())

            self.Service_StartAllNotActivatedThread()

            if self.Service_CheckAllThreadStopped():
                self.ServiceStartTime = int(time())

            if self.DownloadServiceStatus == False:
                if self.Service_CheckAllThreadStopped() == False:
                    break

            if (self.ServiceStartTime + self.Configs["ServiceAutoStop"]) <= int(time()):
                break

            sleep(self.Configs["ServiceSleepTime"])

    def Service_ReturnFirstIdleThreadId(self):
        if len(self.Threads) < self.Configs["MaxThread"]:
            return("AppendNewThread")
        while True:
            for i in range(len(self.Threads)):
                if type(self.Threads[i]) == threading.Thread:
                    if self.Threads[i].is_alive() == False:
                        return(i)
            sleep(self.Configs["ServiceSleepTime"])

    def Service_StartAllNotActivatedThread(self):
        for i in range(len(self.Threads)):
            if self.Threads[i].is_alive() == False:
                try:
                    self.Threads[i].start()
                except RuntimeError as info:
                    pass

    def Service_CheckAllThreadStopped(self):
        seq = ""

        for i in range(len(self.Threads)):
            if self.Threads[i].is_alive():
                seq += "+"
            elif self.Threads[i].is_alive() == False:
                seq += "-"

        if "+" in seq:
            self.DownloadStatus = True
            return(True)
        else:
            if self.DownloadStatus == True:
                self.DownloadStatus = False
            return(False)


    #向jobqueue放入任务
    def add(self, inputjob):
        if type(inputjob) == type(list()):
            for i in range(len(inputjob)):
                job = inputjob[i]
                jobbase = dict(job)
                job["Job"] = jobbase
                self.jobqueue.put(job)
        elif type(inputjob) == type(dict()):
            jobbase = dict(inputjob)
            inputjob["Job"] = jobbase
            self.jobqueue.put(inputjob)

    
    #启动服务
    def StartService(self):
        if self.DownloadServiceStatus == False:
            self.DownloadServiceStatus = True
            self.DownloadService = threading.Thread(target=self.downloadservice, name="DownloadManager", daemon=True)
            self.DownloadService.start()
    

    def StopService(self):
        self.DownloadServiceStatus = False


