#VERSION=24
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

from .Exceptions import Download as Ex_Download
from .AdvancedPath import path as aPath
from .Logs import Logs
from .DFCheck import dfCheck
from .File import saveFile
from .Configs import Configs


class DownloadManager():
    # 下载管理器
    def __init__(self, Logger: Logs | None = None):
        # 定义全局 Logger
        if Logger != None:
            self.Logger = Logger
            self.LogHeader = ["Claset/Downloader"]
        else: self.Logger = None

        self.Configs = Configs(Logger=Logger, LoggerHeader=self.LogHeader).getConfig("Download", TargetLastVersion=0)
        self.FindFileName = reCompile(r"([a-zA-Z0-9_.-]+)$")
        self.Projects = dict()
        self.AdvancedPath = aPath(Others=True, OtherTypes=["&F<Mirrors>&V<&F<Settings>&V<DownloadServer>>", "&F<Mirrors>&V<Official>"])
        self.DownloadsTasks = list()

        # 线程池(ThreadPool)
        self.ThreadPool = ThreadPoolExecutor(max_workers=self.Configs["MaxThread"], thread_name_prefix="DownloadTask")

        # 定义全局 Requests Session
        self.RequestsSession = Session()
        self.RequestsSession.headers = self.Configs['Headers']
        self.RequestsSession.trust_env = self.Configs["UseSystemProxy"]
        if self.Configs["UseSystemProxy"] == True:
            self.RequestsSession.proxies = self.Configs["Proxies"]

        self.Stopping = False


    # 简易下载器(Download) 的代理运行器
    def Download(self, Task: dict) -> None:
        if self.Stopping == True: raise Ex_Download.Stopping

        if not "URL"            in Task: raise Ex_Download.MissingURL
        if not "OutputPath"     in Task: Task["OutputPath"]     = "$PERFIX"
        if not "FileName"       in Task: Task["FileName"]       = self.ReCompile.search(Task["URL"]).group(1)
        if not "Size"           in Task: Task["Size"]           = None
        if not "ProjectID"      in Task: Task["ProjectID"]      = None
        if not "Overwrite"      in Task: Task["Overwrite"]      = True
        if not "Sha1"           in Task: Task["Sha1"]           = None
        if not "ConnectTimeout" in Task: Task["ConnectTimeout"] = self.Configs["Timeouts"]["Connect"]
        if not "ReadTimeout"    in Task: Task["ReadTimeout"]    = self.Configs["Timeouts"]["Read"]
        if not "Retry"          in Task: Task["Retry"]          = self.Configs["Retry"]

        if "$" in Task["URL"]: Task["URL"] = self.AdvancedPath.path(Task["URL"])
        if "$" in Task["OutputPath"]: Task["OutputPath"] = self.AdvancedPath.path(Task["OutputPath"])

        Retry = True

        while Retry == True:
            Retry = False
            Errored = False
            try:
                self.download(
                    URL=Task["URL"],
                    OutputPath=Task["OutputPath"],
                    FileName=Task["FileName"],
                    Size=Task["Size"],
                    Overwrite=Task["Overwrite"],
                    Sha1=Task["Sha1"],
                    ConnectTimeout=Task["ConnectTimeout"],
                    ReadTimeout=Task["ReadTimeout"]
                )

            # 错误处理
            except Ex_Download.Stopping:
                Task["Retry"] = 0
            except Ex_Download.SizeError:
                Errored = True
                self.projectAddJob(Task["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" Download failure, By SizeError, From \"", Task["URL"], "\""], Type="WARN")
            except Ex_Download.FileExist:
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" is Exist, Skipping"])
            except Ex_Download.SchemaError:
                Errored = True
                self.projectAddJob(Task["ProjectID"], ErrorTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["URL \"", Task["URL"], "\""], Type="ERROR")
            except Ex_Download.HashError:
                Errored = True
                self.projectAddJob(Task["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" hash verification failed"], Type="WARN")
            except Ex_Download.ReadTimeout:
                Errored = True
                self.projectAddJob(Task["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" Download timeout, From \"", Task["URL"], "\""], Type="WARN")
            except Ex_Download.ConnectTimeout:
                Errored = True
                self.projectAddJob(Task["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" Connect timeout, From \"", Task["URL"], "\""], Type="WARN")
            except Ex_Download.DownloadExceptions:
                Errored = True
                self.projectAddJob(Task["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" Download failure, By ConnectionError, From \"", Task["URL"], "\""], Type="WARN")
            except Exception as exception:
                Errored = True
                self.projectAddJob(Task["ProjectID"], FailuredTasksCount=1)
                if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["Unknown Error: ", exception], Type="WARN")

            if Errored == True:
                if Task["Retry"] > 0:
                    Task["Retry"] -= 1
                    Retry = True
                else:
                    if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", Task["FileName"], "\" Retry Count Max"], Type="ERROR")
                    self.projectAddJob(Task["ProjectID"], ErrorTasksCount=1)
            else: self.projectAddJob(Task["ProjectID"], CompletedTasksCount=1)


    # 简易下载器
    def download(
        self,
        URL:            str, # 链接地址
        OutputPath:     str, # 输出位置
        FileName:       str, # 文件名
        Size:           int, # 文件大小(字节)
        Overwrite:     bool, # 覆盖已有的文件
        Sha1:           str, # 使用sha1验证下载结果
        ConnectTimeout: int, # 连接超时(若为空则使用全局设置)
        ReadTimeout:    int  # 下载超时(若为空则使用全局设置)
    ) -> None:

        OutputPaths = OutputPath + "/" + FileName

        if (Overwrite == False) and (dfCheck(Path=OutputPaths, Type="f")) == True: raise Ex_Download.FileExist

        if self.Configs["UseGobalRequestsSession"] == True:
            Session = self.RequestsSession
        else:
            Session = requests.Session()
            Session.headers = self.Configs['Headers']

        File = BytesIO()
        if self.Stopping == True: raise Ex_Download.Stopping

        try:
            Request = Session.get(URL, timeout=(ConnectTimeout, ReadTimeout))
            StatusCode = str(Request.status_code)
            if StatusCode[0] in ["4", "5"]: Request.raise_for_status()
            File.write(Request.content)
        except requests.exceptions.ConnectTimeout:
            raise Ex_Download.ConnectTimeout
        except requests.exceptions.ReadTimeout:
            raise Ex_Download.ReadTimeout
        except (
            requests.exceptions.MissingSchema,
            requests.exceptions.InvalidSchema
        ): raise Ex_Download.SchemaError
        except (
            requests.exceptions.ProxyError,
            requests.exceptions.HTTPError,
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError
        ): raise Ex_Download.DownloadExceptions

        if ((Size != None) and (len(File.getbuffer()))) != Size: raise Ex_Download.SizeError
        if ((Sha1 != None) and (sha1(File.getbuffer()).hexdigest() != Sha1)): raise Ex_Download.HashError

        dfCheck(Path=OutputPath, Type="dm")
        saveFile(Path=OutputPaths, FileContent=File.getbuffer(), Type="bytes")

        if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["DownloadTask"], Text=["File \"", FileName, "\" Downloaded"])


    # 添加多个任务至 Project, 不指定 ProjectID 则新建 Project 对象后返回对应的 ProjectID
    def addTasks(self, InputTasks: list, MainProjectID: int | None = None) -> int | None:
        if self.Stopping == True: raise Ex_Download.Stopping
        JobTotal = len(InputTasks)
        if MainProjectID == None:
            InputProjectID = False
            MainProjectID = self.projectCreate(AllTasksCount=JobTotal)
        else: InputProjectID = True
        if self.Logger != None: self.Logger.genLog(self.LogHeader + ["AddTask"], Text=["Adding ", JobTotal, " tasks to Project ", MainProjectID])

        for InputTask in InputTasks:
            InputTask["ProjectID"] = MainProjectID
            self.DownloadsTasks.append(self.ThreadPool.submit(self.Download, Task=InputTask))

        if self.Logger != None: self.Logger.genLog(self.LogHeader + ["AddTask"], Text=["Added ", JobTotal, " tasks to Project ", MainProjectID])
        if InputProjectID == False: return(MainProjectID)


    # 添加单个 dict 任务对象至 Project, 不指定 ProjectID 则新建 Project 对象后返回对应的 ProjectID
    def addTask(self, InputTask: dict, ProjectID: int | None = None) -> int | None:
        if self.Stopping == True: raise Ex_Download.Stopping
        if ProjectID == None:
            InputProjectID = False
            InputTask["ProjectID"] = self.projectCreate(AllTasksCount=1)
        else: InputTask["ProjectID"] = ProjectID
        if self.Logger != None: self.Logger.genLog(self.LogHeader + ["AddTask"], Text=["Adding 1 tasks to Project ", InputTask["ProjectID"]])

        self.DownloadsTasks.append(self.ThreadPool.submit(self.Download, Task=InputTask))

        if self.Logger != None: self.Logger.genLog(Perfixs=self.LogHeader + ["AddTask"], Text=["Added 1 task to Project ", InputTask["ProjectID"]])
        if InputProjectID == False: return(ProjectID)


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
    def projectCreate(self, AllTasksCount: int = 0, setProjectID: int = 0) -> int:
        if setProjectID == 0:
            Temp = True
            while Temp:
                NewProjectID = randint(1,4096)
                if not (NewProjectID in self.Projects.keys()): Temp = False
        else: NewProjectID = setProjectID
        self.Projects[NewProjectID] = {"CompletedTasksCount": 0, "AllTasksCount": AllTasksCount, "FailuredTasksCount": 0, "ErrorTasksCount":0}
        if self.Logger != None:
            self.Logger.genLog(Perfixs=self.LogHeader + ["CreateProject"], Text="Created New Project " + str(NewProjectID))
        return(NewProjectID)


    # 向 Project 对象添加任务
    def projectAddJob(self, ProjectID: int, AllTasksCount: int = None, CompletedTasksCount: int = None, FailuredTasksCount: int = None, ErrorTasksCount: int = None) -> None:
        if AllTasksCount != None:       self.Projects[ProjectID]["AllTasksCount"] += AllTasksCount
        if CompletedTasksCount != None: self.Projects[ProjectID]["CompletedTasksCount"] += CompletedTasksCount
        if FailuredTasksCount != None:  self.Projects[ProjectID]["FailuredTasksCount"] += FailuredTasksCount
        if ErrorTasksCount != None:     self.Projects[ProjectID]["ErrorTasksCount"] += ErrorTasksCount


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
            ErrorTasksCount += self.Projects[ProjectID]["ErrorTasksCount"]
        return(ErrorTasksCount)

