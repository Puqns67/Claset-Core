# -*- coding: utf-8 -*-

from enum import Enum, auto
from subprocess import Popen
from typing import Iterable

from .Exceptions import UndefinedInstanceStatus, InstanceStatusError

__all__ = ("InstanceStatus", "InstanceBase")


class InstanceStatus(Enum):
    UnRunning = auto()
    Stopped = auto()
    Starting = auto()
    Running = auto()


class InstanceBase:
    """实例基类"""

    Instance: Popen | None = None

    def waitInstance(self) -> None:
        """等待实例结束(阻塞线程至实例结束)"""
        if self.checkStatus(InstanceStatus.Running):
            self.Instance.wait()

    def stopInstance(self) -> None:
        """向实例进程发送 "停止" 命令"""
        if self.checkStatus(InstanceStatus.Running):
            self.Instance.terminate()
            self.updateStatus()

    def killInstance(self) -> None:
        """向实例进程发送 "杀死" 命令"""
        if self.checkStatus(InstanceStatus.Running):
            self.Instance.kill()
            self.updateStatus()

    def setStatus(self, Status: InstanceStatus) -> None:
        """设置实例状态"""
        if Status in InstanceStatus:
            self.Status = Status
        else:
            raise UndefinedInstanceStatus(Status)

    def getStatus(self, Update: bool = True) -> InstanceStatus:
        """获取当前实例状态"""
        if Update:
            self.updateStatus()
        return self.Status

    def updateStatus(self) -> None:
        """更新实例状态"""
        if self.Instance.poll() is None:
            self.setStatus(InstanceStatus.Running)
        else:
            self.setStatus(InstanceStatus.Stopped)

    def checkStatus(
        self,
        Status: Iterable[InstanceStatus] | InstanceStatus,
        Reverse: bool = False,
        Raise: Exception | None = None,
    ) -> bool:
        """检查实例状态"""
        if isinstance(Status, InstanceStatus):
            Status = (Status,)

        # 检查状态是否存在
        for OneStatus in Status:
            if OneStatus not in InstanceStatus:
                raise UndefinedInstanceStatus(OneStatus)

        if self.getStatus(Update=False) in Status:
            if not Reverse:
                return True
        else:
            if Reverse:
                return True

        if Raise:
            if issubclass(Raise, Exception):
                raise Raise
            else:
                raise InstanceStatusError(Raise)
        else:
            return False
