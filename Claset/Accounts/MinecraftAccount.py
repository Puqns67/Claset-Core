# -*- coding: utf-8 -*-

from logging import getLogger
from uuid import UUID

from Claset.Utils import getSession

Logger = getLogger(__name__)


class MinecraftAccount():
    """Minecraft 账户相关"""
    def __init__(self, MinecraftAccessToken: str):
        self.AccessToken = MinecraftAccessToken
        self.RequestsSession = getSession()
        self.UUID, self.Name, self.Skins, self.Capes = self.getAccountInfos()


    def getAccountInfos(self, MinecraftAccessToken: str | None = None) -> tuple[UUID, str, list, list]:
        """获取账户相关信息"""
        if MinecraftAccessToken is None:
            MinecraftAccessToken = self.AccessToken

        Infos = self.RequestsSession.get(
            url="https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": "Bearer " + MinecraftAccessToken}
        ).json()

        return((UUID(Infos["id"]), Infos["name"], Infos["skins"], Infos["capes"],))


    def DownloadSkins():
        """下载此账户的皮肤"""

