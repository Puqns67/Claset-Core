#VERSION=19
#
#Claset/Base/Download.py
#通过url下载数据
#

import re
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from random import randint
from time import sleep
from hashlib import sha1

import requests

from . import AdvancedPath, DFCheck, Loadfile, Path, Savefile


class downloadmanager():
    def __init__(self, Logger=None):
        self.Configs = Loadfile.loadfile("$EXEC/Configs/Download.json", "json")
        self.ReCompile = re.compile(self.Configs["ReadFileNameReString"])
        self.Projects = {0: {"CompletedTasksCount": 0, "AllTasksCount": 0, "FailuredTasksCount": 0, "Tasks": []}}
        self.AdvancedPath = AdvancedPath.path(Others=True, OtherTypes=[["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<1>", "&F<$EXEC/Configs/Settings.json>&V<DownloadServer>"], ["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<Official>"]])
        self.DownloadsTasks = []

        #ThreadPool
        self.ThreadPool = ThreadPoolExecutor(max_workers=self.Configs["MaxThread"])

        #全局Session
        self.RequestsSession = requests.Session()
        self.RequestsSession.headers = self.Configs['Headers']

        #定义全局Logger
        if Logger != None:
            self.Logger = Logger
            self.LogHeader = ["Downloader"]


    #简易下载器
    def download(self, Base) -> str:
        #URL: 链接地址
        #OutputPath: 输出位置
        #FileName: 文件名
        #Size: 文件大小(字节)
        #ProjectID: 任务id
        #Overwrite: 覆盖已有的文件
        #Timeout: 传输超时
        #Session: 全局Session
        #Base: 源Jobs
        #Sha1: 使用sha1验证下载结果

        if not "URL" in Base: raise KeyError("not have URL")
        if not "OutputPath" in Base: Base["OutputPath"] = "$PERFIX"
        if not "FileName" in Base: Base["FileName"] = None
        if not "Size" in Base: Base["Size"] = None
        if not "ProjectID" in Base: Base["ProjectID"] = None
        if not "Overwrite" in Base: Base["Overwrite"] = True
        if not "Timeout" in Base: Base["Timeout"] = None
        if not "Session" in Base: Base["Session"] = None
        if not "Sha1" in Base: Base["Sha1"] = None
        RawBase = Base

        if Base["Timeout"] == None: Base["Timeout"] = self.Configs["Timeout"]
        if "$" in Base["URL"]: Base["URL"] = self.AdvancedPath.path(Base["URL"])
        if "$" in Base["OutputPath"]: Base["OutputPath"] = Path.path(Base["OutputPath"])
        if Base["FileName"] == None: Base["FileName"] = self.ReCompile.search(Base["URL"]).group(1)

        OutputPaths = Base["OutputPath"] + "\\" + Base["FileName"]

        if Base["Overwrite"] == False:
            if DFCheck.dfcheck("f", OutputPaths) == True:
                if Base["ProjectID"] != None:
                    self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
                if self.Logger != None:
                    self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" is Exist, Skipping.")
                return("FileExist")

        if Base["Session"] == None:
            Session = requests.Session()
            Session.headers = self.Configs['Headers']
        File = BytesIO()
        try:
            Request = Base["Session"].get(Base["URL"], timeout=Base["Timeout"])
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
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Download failure, By ConnectionError, From \"" + Base["URL"] + "\"", Type="WARN")
            self.add(RawBase, ProjectID=Base["ProjectID"])
            self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
            return("DownloadFailure")

        if Base["Size"] != None:
            if len(File.getbuffer()) != Base["Size"]:
                if self.Logger != None:
                    self.Logger.GenLog(
                        Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Download failure, By SizeError, From \"" + Base["URL"] + "\", Buffer size " + str(len(File.getbuffer())), Type="WARN")
                self.add(RawBase, ProjectID=Base["ProjectID"])
                self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
                return("SizeFailure")

        if Base["Sha1"] != None:
            hashobj = sha1(File.getbuffer()).hexdigest()
            if hashobj != Base["Sha1"]:
                if self.Logger != None:
                    self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" hash verification failed", Type="WARN")
                self.add(RawBase, ProjectID=Base["ProjectID"])
                self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
                return("HashFailure")

        DFCheck.dfcheck("dm", Base["OutputPath"])
        Savefile.savefile(OutputPaths, File.getbuffer(), filetype="bytes")

        if self.Logger != None: self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Downloaded", Type="DEBUG")
        if Base["ProjectID"] != None: self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
        return("Done")


    def add(self, InputJob, ProjectID=None, FailuredTasksCount=1, SourceProjectID=None) -> int:
        if type(InputJob) == type(list()):
            JobTotal = len(InputJob)
            if ProjectID == None:
                ProjectID = self.Project_create(JobTotal)
            else:
                self.Project_addJob(ProjectID, JobTotal)

            for i in range(JobTotal):
                Job = InputJob[i]
                Job["ProjectID"] = ProjectID
                Job["Session"] = self.RequestsSession
                self.DownloadsTasks.append(self.ThreadPool.submit(self.download, Base=Job))

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

            if ProjectID == 0:
                self.Projects[0]["Tasks"].append(InputJob)
            else:
                InputJob["Session"] = self.RequestsSession
                self.DownloadsTasks.append(self.ThreadPool.submit(self.download, Base=InputJob))

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
            if i["OtherURL"]:
                i["URL"] = i["OtherURL"]
                del(i["OtherURL"])
            Tasks.append(i)
        self.Projects[0]["Tasks"] = []
        return(self.add(Tasks))


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

