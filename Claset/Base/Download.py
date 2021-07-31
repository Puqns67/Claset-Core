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

#Exceptions
class DownloadException(Exception): pass
class FileExist(DownloadException): pass
class Timeout(DownloadException): pass 
class ConnectTimeout(Timeout): pass
class ReadTimeout(Timeout): pass
class HashError(DownloadException): pass
class SizeError(DownloadException): pass
class SchemaError(DownloadException): pass


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
    def download(self, Base) -> None:
        #URL: 链接地址
        #OutputPath: 输出位置
        #FileName: 文件名
        #Size: 文件大小(字节)
        #ProjectID: 任务id
        #Overwrite: 覆盖已有的文件
        #ConnectTimeout: 连接超时(若为空则使用全局设置)
        #ReadTimeout: 下载超时(若为空则使用全局设置)
        #Session: 全局Session
        #Base: 源Jobs
        #Sha1: 使用sha1验证下载结果

        if not "URL" in Base: raise KeyError("not have URL")
        if not "OutputPath" in Base: Base["OutputPath"] = "$PERFIX"
        if not "FileName" in Base: Base["FileName"] = self.ReCompile.search(Base["URL"]).group(1)
        if not "Size" in Base: Base["Size"] = None
        if not "ProjectID" in Base: Base["ProjectID"] = None
        if not "Overwrite" in Base: Base["Overwrite"] = True
        if not "Session" in Base: Base["Session"] = None
        if not "Sha1" in Base: Base["Sha1"] = None
        if not "ConnectTimeout" in Base: Base["ConnectTimeout"] = self.Configs["Timeouts"]["Connect"]
        if not "ReadTimeout" in Base: Base["ReadTimeout"] = self.Configs["Timeouts"]["Read"]
        if not "Retry" in Base: Base["Retry"] = self.Configs["Retry"]
        RawBase = Base

        if "$" in Base["URL"]: Base["URL"] = self.AdvancedPath.path(Base["URL"])
        if "$" in Base["OutputPath"]: Base["OutputPath"] = Path.path(Base["OutputPath"])

        OutputPaths = Base["OutputPath"] + "\\" + Base["FileName"]

        if Base["Overwrite"] == False:
            if DFCheck.dfcheck("f", OutputPaths) == True:
                if Base["ProjectID"] != None:
                    self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
                if self.Logger != None:
                    self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" is Exist, Skipping")
                raise FileExist

        if Base["Session"] == None:
            Session = requests.Session()
            Session.headers = self.Configs['Headers']
        File = BytesIO()

        try:
            Request = Base["Session"].get(Base["URL"], timeout=(Base["ConnectTimeout"], Base["ReadTimeout"]))
            StatusCode = str(Request.status_code)
            if StatusCode[0] in ["4", "5"]: Request.raise_for_status()
            File.write(Request.content)
        except requests.exceptions.ConnectTimeout:
            if self.Logger != None:
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Connect timeout, From \"" + Base["URL"] + "\"", Type="WARN")
            self.add(RawBase, ProjectID=Base["ProjectID"])
            self.Project_addJob(Base["ProjectID"], FailuredTasksCount=1)
            raise ConnectTimeout
        except requests.exceptions.ReadTimeout:
            if self.Logger != None:
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Download timeout, From \"" + Base["URL"] + "\"", Type="WARN")
            self.add(RawBase, ProjectID=Base["ProjectID"])
            self.Project_addJob(Base["ProjectID"], FailuredTasksCount=1)
            raise ReadTimeout
        except (
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema
        ):
            if self.Logger != None:
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="URL \"" + Base["URL"] + "\" ", Type="WARN")
            self.add(RawBase, ProjectID=0)
            self.Project_addJob(Base["ProjectID"], ErrorTasksCount=1)
            raise SchemaError
        except (
            requests.exceptions.ProxyError,
            requests.exceptions.HTTPError,
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError
        ):
            if self.Logger != None:
                self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Download failure, By ConnectionError, From \"" + Base["URL"] + "\"", Type="WARN")
            self.add(RawBase, ProjectID=Base["ProjectID"])
            self.Project_addJob(Base["ProjectID"], FailuredTasksCount=1)
            raise DownloadException

        if Base["Size"] != None:
            if len(File.getbuffer()) != Base["Size"]:
                if self.Logger != None:
                    self.Logger.GenLog(
                        Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Download failure, By SizeError, From \"" + Base["URL"] + "\", Buffer size " + str(len(File.getbuffer())), Type="WARN")
                self.add(RawBase, ProjectID=Base["ProjectID"])
                self.Project_addJob(Base["ProjectID"], FailuredTasksCount=1)
                return("SizeError")

        if Base["Sha1"] != None:
            hashobj = sha1(File.getbuffer()).hexdigest()
            if hashobj != Base["Sha1"]:
                if self.Logger != None:
                    self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" hash verification failed", Type="WARN")
                self.add(RawBase, ProjectID=Base["ProjectID"])
                self.Project_addJob(Base["ProjectID"], FailuredTasksCount=1)
                return("HashError")

        DFCheck.dfcheck("dm", Base["OutputPath"])
        Savefile.savefile(OutputPaths, File.getbuffer(), filetype="bytes")

        if self.Logger != None: self.Logger.GenLog(Perfixs=self.LogHeader + ["DownloadTask"], Text="File \"" + Base["FileName"] + "\" Downloaded", Type="DEBUG")
        if Base["ProjectID"] != None: self.Project_addJob(Base["ProjectID"], CompletedTasksCount=1)
        return("Done")


    def add(self, InputJob, ProjectID=None) -> int:
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

            self.Project_addJob(ProjectID, AllTasksCount=1)
            InputJob["ProjectID"] = ProjectID

            if ProjectID == 0:
                self.Projects[0]["Tasks"].append(InputJob)
            else:
                InputJob["Session"] = self.RequestsSession
                self.DownloadsTasks.append(self.ThreadPool.submit(self.download, Base=InputJob))

            if self.Logger != None:
                self.Logger.GenLog(Perfixs=self.LogHeader + ["AddTask"], Text="Added 1 task to Project " + str(ProjectID))

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
            self.Projects[NewProjectID] = {"CompletedTasksCount": 0, "AllTasksCount": AllTasksCount, "FailuredTasksCount": 0, "ErrorTasksCount":0}
            if self.Logger != None:
                self.Logger.GenLog(Perfixs=self.LogHeader + ["CreateProject"], Text="Created New Project " + str(NewProjectID))
            return(NewProjectID)


    def Project_addJob(self, ProjectID, AllTasksCount=None, CompletedTasksCount=None, FailuredTasksCount=None, ErrorTasksCount=None) -> None:
        if AllTasksCount != None:
            self.Projects[ProjectID]["AllTasksCount"] += AllTasksCount

        if CompletedTasksCount != None:
            self.Projects[ProjectID]["CompletedTasksCount"] += CompletedTasksCount

        if FailuredTasksCount != None:
            self.Projects[ProjectID]["FailuredTasksCount"] += FailuredTasksCount
        
        if ErrorTasksCount != None:
            self.Projects[ProjectID]["ErrorTasksCount"] += ErrorTasksCount


    #通过ProjectID阻塞线程
    def Project_join(self, ProjectID) -> int:
        while True:
            if (self.Projects[ProjectID]["CompletedTasksCount"] + self.Projects[ProjectID]["FailuredTasksCount"] + self.Projects[ProjectID]["ErrorTasksCount"]) == self.Projects[ProjectID]["AllTasksCount"]:
                break
            sleep(self.Configs["SleepTime"])
        return(self.Projects[ProjectID]["ErrorTasksCount"])

