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

from requests import (
    __version__ as RequestsVersion, Session,
    exceptions as Ex_Requests, packages as requestsPackages
)
from urllib3 import __version__ as Urllib3Version

from .Configs import Configs
from .Exceptions import Download as Ex_Download
from .File import dfCheck, loadFile, saveFile
from .Path import path as Pathmd, pathAdder

Logger = getLogger(__name__)


class DownloadManager():
    """下载管理器"""
    DownloadsTasks = list()
    Projects = dict()
    Adding = False
    Stopping = False

    def __init__(self):
        self.Configs = Configs(ID="Download")

        # 线程池(ThreadPool)
        self.ThreadPool = ThreadPoolExecutor(max_workers=self.Configs["MaxThread"], thread_name_prefix="DownloadTask")

        # 定义全局 Requests Session
        if self.Configs["UseGobalRequestsSession"] == True:
            self.RequestsSession = self.setSession()

        Logger.debug("urllib3 Version: %s", Urllib3Version)
        Logger.debug("requests Version: %s", RequestsVersion)


    def setSession(self, TheSession: Session | None = None) -> Session:
        """设置/获取 Session"""
        if TheSession == None: TheSession = Session()

        TheSession.stream = True
        TheSession.headers = self.Configs['Headers']
        TheSession.trust_env = self.Configs["UseSystemProxy"]
        TheSession.verify = self.Configs["SSLVerify"]

        if self.Configs["SSLVerify"] == False:
            requestsPackages.urllib3.disable_warnings()

        if self.Configs["ProxyLink"] != None:
            TheSession.proxies = {"http": self.Configs["ProxyLink"], "https": self.Configs["ProxyLink"]}

            # 使用代理时将强制禁用 SSL 验证与使用系统代理
            requestsPackages.urllib3.disable_warnings()
            TheSession.verify = False
            TheSession.trust_env = False

        return(TheSession)


    def Download(self, Task: dict) -> dict:
        """简易下载器 (Download) 的代理运行器"""
        if not Task.get("ISFULL"):
            Task = self.fullTask(Task)

        if not "URL" in Task:
            raise Ex_Download.TaskMissingURL

        Retry = True
        while Retry:
            Retry = False
            Errored = False
            StopType = "Downloaded"
            try:
                self.download(
                    URL=Task["URL"],
                    OutputPaths=Task["OutputPaths"],
                    Size=Task["Size"],
                    Overwrite=Task["Overwrite"],
                    Sha1=Task["Sha1"],
                    ConnectTimeout=Task["ConnectTimeout"],
                    ReadTimeout=Task["ReadTimeout"]
                )
            # 错误处理
            except Ex_Download.Stopping:
                StopType = "Stopping"
            except Ex_Download.SizeError:
                Errored = True
                self.addJobToProject(Task["ProjectID"], FailuredTasksCount=1)
                Logger.warning("File \"%s\" Download failure, By SizeError, From \"%s\"", Task["FileName"], Task["URL"])
            except Ex_Download.FileExist:
                StopType = "FileExist"
            except Ex_Download.SchemaError:
                Errored = True
                self.addJobToProject(Task["ProjectID"], ErrorTasksCount=1)
                Logger.error("URL \"%s\" Formart Error", Task["URL"])
            except Ex_Download.HashError:
                Errored = True
                self.addJobToProject(Task["ProjectID"], FailuredTasksCount=1)
                Logger.warning("File \"%s\" hash verification failed", Task["FileName"])
            except Ex_Download.ReadTimeout:
                Errored = True
                self.addJobToProject(Task["ProjectID"], FailuredTasksCount=1)
                Logger.warning("File \"%s\" Download timeout,  From \"%s\"", Task["FileName"], Task["URL"])
            except Ex_Download.ConnectTimeout:
                Errored = True
                self.addJobToProject(Task["ProjectID"], FailuredTasksCount=1)
                Logger.warning("File \"%s\" Connect timeout, From \"%s\"", Task["FileName"], Task["URL"])
            except Ex_Download.DownloadExceptions:
                Errored = True
                self.addJobToProject(Task["ProjectID"], FailuredTasksCount=1)
                Logger.warning("File \"%s\" Download failure, By ConnectionError, From \"%s\"", Task["FileName"], Task["URL"])
            except Exception:
                Errored = True
                self.addJobToProject(Task["ProjectID"], FailuredTasksCount=1)
                Logger.warning("Unknown Error:", exc_info=True)

            if Errored == True:
                if Task["Retry"] > 0:
                    Task["Retry"] -= 1
                    Retry = True
                    continue
                else:
                    Logger.error("File \"%s\" Retry Count Max", Task["FileName"])
                    self.addJobToProject(Task["ProjectID"], ErrorTasksCount=1)
                    raise Ex_Download.DownloadExceptions
            else:
                self.addJobToProject(Task["ProjectID"], CompletedTasksCount=1)
                # 没有出现下载错误之后尝试执行 Task["Next"]
                if Task["Next"] != None:
                    try:
                        Task["Next"](Task)
                    except Exception:
                        Logger.warning("Next Error: ",exc_info=True)

                match StopType:
                    case "Downloaded": Logger.info("File \"%s\" Downloaded", Task["FileName"])
                    case "Stopping": pass
                    case "FileExist": Logger.info("File \"%s\" is Exist, Skipping", Task["FileName"])

                return(Task)


    def download(
        self,
        URL:            str, # 链接地址
        OutputPaths:    str, # 输出路径
        Size:           int, # 文件大小(字节)
        Overwrite:     bool, # 覆盖已有的文件
        Sha1:           str, # 使用sha1验证下载结果
        ConnectTimeout: int, # 连接超时(若为空则使用全局设置)
        ReadTimeout:    int  # 下载超时(若为空则使用全局设置)
        ) -> None:
        """简易下载器"""
        if ((Overwrite == False) and (Sha1 != None) and (dfCheck(Path=OutputPaths, Type="f") == True) and (sha1(loadFile(Path=OutputPaths, Type="bytes")).hexdigest() == Sha1)):
            raise Ex_Download.FileExist

        if self.Configs["UseGobalRequestsSession"] == True:
            UsedSession = self.RequestsSession
        else:
            UsedSession = self.setSession()

        File = BytesIO()
        if self.Stopping == True: raise Ex_Download.Stopping

        try:
            with UsedSession.get(URL, timeout=(ConnectTimeout, ReadTimeout,)) as Request:
                StatusCode = str(Request.status_code)
                if self.Configs["ErrorByStatusCode"] and (StatusCode[0] in ["4", "5"]): Request.raise_for_status()
                while True:
                    Temp = Request.raw.read(1024)
                    if self.Stopping == True: raise Ex_Download.Stopping
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


    def fullTask(self, Task: dict = dict()) -> dict:
        """完善 Task"""
        # 处理缺失的项目
        if "Size"           not in Task: Task["Size"]           = None
        if "ProjectID"      not in Task: Task["ProjectID"]      = None
        if "Overwrite"      not in Task: Task["Overwrite"]      = True
        if "Sha1"           not in Task: Task["Sha1"]           = None
        if "ConnectTimeout" not in Task: Task["ConnectTimeout"] = self.Configs["Timeouts"]["Connect"]
        if "ReadTimeout"    not in Task: Task["ReadTimeout"]    = self.Configs["Timeouts"]["Read"]
        if "Retry"          not in Task: Task["Retry"]          = self.Configs["Retry"]
        if "Next"           not in Task: Task["Next"]           = None

        if (("OutputPaths" not in Task) or (Task["OutputPaths"] == None) or (Task["OutputPaths"] == str())):
            # 如不存在 OutputPath 或 OutputPath 为空, 则使用当前位置
            if ((not "OutputPath" in Task) or ("OutputPath" == None)):
                Task["OutputPath"] = "$PREFIX"

            # 如不存在 FileName 则优先从 URL 中获取文件名, 若 FileName 为 None, 则优先从 OutPutPath 中获取文件名, 若都无法获取则使用 NoName
            if "FileName" not in Task:
                Task["FileName"] = baseName(Task["URL"])
                if Task["FileName"] == str():
                    Task["FileName"] = baseName(Task["OutputPath"])
            if Task["FileName"] == None:
                Task["FileName"] = baseName(Task["OutputPath"])
                if Task["FileName"] == str():
                    Task["FileName"] = baseName(Task["URL"])
            if Task["FileName"] == str():
                Task["FileName"] = "NoName"

            # 从 OutputPath 中去除重复的文件名
            if ((Task["FileName"] in Task["OutputPath"]) and ((search(Task["FileName"] + "$", Task["OutputPath"])) != None)):
                Task["OutputPath"] = search("^(.*)" + Task["FileName"] + "$", Task["OutputPath"]).groups()[0]

            Task["OutputPaths"] = pathAdder(Task["OutputPath"], Task["FileName"])
        else:
            try:
                Task["OutputPath"], Task["FileName"] = splitPath(Task["OutputPaths"])
            except Exception:
                raise Ex_Download.UnpackOutputPathsError

        # 解析 Paths
        if "$" in Task["URL"]:
            Task["URL"] = Pathmd(Task["URL"])
        if "$" in Task["OutputPaths"]:
            Task["OutputPaths"] = Pathmd(Task["OutputPaths"], IsPath=True)

        Task["ISFULL"] = True
        return(Task)


    def addTasks(self, InputTasks: list[dict], MainProjectID: int | None = None) -> int | None:
        """添加多个任务至 Project, 不指定 ProjectID 则新建 Project 对象后返回对应的 ProjectID"""
        # 如果正在添加任务则不等待添加完成
        while self.Adding:
            sleep(self.Configs["SleepTime"])
        self.Adding = True

        if self.Stopping == True: raise Ex_Download.Stopping
        JobTotal = len(InputTasks)
        if MainProjectID == None:
            InputProjectID = False
            MainProjectID = self.createProject(AllTasksCount=JobTotal)
        else:
            InputProjectID = True
            self.addJobToProject(ProjectID=MainProjectID, AllTasksCount=JobTotal)
        Logger.debug("Adding %s tasks to Project %s", JobTotal, MainProjectID)

        for InputTask in InputTasks:
            InputTask["ProjectID"] = MainProjectID
            InputTask["ListID"] = len(self.DownloadsTasks)
            self.DownloadsTasks.append(self.ThreadPool.submit(self.Download, Task=InputTask))

        self.Adding = False
        Logger.info("Added %s tasks to Project %s", JobTotal, MainProjectID)
        if InputProjectID == False: return(MainProjectID)


    def addTask(self, InputTask: dict, ProjectID: int | None = None) -> int | None:
        """添加单个 dict 任务对象至 Project, 不指定 ProjectID 则新建 Project 对象后返回对应的 ProjectID"""
        # 如果正在添加任务则不等待添加完成
        while self.Adding:
            sleep(self.Configs["SleepTime"])
        self.Adding = True

        if self.Stopping == True: raise Ex_Download.Stopping
        if ProjectID == None:
            InputedProjectID = False
            ProjectID = self.createProject(AllTasksCount=1)
        else:
            InputedProjectID = True
            self.addJobToProject(ProjectID=ProjectID, AllTasksCount=1)
        Logger.debug("Adding 1 tasks to Project %s", ProjectID)

        InputTask["ProjectID"] = ProjectID
        InputTask["ListID"] = len(self.DownloadsTasks)
        self.DownloadsTasks.append(self.ThreadPool.submit(self.Download, Task=InputTask))

        self.Adding = False
        Logger.info("Added 1 task to Project %s", ProjectID)

        if InputedProjectID == False:
            return(ProjectID)
        else:
            return(None)


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


    def waitProject(self, ProjectIDs: int | list, Raise: Exception | None = None) -> int:
        """通过 ProjectID 的列表阻塞线程, 阻塞结束后返回总错误计数"""
        if type(ProjectIDs) == type(int()): ProjectIDs = [ProjectIDs]
        ErrorTasksCount = int()
        for ProjectID in ProjectIDs:
            while ((self.Projects[ProjectID]["CompletedTasksCount"] + self.Projects[ProjectID]["ErrorTasksCount"]) != self.Projects[ProjectID]["AllTasksCount"]):
                sleep(self.Configs["SleepTime"])
            ErrorTasksCount += self.Projects[ProjectID]["ErrorTasksCount"]

        if len(ProjectIDs) > 1:
            Logger.debug("Waited Projects %s completed by %s Errors", ProjectIDs, ErrorTasksCount)
        else:
            Logger.debug("Waited Project \"%s\" completed by %s Errors", ProjectIDs[0], ErrorTasksCount)

        if ((Raise != None) and (ErrorTasksCount > 0)):
            raise Raise(ErrorTasksCount)
        else:
            return(ErrorTasksCount)

