#VERSION=10
#
#Claset/Base/Download.py
#通过url下载数据
#

import requests, threading, re

from queue import Queue
from time import time, sleep
from io import BytesIO
from random import randint

from Claset.Base.Savefile import savefile
from Claset.Base.Path import path as pathmd
from Claset.Base.Loadfile import loadfile
from Claset.Base.DFCheck import dfcheck
from Claset.Base.AdvancedPath import path as apathmd


class downloadmanager():
    def __init__(self, DoType=None):
        self.Configs = loadfile("$EXEC/Configs/Download.json", "json")
        self.ReCompile = re.compile(self.Configs["ReadFileNameReString"])
        self.JobQueue = Queue(maxsize=0)
        self.DownloadStatus = False
        self.DownloadServiceStatus = False
        self.Threads = []
        self.ThreadINFOs = []
        self.Projects = {"0": {"CompletedProject": 0, "AllProject": 0}}
        self.AdvancedPath = apathmd(Others=True)
        self.DownloadService = ""

        for i in range(self.Configs["MaxThread"]):
            self.ThreadINFOs.append({"ID": i})

        if DoType == "Start":
            self.StartService()

    def reload(self, DoType=None):
        self.StopService(True)
        del(self.DownloadService)
        del(self.DownloadServiceStatus)
        del(self.DownloadStatus)
        del(self.AdvancedPath)
        self.__init__(DoType)


    #简易下载器
    def download(
        self, ThreadID, URL=None, OutputPath="$PREFIX",
        FileName=None, Size=None, ProjectID=None, Retry=0,
        Overwrite=True, Timeout=None
        ):
        #ThreadID: 线程id
        #URL: 链接地址
        #OutputPath: 输出位置
        #FileName: 文件名
        #Size: 文件大小(字节)
        #ProjectID: 任务id
        #Retry: 重试次数
        #Overwrite: 覆盖已有的文件
        #Timeout: 传输超时

        if URL == None: raise KeyError("not have URL")
        if "$" in URL: URL = self.AdvancedPath.path(URL)
        if Timeout == None: Timeout = self.Configs["Timeout"]
        if Retry < 0: self.add(self.ThreadINFOs[ThreadID]["Jobbase"], ProjectID=0)
        self.ThreadINFOs[ThreadID]["Jobbase"]["Retry"] -= 1

        OutputPath = pathmd(OutputPath)

        if FileName == None: FileName = self.ReCompile.search(URL).group(1)

        OutputPaths = OutputPath + "\\" + FileName

        if Overwrite == False:
            if dfcheck("f", OutputPaths) == True:
                if ProjectID != None:
                    self.Project_addJob(ProjectID, CompleledProject=1)
                return("FileExist")

        RSession = requests.Session()
        RSession.headers = self.Configs['Headers']
        File = BytesIO()
        try:
            Request = RSession.get(URL, timeout=Timeout)
            StatusCode = str(Request.status_code)
            if StatusCode[0] in ["4", "5"]: Request.raise_for_status()
            File.write(Request.content)
        except (
            requests.exceptions.ProxyError,
            requests.exceptions.HTTPError,
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout
        ):
            self.add(self.ThreadINFOs[ThreadID]["Jobbase"], ProjectID=ProjectID)

        if Size != None:
            if len(File.getbuffer()) != Size:
                self.add(self.ThreadINFOs[ThreadID]["Jobbase"], ProjectID=ProjectID)

        dfcheck("dm", OutputPath)
        savefile(OutputPaths, File.getbuffer(), filetype="bytes")

        if ProjectID != None: self.Project_addJob(ProjectID, CompleledProject=1)


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

                if self.DownloadStatus == False: self.DownloadStatus = True

                self.ServiceStartTime = int(time())

            self.Service_StartAllNotActivatedThread()

            if self.Service_CheckAllThreadStopped(): self.ServiceStartTime = int(time())

            if self.DownloadServiceStatus == False:
                if self.Service_CheckAllThreadStopped() == False: break

            if (self.ServiceStartTime + self.Configs["ServiceAutoStop"]) <= int(time()): break

            sleep(self.Configs["ServiceSleepTime"])

    def Service_ReturnFirstIdleThreadId(self) -> int:
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
                try: self.Threads[i].start()
                except RuntimeError: pass

    def Service_CheckAllThreadStopped(self) -> bool:
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
    def add(self, InputJob, autoStartService=True, ProjectID=None):
        if ProjectID != None:
            pass

        if type(InputJob) == type(list()):
            if ProjectID == None:
                ProjectID = self.Project_create(len(InputJob))
            else:
                self.Project_addJob(ProjectID, len(InputJob))

            for i in range(len(InputJob)):
                Job = InputJob[i]
                Job["ProjectID"] = ProjectID
                self.JobQueue.put(Job)
            return(ProjectID)

        elif type(InputJob) == type(dict()):
            if ProjectID == None:
                ProjectID = self.Project_create(1)
            else:
                self.Project_addJob(ProjectID, AllProject=1)
            InputJob["ProjectID"] = ProjectID
            self.JobQueue.put(InputJob)
            return(ProjectID)

        if autoStartService:
            self.StartService()


    #启动服务
    def StartService(self):
        if self.DownloadServiceStatus == False:
            try:
                if self.DownloadService:
                    if self.DownloadService.is_alive():
                        self.DownloadStatus = True
                        return(0)
            except AttributeError:
                pass

            self.DownloadServiceStatus = True
            self.DownloadService = threading.Thread(target=self.downloadservice, name="DownloadManager", daemon=True)
            self.DownloadService.start()


    #停止服务
    def StopService(self, join=False):
        if self.DownloadServiceStatus:
            self.DownloadServiceStatus = False
            if join:
                while True:
                    if self.DownloadService.is_alive() == False:
                        break
                    sleep(self.Configs["ServiceSleepTime"])


    #建立Project
    def Project_create(self, AllProject=0) -> int:
        while True:
            seqq = ""
            intt = randint(1,999999999)
            for i in self.Projects.keys():
                if intt == i:
                    seqq += "-"
            if "-" in seqq:
                continue
            self.Projects[intt] = {"CompletedProject": 0, "AllProject": AllProject}
            return(intt)


    def Project_addJob(self, ProjectID, AllProject=None, CompleledProject=None):
        if AllProject != None:
            self.Projects[ProjectID]["AllProject"] += AllProject

        if CompleledProject != None:
            self.Projects[ProjectID]["CompletedProject"] += CompleledProject


    #通过ProjectID阻塞线程
    def Project_join(self, ProjectID):
        while True:
            if self.Projects[ProjectID]["CompletedProject"] == self.Projects[ProjectID]["AllProject"]:
                break
            sleep(self.Configs["ServiceSleepTime"])

