# -*- coding: utf-8 -*-
"""通过 URL 列表多线程下载数据"""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1
from io import BytesIO
from logging import getLogger
from os.path import basename as baseName, split as splitPath
from random import randint
from re import search
from time import sleep
from typing import Any

from Claset import __fullversion__
from requests import (
    __version__ as RequestsVersion, Session, post,
    exceptions as Ex_Requests, packages as requestsPackages
)
from urllib3 import __version__ as Urllib3Version

from .Configs import Configs
from .Exceptions import Download as Ex_Download
from .File import dfCheck, loadFile, saveFile
from .Path import pathAdder, path as Pathmd

__all__ = ("getSession", "DownloadTask", "DownloadManager",)
Logger = getLogger(__name__)
DownloadConfigs = Configs(ID="Download")


def getSession(TheSession: Session | None = None) -> Session:
    """设置/获取 Session"""
    if TheSession == None: TheSession = Session()

    TheSession.stream = True
    TheSession.trust_env = DownloadConfigs["UseSystemProxy"]
    TheSession.verify = DownloadConfigs["SSLVerify"]

    # 设置代理
    if DownloadConfigs["SSLVerify"] == False:
        requestsPackages.urllib3.disable_warnings()

    if DownloadConfigs["ProxyLink"] != None:
        try:
            post(DownloadConfigs["ProxyLink"])
        except Ex_Requests.ConnectionError:
            Logger.warning("Unable to connect to the proxy server: \"%s\", Disable it", DownloadConfigs["ProxyLink"])
        except Ex_Requests.InvalidSchema:
            Logger.warning("Proxy server url schema error: \"%s\", Disable it", DownloadConfigs["ProxyLink"])
        else:
            TheSession.proxies = {"http": DownloadConfigs["ProxyLink"], "https": DownloadConfigs["ProxyLink"]}
            # 使用代理时将强制禁用 SSL 验证与使用系统代理
            requestsPackages.urllib3.disable_warnings()
            TheSession.verify = False
            TheSession.trust_env = False

    # 设置 Headers
    SourceHeaders: dict = DownloadConfigs['Headers']
    SourceHeaders["user-agent"] = SourceHeaders["user-agent"].format(ClasetVersion=__fullversion__)
    TheSession.headers = SourceHeaders

    return(TheSession)


class DownloadTask():
    def __init__(
        self, URL: str, FileName: str | None = None, OutputPath: str | None = None, OutputPaths: str | None = None,
        Size: int | None = None, ProjectID: int | None = None, Overwrite: bool = True, Sha1: str | None = None,
        ConnectTimeout: int | None = None, ReadTimeout: int | None = None, Retry: int | None = None, Next: Any | None = None
        ) -> None:
        self.URL = URL
        self.FileName = FileName
        self.OutputPath = OutputPath
        self.OutputPaths = OutputPaths
        self.Size = Size
        self.ProjectID = ProjectID
        self.Overwrite = Overwrite
        self.Sha1 = Sha1
        self.ConnectTimeout = ConnectTimeout
        self.ReadTimeout = ReadTimeout
        self.Retry = Retry
        self.Next = Next
        self.ISFULL = False


    def full(self) -> None:
        """完善本 Task"""
        # 处理缺失的项目
        if ((self.OutputPaths == None) or (self.OutputPaths == str())):
            # 如不存在 OutputPath 或 OutputPath 为空, 则使用当前位置
            if ((self.OutputPath == None) or (self.OutputPath == str())):
                self.OutputPath = "$PREFIX"

            # 如不存在 FileName 则优先从 URL 中获取文件名, 若 FileName 为 None, 则优先从 OutPutPath 中获取文件名, 若都无法获取则使用 NoName
            if self.FileName == None:
                self.FileName = baseName(self.URL)
                if self.FileName == str():
                    self.FileName = baseName(self.OutputPath)
            if self.FileName == None:
                self.FileName = baseName(self.OutputPath)
                if self.FileName == str():
                    self.FileName = baseName(self.URL)
            if self.FileName == str():
                self.FileName = "NoName"

            # 从 OutputPath 中去除重复的文件名
            if ((self.FileName in self.OutputPath) and ((search(self.FileName + "$", self.OutputPath)) != None)):
                self.OutputPath = search("^(.*)" + self.FileName + "$", self.OutputPath).groups()[0]

            self.OutputPaths = pathAdder(self.OutputPath, self.FileName)
        else:
            try:
                self.OutputPath, self.FileName = splitPath(self.OutputPaths)
            except Exception:
                raise Ex_Download.UnpackOutputPathsError

        # 解析 Paths
        if "$" in self.URL:
            self.URL = Pathmd(self.URL)
        if "$" in self.OutputPaths:
            self.OutputPaths = Pathmd(self.OutputPaths, IsPath=True)

        self.ISFULL = True


