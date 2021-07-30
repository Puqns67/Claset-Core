#VERSION=FINALLY_17
#
#Claset/Base/old_Download.py
#通过url下载数据
#已弃用, 存档用
#

import re
import threading
from io import BytesIO
from queue import Queue
from random import randint
from time import sleep, time

import requests

from . import AdvancedPath, DFCheck, Loadfile, Path, Savefile


class downloadmanager():
    def __init__(self, DoType=None, Logger=None):
        self.Configs = Loadfile.loadfile("$EXEC/Configs/Download.json", "json")
        self.ReCompile = re.compile(self.Configs["ReadFileNameReString"])
        self.JobQueue = Queue(maxsize=0)
        self.DownloadStatus = False
        self.DownloadServiceStatus = False
        self.Threads = []
        self.ThreadINFOs = []
        self.Projects = {0: {"CompletedTasksCount": 0, "AllTasksCount": 0, "FailuredTasksCount": 0, "Tasks": []}}
        self.AdvancedPath = AdvancedPath.path(Others=True, OtherTypes=[["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<1>", "&F<$EXEC/Configs/Settings.json>&V<DownloadServer>"], ["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<Official>"]])
        self.DownloadService = ""

        #全局Session
        self.RequestsSession = requests.Session()
        self.RequestsSession.headers = self.Configs['Headers']
        
        #创建空ThreadINFOs
        for i in range(self.Configs["MaxThread"]):
            self.ThreadINFOs.append({"ID": i})

        #定义全局Logger
        if Logger != None:
            self.Logger = Logger
            self.LogHeader = ["Downloader"]
        
        if DoType == "Start":
            self.StartService()


    def Reload(self, DoType=None):
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
        Overwrite=True, Timeout=None, OfficialURL=None, Session=None
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
        #OfficialURL：官方URL(不适用)
        #Session: 全局Session

        if Timeout == None: Timeout = self.Configs["Timeout"]

        if self.Logger != None:
            ThreadIDStr = str(ThreadID)
            if self.Configs["MaxThread"] >= 100:
                if len(ThreadIDStr) == 1: ThreadIDStr = "00" + ThreadIDStr
                elif len(ThreadIDStr) == 2: ThreadIDStr = "0" + ThreadIDStr
            elif self.Configs["MaxThread"] >= 10:
                if len(ThreadIDStr) == 1: ThreadIDStr = "0" + ThreadIDStr

        if Retry < 0:
            if self.Logger != None: 
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadThread", ThreadIDStr], Text="File \"" + FileName + "\" Retry count is max", Type="ERROR")
            self.add(self.ThreadINFOs[ThreadID]["Jobbase"], ProjectID=0, SourceProjectID=ProjectID)
            return("RetryFailure")
        self.ThreadINFOs[ThreadID]["Jobbase"]["Retry"] -= 1

        if URL == None: raise KeyError("not have URL")
        if "$" in URL: URL = self.AdvancedPath.path(URL)
        if "$" in OutputPath: OutputPath = Path.path(OutputPath)
        if FileName == None: FileName = self.ReCompile.search(URL).group(1)

        OutputPaths = OutputPath + "\\" + FileName

        if Overwrite == False:
            if DFCheck.dfcheck("f", OutputPaths) == True:
                if ProjectID != None:
                    self.Project_addJob(ProjectID, CompletedTasksCount=1)
                if self.Logger != None: 
                    self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadThread", ThreadIDStr], Text="File \"" + FileName + "\" is Exist, Skipping.")
                return("FileExist")

        if Session == None:
            Session = requests.Session()
            Session.headers = self.Configs['Headers']
        File = BytesIO()
        try:
            Request = Session.get(URL, timeout=Timeout)
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
            if self.Logger != None: 
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadThread", ThreadIDStr], Text="File \"" + FileName + "\" Download failure, By ConnectionError, From \"" + URL + "\"", Type="WARN")
            self.add(self.ThreadINFOs[ThreadID]["Jobbase"], ProjectID=ProjectID)
            self.Project_addJob(ProjectID, CompletedTasksCount=1)
            return("DownloadFailure")

        if Size != None:
            if len(File.getbuffer()) != Size:
                if self.Logger != None: 
                    self.Logger.GenLog(
                        Perfixs=self.LogHeader + ["DownloadThread", ThreadIDStr], 
                        Text="File \"" + FileName + "\" Download failure, By SizeError, From \"" + URL + "\", Buffer size " + str(len(File.getbuffer())), 
                        Type="WARN")
                self.add(self.ThreadINFOs[ThreadID]["Jobbase"], ProjectID=ProjectID)
                self.Project_addJob(ProjectID, CompletedTasksCount=1)
                return("SizeFailure")

        DFCheck.dfcheck("dm", OutputPath)
        Savefile.savefile(OutputPaths, File.getbuffer(), filetype="bytes")

        if self.Logger != None: self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadThread", ThreadIDStr], Text="File \"" + FileName + "\" Downloaded", Type="DEBUG")
        if ProjectID != None: self.Project_addJob(ProjectID, CompletedTasksCount=1)
        return("Done")


    #下载服务
    def downloadservice(self):
        if self.Logger != None: 
            self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadService"], Text="Download Service Started.")
        self.ServiceStartTime = int(time())
        while True:
            while len(self.JobQueue.queue) != 0:
                Job = self.JobQueue.get()
                ThreadID = self.Service_ReturnFirstIdleThreadId()

                if ThreadID == "AppendNewThread":
                    ThreadID = len(self.Threads)

                    self.ThreadINFOs[ThreadID]["Jobbase"] = Job
                    Job["ThreadID"] = ThreadID
                    Job["Session"] = self.RequestsSession
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
                if self.Service_CheckAllThreadStopped() == False:
                    if self.Logger != None: 
                        self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadService"], Text="Download Service Stopped, All Thread Stopped.")
                    break

            if (self.ServiceStartTime + self.Configs["ServiceAutoStop"]) <= int(time()):
                if self.Logger != None: 
                    self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadService"], Text="Download Service Auto Stopped.")
                break

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

    def Service_StartAllNotActivatedThread(self) -> None:
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
    def add(self, InputJob, autoStartService=True, ProjectID=None, FailuredTasksCount=1, SourceProjectID=None) -> int:
        if type(InputJob) == type(list()):
            JobTotal = len(InputJob)
            if ProjectID == None:
                ProjectID = self.Project_create(JobTotal)
            else:
                self.Project_addJob(ProjectID, JobTotal)

            for i in range(JobTotal):
                Job = InputJob[i]
                Job["ProjectID"] = ProjectID
                self.JobQueue.put(Job)

            if autoStartService == True:
                self.StartService()

            if self.Logger != None: 
                self.Logger.GenLog(self.LogHeader + ["AddTask"], "Added " + str(JobTotal) + " tasks to Project " + str(ProjectID))

            return(ProjectID)

        elif type(InputJob) == type(dict()):
            if ProjectID == None:
                ProjectID = self.Project_create(1)
            elif ProjectID == 0:
                self.Project_addJob(ProjectID, AllTasksCount=1, FailuredTasksCount=FailuredTasksCount, SourceProjectID=SourceProjectID)
            else:
                self.Project_addJob(ProjectID, AllTasksCount=1)
            InputJob["ProjectID"] = ProjectID
            
            if ProjectID != 0:
                self.JobQueue.put(InputJob)
            else:
                self.Projects[0]["Tasks"].append(InputJob)

            if autoStartService == True:
                self.StartService()
            
            if self.Logger != None: 
                self.Logger.GenLog(Perfixs=self.LogHeader + ["AddTask"], Text="Added 1 task to " + str(ProjectID))

            return(ProjectID)


    #重试来自Project0的任务
    def Retry(self) -> int:
        if self.Logger != None: 
            self.Logger.GenLog(Perfixs=self.LogHeader + ["Retry"], Text="Retry tasks from Project 0")
        Tasks = []
        for i in self.Projects[0]["Tasks"]:
            del(i["ThreadID"])
            i["Retry"] = 5
            if i["OfficialURL"]:
                i["URL"] = i["OfficialURL"]
                del(i["OfficialURL"])
            Tasks.append(i)
        self.Projects[0]["Tasks"] = []
        return(self.add(Tasks))


    #启动服务
    def StartService(self) -> None:
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
    def StopService(self, join=False) -> None:
        if self.DownloadServiceStatus:
            self.DownloadServiceStatus = False
            if join == False:
                while True:
                    if self.DownloadService.is_alive() == False:
                        break
                    sleep(self.Configs["ServiceSleepTime"])


    #建立Project
    def Project_create(self, AllTasksCount=0) -> int:
        while True:
            NewProjectID = randint(1,4096)
            if NewProjectID in self.Projects.keys():
                continue
            self.Projects[NewProjectID] = {"CompletedTasksCount": 0, "AllTasksCount": AllTasksCount, "FailuredTasksCount": 0}
            if self.Logger != None: 
                self.Logger.GenLog(Perfixs=self.LogHeader + ["CreateProject"], Text="Created New Project " + str(NewProjectID))
            return(NewProjectID)


    def Project_addJob(self, ProjectID, AllTasksCount=None, CompletedTasksCount=None, FailuredTasksCount=None, SourceProjectID=None) -> None:
        if ProjectID == 0:
            if (FailuredTasksCount == None) or (SourceProjectID == None): raise ValueError
            self.Projects[SourceProjectID]["FailuredTasksCount"] += FailuredTasksCount

        if AllTasksCount != None:
            self.Projects[ProjectID]["AllTasksCount"] += AllTasksCount

        if CompletedTasksCount != None:
            self.Projects[ProjectID]["CompletedTasksCount"] += CompletedTasksCount


    #通过ProjectID阻塞线程
    def Project_join(self, ProjectID) -> int:
        while True:
            if (self.Projects[ProjectID]["CompletedTasksCount"] + self.Projects[ProjectID]["FailuredTasksCount"]) == self.Projects[ProjectID]["AllTasksCount"]:
                break
            sleep(self.Configs["ServiceSleepTime"])
        return(self.Projects[ProjectID]["FailuredTasksCount"])

