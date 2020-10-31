#VERSION=5
#
#Claset/Base/Download.py
#通过url下载数据
#

import urllib.request, threading, re

from queue import Queue
from time import time, sleep
from io import BytesIO
from random import randint

from Claset.Base.Savefile import save
from Claset.Base.Path import path as pathmd
from Claset.Base.Loadjson import loadjson
from Claset.Base.DFCheck import dfcheck

class downloadmanager():
    def __init__(self, DoType=None):
        self.Configs = loadjson("$EXEC/Configs/Download.json")
        self.ReCompile = re.compile("[a-zA-Z0-9_.-]+$")
        self.JobQueue = Queue(maxsize=0)
        self.DownloadStatus = False
        self.DownloadServiceStatus = False
        self.Threads = []
        self.ThreadINFOs = []
        self.Projects = {}

        for i in range(self.Configs["MaxThread"]):
            self.ThreadINFOs.append({"ID": i})

        if DoType == "Start":
            self.StartService()


    #简易下载器
    def download(self, ThreadID, URL=None, OutputPath="$PREFIX", FileName=None, Size=None, ProjectID=None):
        if URL == None:
            raise KeyError("DontHaveURL")

        OutputPath = pathmd(OutputPath)

        if FileName == None:
            Seqq, Seqw = self.ReCompile.search(URL).span()
            FileName = URL[Seqq:Seqw]

        OutputPaths = OutputPath + "/" + FileName
        dfcheck("dm", OutputPath)

        Request = urllib.request.Request(URL, headers=self.Configs["Headers"])
        
        try:
            with urllib.request.urlopen(Request) as Response:
                File = BytesIO()
                NowSize = 0
                Length = int(Response.getheader('content-length'))

                if Length:
                    BlockSize = int(Length / 50)
                else:
                    BlockSize = Length

                while True:
                    OneWhile = Response.read(BlockSize)
                    if not OneWhile:
                        break
                    File.write(OneWhile)
                    NowSize += len(OneWhile)
                    if Length:
                        self.ThreadINFOs[ThreadID]["Percent"] = int((NowSize / Length) * 100)

                if Size != None:
                    if NowSize != Size:
                        self.add(Job)
                        raise ValueError("SizeError")

                save(OutputPaths, File.getbuffer(), filetype="bytes")
                if ProjectID != None:
                    self.Project_addCompletes(ProjectID)

        except urllib.error.HTTPError as info:
            self.add(Job)
            return(info)


    #下载服务
    def downloadservice(self):
        self.ServiceStartTime = int(time())
        while True:
            while len(self.JobQueue.queue) != 0:
                Job = self.JobQueue.get()
                ThreadID = self.Service_ReturnFirstIdleThreadId()

                if ThreadID == "AppendNewThread":
                    ThreadID = len(self.Threads)

                    self.ThreadINFOs[ThreadID]["Jobbase"] = Job
                    Job["ThreadID"] = ThreadID
                    ThreadID = str(ThreadID)
                    athread = threading.Thread(target=self.download, kwargs=Job, name=f"DownloadThread{ThreadID}", daemon=True)
                    self.Threads.append(athread)
                    self.Threads[-1].start()
                else:
                    self.ThreadINFOs[ThreadID]["Jobbase"] = Job
                    Job["ThreadID"] = ThreadID
                    ThreadID = str(ThreadID)
                    athread = threading.Thread(target=self.download, kwargs=Job, name=f"DownloadThread{ThreadID}", daemon=True)
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
    def add(self, InputJob):
        if type(InputJob) == type(list()):
            ProjectID = self.Project_create(len(InputJob))
            for i in range(len(InputJob)):
                Job = InputJob[i]
                Job["ProjectID"] = ProjectID
                self.JobQueue.put(Job)
            return(ProjectID)
        elif type(InputJob) == type(dict()):
            ProjectID = self.Project_create(1)
            InputJob["ProjectID"] = ProjectID
            self.JobQueue.put(InputJob)
            return(ProjectID)

    
    #启动服务
    def StartService(self):
        if self.DownloadServiceStatus == False:
            self.DownloadServiceStatus = True
            self.DownloadService = threading.Thread(target=self.downloadservice, name="DownloadManager", daemon=True)
            self.DownloadService.start()
    

    #停止服务
    def StopService(self):
        self.DownloadServiceStatus = False

    
    #建立Project
    def Project_create(self, AllProject=0):
        while True:
            seqq = ""
            intt = randint(0,999999999)
            for i in self.Projects.keys():
                if intt == i:
                    seqq += "-"
            if "-" in seqq:
                continue
            self.Projects[intt] = {"CompletedProject": 0, "AllProject": AllProject}
            return(intt)

            
    def Project_addCompletes(self, ProjectID, CompleledProject=1):
        self.Projects[ProjectID]["CompletedProject"] += CompleledProject


    #通过ProjectID阻塞线程
    def Project_join(self, ProjectID):
        while True:
            if self.Projects[ProjectID]["CompletedProject"] == self.Projects[ProjectID]["AllProject"]:
                break
            sleep(self.Configs["ServiceSleepTime"])

