# -*- coding: utf-8 -*-

from logging import getLogger
from uuid import UUID

from Claset.Utils import getSession

Logger = getLogger()

class MinecraftAccount():
    def __init__(self, MinecraftAccessToken: str):
        self.AccessToken = MinecraftAccessToken
        self.RequestsSession = getSession()
        self.UUID, self.Name, self.Skins, self.Capes = self.getAccountInfos()


    def getAccountInfos(self, MinecraftAccessToken: str | None = None) -> tuple[UUID, str, list, list]:
        if MinecraftAccessToken == None:
            MinecraftAccessToken = self.AccessToken

        Infos = self.RequestsSession.get(
            url="https://api.minecraftservices.com/minecraft/profile",
            headers={"Authorization": "Bearer " + MinecraftAccessToken}
        ).json()

        return((UUID(Infos["id"]), Infos["name"], Infos["skins"], Infos["capes"],))


    def DownloadSkins():
        pass

