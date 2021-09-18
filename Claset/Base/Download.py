#VERSION=22
#
#Claset/Base/Download.py
#通过url下载数据
#

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1
from io import BytesIO
from random import randint
from re import compile as reCompile
from time import sleep

import requests.exceptions
from requests import Session

from . import AdvancedPath
from . import DFCheck
from . import Loadfile
from . import Path
from . import Savefile

from . import Exceptions


class DownloadManager():
    def __init__(self, Logger=None):
        self.Configs = Loadfile.loadFile("$EXEC/Configs/Download.json", "json")
        self.ReCompile = reCompile(self.Configs["ReadFileNameReString"])
        self.Projects = {0: {"CompletedTasksCount": 0, "AllTasksCount": 0, "FailuredTasksCount": 0, "Tasks": []}}
        self.AdvancedPath = AdvancedPath.path(Others=True, OtherTypes=[["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<1>", "&F<$EXEC/Configs/Settings.json>&V<DownloadServer>"], ["&F<$EXEC/Configs/GameDownloadMirrors.json>&V<Official>"]])
        self.DownloadsTasks = list()

        # 线程池(ThreadPool)
        self.ThreadPool = ThreadPoolExecutor(max_workers=self.Configs["MaxThread"], thread_name_prefix="DownloadTask")

        # 定义全局 Requests Session
        self.RequestsSession = Session()
        self.RequestsSession.headers = self.Configs['Headers']

        # 定义全局 Logger
        if Logger != None:
            self.Logger = Logger
            self.LogHeader = ["Downloader"]

        self.Stopping = False


    # 简易下载器(Download) 的代理运行器
    def Download(self, Base: dict) -> None:
        if self.Stopping == True: raise Exceptions.Download.Stopping

        if not "URL"            in Base: raise Exceptions.Download.MissingURL
        if not "OutputPath"     in Base: Base["OutputPath"]     = "$PERFIX"
        if not "FileName"       in Base: Base["FileName"]       = self.ReCompile.search(Base["URL"]).group(1)
        if not "Size"           in Base: Base["Size"]           = None
        if not "ProjectID"      in Base: Base["ProjectID"]      = None
        if not "Overwrite"      in Base: Base["Overwrite"]      = True
        if not "Sha1"           in Base: Base["Sha1"]           = None
        if not "ConnectTimeout" in Base: Base["ConnectTimeout"] = self.Configs["Timeouts"]["Connect"]
        if not "ReadTimeout"    in Base: Base["ReadTimeout"]    = self.Configs["Timeouts"]["Read"]
        if not "Retry"          in Base: Base["Retry"]          = self.Configs["Retry"]

        if "$" in Base["URL"]: Base["URL"] = self.AdvancedPath.path(Base["URL"])
        if "$" in Base["OutputPath"]: Base["OutputPath"] = Path.path(Base["OutputPath"])

        Retry = True

        while Retry == True:
            Retry = False
            Errored = False
            try:
                self.download(
                    URL=Base["URL"],
                    OutputPath=Base["OutputPath"],
                    FileName=Base["FileName"],
                    Size=Base["Size"],
                    ProjectID=Base["ProjectID"],
                    Overwrite=Base["Overwrite"],
                    Sha1=Base["Sha1"],
                    ConnectTimeout=Base["ConnectTimeout"],
                    ReadTimeout=Base["ReadTimeout"]
                    )
            except Exceptions.Download.Stopping:
                Errored = True
                Base["Retry"] = 0
            except Exceptions.Download.SizeError:
                Errored = True
                self.projectAddJob(Base["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Base["FileName"], "\" Download failure, By SizeError, From \"", Base["URL"], "\""], Type="WARN")
            except Exceptions.Download.FileExist:
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Base["FileName"], "\" is Exist, Skipping"])
            except Exceptions.Download.SchemaError:
                Errored = True
                self.projectAddJob(Base["ProjectID"], ErrorTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["URL \"", Base["URL"], "\""], Type="ERROR")
            except Exceptions.Download.HashError:
                Errored = True
                self.projectAddJob(Base["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Base["FileName"], "\" hash verification failed"], Type="WARN")
            except Exceptions.Download.ReadTimeout:
                Errored = True
                self.projectAddJob(Base["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Base["FileName"], "\" Download timeout, From \"", Base["URL"], "\""], Type="WARN")
            except Exceptions.Download.ConnectTimeout:
                Errored = True
                self.projectAddJob(Base["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Base["FileName"], "\" Connect timeout, From \"", Base["URL"], "\""], Type="WARN")
            except Exceptions.Download.DownloadExceptions:
                Errored = True
                self.projectAddJob(Base["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Base["FileName"], "\" Download failure, By ConnectionError, From \"", Base["URL"], "\""], Type="WARN")

            if Errored == True:
                if Base["Retry"] > 0:
                    Base["Retry"] -= 1
                    Retry = True
                else: self.projectAddJob(Base["ProjectID"], ErrorTasksCount=1)
            else: self.projectAddJob(Base["ProjectID"], CompletedTasksCount=1)


    # 简易下载器
    def download(
        self,
        URL:            str, # 链接地址
        OutputPath:     str, # 输出位置
        FileName:       str, # 文件名
        Size:           int, # 文件大小(字节)
        ProjectID:      int, # 任务id
        Overwrite:     bool, # 覆盖已有的文件
        Sha1:           str, # 使用sha1验证下载结果
        ConnectTimeout: int, # 连接超时(若为空则使用全局设置)
        ReadTimeout:    int  # 下载超时(若为空则使用全局设置)
        ) -> None:

        OutputPaths = OutputPath + "\\" + FileName

        if Overwrite == False:
            if DFCheck.dfCheck("f", OutputPaths) == True: raise Exceptions.Download.FileExist

        if self.Configs["UseGobalRequestsSession"] == True:
            Session = self.RequestsSession
        else:
            Session = requests.Session()
            Session.headers = self.Configs['Headers']

        File = BytesIO()
        if self.Stopping == True: raise Exceptions.Download.Stopping

        try:
            Request = Session.get(URL, timeout=(ConnectTimeout, ReadTimeout))
            StatusCode = str(Request.status_code)
            if StatusCode[0] in ["4", "5"]: Request.raise_for_status()
            File.write(Request.content)
        except requests.exceptions.ConnectTimeout:
            raise Exceptions.Download.ConnectTimeout
        except requests.exceptions.ReadTimeout:
            raise Exceptions.Download.ReadTimeout
        except (
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema
        ): raise Exceptions.Download.SchemaError
        except (
            requests.exceptions.ProxyError,
            requests.exceptions.HTTPError,
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError
        ): raise Exceptions.Download.DownloadExceptions

        if Size != None:
            if len(File.getbuffer()) != Size: raise Exceptions.Download.SizeError

        if Sha1 != None:
            hashobj = sha1(File.getbuffer()).hexdigest()
            if hashobj != Sha1: raise Exceptions.Download.HashError

        DFCheck.dfCheck("dm", OutputPath)
        Savefile.saveFile(OutputPaths, File.getbuffer(), filetype="bytes")

        if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", FileName, "\" Downloaded"])
        if ProjectID != None: self.projectAddJob(ProjectID, CompletedTasksCount=1)


    # 添加任务至 Project, 不指定 ProjectID 则新建 Project 对象后返回对应的 ProjectID
    def addTasks(self, InputJob: list, ProjectID: int = None) -> int:
        if self.Stopping == True: raise Exceptions.Download.Stopping
        if type(InputJob) == type(list()):
            JobTotal = len(InputJob)
            if ProjectID == None:
                ProjectID = self.projectCreate(JobTotal)
            else:
                self.projectAddJob(ProjectID, JobTotal)

            if self.Logger != None:
                self.Logger.genLog(self.LogHeader + ["AddTask"], Text=["Adding ", str(JobTotal), " tasks to Project ", str(ProjectID)])
            
            Temp = list()
            for i in range(JobTotal):
                Job = InputJob[i]
                Job["ProjectID"] = ProjectID
                Temp.append(self.ThreadPool.submit(self.Download, Base=Job))
            self.DownloadsTasks.extend(Temp)

            if self.Logger != None:
                self.Logger.genLog(self.LogHeader + ["AddTask"], Text=["Added ", str(JobTotal), " tasks to Project ", str(ProjectID)])

            return(ProjectID)

        elif type(InputJob) == type(dict()):
            if ProjectID == None:
                ProjectID = self.projectCreate(1)

            self.projectAddJob(ProjectID, AllTasksCount=1)

            if self.Logger != None:
                self.Logger.genLog(self.LogHeader + ["AddTask"], Text="Adding 1 tasks to Project " + str(ProjectID))

            InputJob["ProjectID"] = ProjectID

            if ProjectID == 0:
                self.Projects[0]["Tasks"].append(InputJob)
            else:
                self.DownloadsTasks.append(self.ThreadPool.submit(self.Download, Base=InputJob))

            if self.Logger != None:
                self.Logger.genLog(Perfixs=self.LogHeader + ["AddTask"], Text="Added 1 task to Project " + str(ProjectID))

            return(ProjectID)


    # 重试来自 Project 0 的任务
    def retry(self) -> list:
        if self.Logger != None:
            self.Logger.genLog(Perfixs=self.LogHeader + ["Retry"], Text="Retry tasks from Project 0")
        Tasks = list()
        for i in self.Projects[0]["Tasks"]:
            del(i["ThreadID"])
            i["Retry"] = 5
            if i["OtherURL"]:
                i["URL"] = i["OtherURL"]
                del(i["OtherURL"])
            Tasks.append(i)
        self.Projects[0]["Tasks"] = []
        return(self.addTasks(Tasks))


    # 停止可停止的一切 Project 对象
    def stop(self) -> None:
        self.Stopping = True
        CantCancelled, BeingCancelled, Cancelled = int(), int(), int()
        for Task in self.DownloadsTasks:
            if Task.done(): pass
            elif Task.running():
                if self.Logger != None: CantCancelled += 1
            elif Task.cancel():
                if self.Logger != None: BeingCancelled += 1
            if Task.cancelled():
                if self.Logger != None: Cancelled += 1

        if CantCancelled != 0:
            self.Logger.genLog(Perfixs=self.LogHeader + ["Stopping"], Text=[CantCancelled, " task cannot be cancelled, ", BeingCancelled, " task is being cancelled, ", Cancelled, " task cancelled"], Type="WARN")
        else:
            self.Logger.genLog(Perfixs=self.LogHeader + ["Stopping"], Text=["0 task cannot be cancelled, ", BeingCancelled, " task is being cancelled, ", Cancelled, " task cancelled"])


    # 建立 Project 对象
    def projectCreate(self, AllTasksCount: int = 0) -> int:
        while True:
            NewProjectID = randint(1,4096)
            if NewProjectID in self.Projects.keys():
                continue
            self.Projects[NewProjectID] = {"CompletedTasksCount": 0, "AllTasksCount": AllTasksCount, "FailuredTasksCount": 0, "ErrorTasksCount":0}
            if self.Logger != None:
                self.Logger.genLog(Perfixs=self.LogHeader + ["CreateProject"], Text="Created New Project " + str(NewProjectID))
            return(NewProjectID)


    # 向 Project 对象添加任务
    def projectAddJob(self, ProjectID: int, AllTasksCount: int = None, CompletedTasksCount: int = None, FailuredTasksCount: int = None, ErrorTasksCount: int = None) -> None:
        if AllTasksCount != None:
            self.Projects[ProjectID]["AllTasksCount"] += AllTasksCount

        if CompletedTasksCount != None:
            self.Projects[ProjectID]["CompletedTasksCount"] += CompletedTasksCount

        if FailuredTasksCount != None:
            self.Projects[ProjectID]["FailuredTasksCount"] += FailuredTasksCount

        if ErrorTasksCount != None:
            self.Projects[ProjectID]["ErrorTasksCount"] += ErrorTasksCount


    # 通过 ProjectID 的列表阻塞线程, 阻塞结束后返回总错误计数
    def projectJoin(self, ProjectIDs: list) -> int:
        if type(ProjectIDs) == type(int()):
            Temp = list()
            Temp.append(ProjectIDs)
            ProjectIDs = Temp
        ErrorTasksCount = int()
        for ProjectID in ProjectIDs:
            while True:
                if (self.Projects[ProjectID]["CompletedTasksCount"] + self.Projects[ProjectID]["ErrorTasksCount"]) == self.Projects[ProjectID]["AllTasksCount"]:
                    break
                sleep(self.Configs["SleepTime"])
                #print(self.Projects[ProjectID]["CompletedTasksCount"],self.Projects[ProjectID]["ErrorTasksCount"],self.Projects[ProjectID]["AllTasksCount"])
                #print(self.DownloadsTasks[0].exception())
            ErrorTasksCount += self.Projects[ProjectID]["ErrorTasksCount"]
        return(ErrorTasksCount)