class DownloadManager():
    """下载管理器"""
    DownloadsTasks = list()
    Projects = dict()
    Adding = False
    Stopping = False

    def __init__(self):
        # 线程池(ThreadPool)
        self.ThreadPool = ThreadPoolExecutor(max_workers=DownloadConfigs["MaxThread"], thread_name_prefix="DownloadTask")

        # 定义全局 Requests Session
        if DownloadConfigs["UseGobalRequestsSession"] == True:
            self.RequestsSession = getSession()

        Logger.debug("urllib3 Version: %s", Urllib3Version)
        Logger.debug("requests Version: %s", RequestsVersion)


    def Download(self, Task: DownloadTask) -> DownloadTask:
        """简易下载器 (Download) 的代理运行器"""
        if not Task.ISFULL:
            Task.full()

        Retry = True
        while Retry:
            Retry = False
            Errored = False
            StopType = "Downloaded"
            try:
                self.download(
                    URL=Task.URL,
                    OutputPaths=Task.OutputPaths,
                    Size=Task.Size,
                    Sha1=Task.Sha1,
                    Overwrite=Task.Overwrite,
                    ConnectTimeout=Task.ConnectTimeout,
                    ReadTimeout=Task.ReadTimeout
                )
            # 错误处理
            except Ex_Download.Stopping:
                StopType = "Stopping"
            except Ex_Download.SizeError:
                Errored = True
                self.addJobToProject(Task.ProjectID, FailuredTasksCount=1)
                Logger.warning("File \"%s\" Download failure, By SizeError, From \"%s\"", Task.FileName, Task.URL)
            except Ex_Download.FileExist:
                StopType = "FileExist"
            except Ex_Download.SchemaError:
                Errored = True
                self.addJobToProject(Task.ProjectID, ErrorTasksCount=1)
                Logger.error("URL \"%s\" Formart Error", Task.URL)
            except Ex_Download.HashError:
                Errored = True
                self.addJobToProject(Task.ProjectID, FailuredTasksCount=1)
                Logger.warning("File \"%s\" hash verification failed", Task.FileName)
            except Ex_Download.ReadTimeout:
                Errored = True
                self.addJobToProject(Task.ProjectID, FailuredTasksCount=1)
                Logger.warning("File \"%s\" Download timeout,  From \"%s\"", Task.FileName, Task.URL)
            except Ex_Download.ConnectTimeout:
                Errored = True
                self.addJobToProject(Task.ProjectID, FailuredTasksCount=1)
                Logger.warning("File \"%s\" Connect timeout, From \"%s\"", Task.FileName, Task.URL)
            except Ex_Download.DownloadExceptions:
                Errored = True
                self.addJobToProject(Task.ProjectID, FailuredTasksCount=1)
                Logger.warning("File \"%s\" Download failure, By ConnectionError, From \"%s\"", Task.FileName, Task.URL)
            except Exception:
                Errored = True
                self.addJobToProject(Task.ProjectID, FailuredTasksCount=1)
                Logger.warning("Unknown Error:", exc_info=True)

            if Errored == True:
                if Task.Retry > 0:
                    Task.Retry -= 1
                    Retry = True
                    continue
                else:
                    Logger.error("File \"%s\" Retry Count Max", Task.FileName)
                    self.addJobToProject(Task.ProjectID, ErrorTasksCount=1)
                    raise Ex_Download.DownloadExceptions
            else:
                self.addJobToProject(Task.ProjectID, CompletedTasksCount=1)
                # 没有出现下载错误之后尝试执行 Task.Next
                if Task.Next != None:
                    try:
                        Task.Next(Task)
                    except Exception:
                        Logger.warning("Next Error: ", exc_info=True)

                match StopType:
                    case "Downloaded": Logger.info("File \"%s\" Downloaded", Task.FileName)
                    case "Stopping": pass
                    case "FileExist": Logger.info("File \"%s\" is Exist, Skipping", Task.FileName)
                    case _: raise ValueError(StopType)

                if StopType != "Stopping":
                    return(Task)


    def download(
        self,
        URL:            str, # 链接地址
        OutputPaths:    str, # 输出路径
        Size:           int | None = None, # 文件大小(字节)
        Overwrite:     bool | None = None, # 覆盖已有的文件
        Sha1:           str | None = None, # 使用sha1验证下载结果
        ConnectTimeout: int | None = None, # 连接超时(若为空则使用全局设置)
        ReadTimeout:    int | None = None  # 下载超时(若为空则使用全局设置)
        ) -> None:
        """简易下载器"""
        if dfCheck(Path=OutputPaths, Type="f"):
            if Overwrite == False:
                if Sha1 != None:
                    if (sha1(loadFile(Path=OutputPaths, Type="bytes")).hexdigest() == Sha1):
                        raise Ex_Download.FileExist
                    else:
                        Logger.warning("File: \"%s\" sha1 verify Error! ReDownload it")
                else:
                    raise Ex_Download.FileExist

        if ConnectTimeout is None:
            ConnectTimeout = DownloadConfigs["Timeouts"]["Connect"]
        if ReadTimeout is None:
            ReadTimeout = DownloadConfigs["Timeouts"]["Read"]

        if DownloadConfigs["UseGobalRequestsSession"]:
            UsedSession = self.RequestsSession
        else:
            UsedSession = getSession()

        File = BytesIO()
        if self.Stopping:
            raise Ex_Download.Stopping

        try:
            with UsedSession.get(URL, timeout=(ConnectTimeout, ReadTimeout,)) as Request:
                StatusCode = str(Request.status_code)
                if DownloadConfigs["ErrorByStatusCode"] and (StatusCode[0] in ["4", "5"]): Request.raise_for_status()
                while True:
                    Temp = Request.raw.read(1024)
                    if self.Stopping: raise Ex_Download.Stopping
                    if Temp == bytes(): break
                    File.write(Temp)
        except Ex_Requests.ConnectTimeout:
            raise Ex_Download.ConnectTimeout
        except Ex_Requests.ReadTimeout:
            raise Ex_Download.ReadTimeout
        except (
            Ex_Requests.MissingSchema,
            Ex_Requests.InvalidSchema
        ): raise Ex_Download.SchemaError
        except (
            Ex_Requests.ProxyError,
            Ex_Requests.HTTPError,
            Ex_Requests.SSLError,
            Ex_Requests.ConnectionError
        ): raise Ex_Download.DownloadExceptions

        if ((Size != None) and (len(File.getbuffer())) != Size): raise Ex_Download.SizeError
        if ((Sha1 != None) and (sha1(File.getbuffer()).hexdigest() != Sha1)): raise Ex_Download.HashError

        dfCheck(Path=OutputPaths, Type="fm")
        saveFile(Path=OutputPaths, FileContent=File.getbuffer(), Type="bytes")


    def addTask(self, InputTasks: list[DownloadTask] | DownloadTask, MainProjectID: int | None = None) -> int:
        """添加任务至 Project, 不指定 ProjectID 则新建 Project 对象后返回对应的 ProjectID"""
        # 如果正在添加任务则不等待添加完成
        if self.Stopping == True:
            raise Ex_Download.Stopping
        while self.Adding:
            if self.Stopping == True:
                raise Ex_Download.Stopping
            sleep(DownloadConfigs["SleepTime"])
        self.Adding = True

        if isinstance(InputTasks, DownloadTask):
            InputTasks = [InputTasks]
            JobTotal = 1
        else:
            JobTotal = len(InputTasks)

        if MainProjectID == None:
            MainProjectID = self.createProject(AllTasksCount=JobTotal)
        else:
            self.addJobToProject(ProjectID=MainProjectID, AllTasksCount=JobTotal)
        Logger.debug("Adding %s tasks to Project %s", JobTotal, MainProjectID)

        for InputTask in InputTasks:
            InputTask.ProjectID = MainProjectID
            self.DownloadsTasks.append(self.ThreadPool.submit(self.Download, Task=InputTask))

        self.Adding = False
        Logger.info("Added %s tasks to Project %s", JobTotal, MainProjectID)
        return(MainProjectID)


    def stop(self) -> None:
        """停止可停止的一切 Project 对象"""
        self.Stopping = True
        CantCancelled, BeingCancelled, Cancelled = int(), int(), int()
        for Task in self.DownloadsTasks:
            if Task.done(): pass
            elif Task.running(): CantCancelled += 1
            elif Task.cancel(): BeingCancelled += 1
            elif Task.cancelled(): Cancelled += 1

        if CantCancelled != 0:
            Logger.warning("%s task cannot be cancelled, %s task is being cancelled, %s task cancelled", CantCancelled, BeingCancelled, Cancelled)
        else:
            Logger.info("0 task cannot be cancelled, %s task is being cancelled, %s task cancelled", BeingCancelled, Cancelled)

        self.ThreadPool.shutdown(wait=False)


    def createProject(self, AllTasksCount: int = 0, setProjectID: int | None = None) -> int:
        """建立 Project 对象"""
        if setProjectID == None:
            while True:
                NewProjectID = randint(1,4096)
                if not (NewProjectID in self.Projects.keys()):
                    break
        else:
            if setProjectID in self.Projects.keys():
                raise ValueError(setProjectID)
            else:
                NewProjectID = setProjectID
        self.Projects[NewProjectID] = {"CompletedTasksCount": 0, "AllTasksCount": AllTasksCount, "FailuredTasksCount": 0, "ErrorTasksCount": 0}
        Logger.info("Created New Project %s", NewProjectID)
        return(NewProjectID)


    def deleteProject(self, ProjectID: int):
        """删除 Project 对象"""
        del(self.Projects[ProjectID])


    def addJobToProject(self, ProjectID: int, AllTasksCount: int | None = None, CompletedTasksCount: int | None = None, FailuredTasksCount: int | None = None, ErrorTasksCount: int | None = None) -> None:
        """向 Project 对象添加任务"""
        if AllTasksCount != None:       self.Projects[ProjectID]["AllTasksCount"] += AllTasksCount
        if CompletedTasksCount != None: self.Projects[ProjectID]["CompletedTasksCount"] += CompletedTasksCount
        if FailuredTasksCount != None:  self.Projects[ProjectID]["FailuredTasksCount"] += FailuredTasksCount
        if ErrorTasksCount != None:     self.Projects[ProjectID]["ErrorTasksCount"] += ErrorTasksCount


    def waitProject(self, ProjectIDs: list | int, Raise: Exception | None = None) -> int:
        """通过 ProjectID 的列表阻塞线程, 阻塞结束后返回总错误计数"""
        if isinstance(ProjectIDs, int): ProjectIDs = [ProjectIDs]
        ErrorTasksCount = int()
        for ProjectID in ProjectIDs:
            while not self.isProjectCompleted(ProjectID=ProjectID):
                sleep(DownloadConfigs["SleepTime"])
            ErrorTasksCount += self.Projects[ProjectID]["ErrorTasksCount"]

        if len(ProjectIDs) > 1:
            Logger.debug("Waited Projects %s completed by %s Errors", ProjectIDs, ErrorTasksCount)
        else:
            Logger.debug("Waited Project \"%s\" completed by %s Errors", ProjectIDs[0], ErrorTasksCount)

        if ((Raise != None) and (ErrorTasksCount > 0)):
            raise Raise(ErrorTasksCount)
        else:
            return(ErrorTasksCount)


    def isProjectCompleted(self, ProjectID: int) -> bool:
        """检查此 Project 是否已完成"""
        if self.Projects[ProjectID]["CompletedTasksCount"] + self.Projects[ProjectID]["ErrorTasksCount"] == self.Projects[ProjectID]["AllTasksCount"]:
            return(True)
        else:
            return(False)

