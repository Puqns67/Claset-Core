# -*- coding: utf-8 -*-

from logging import getLogger
from time import sleep, time, strptime, mktime
from uuid import UUID

from Claset.Utils import getSession

from .AccountAPIURLSets import *

from .Exceptions import MicrosoftOAuthDeclined, MicrosoftOAuthTimeOut

__all__ = ("MicrosoftAuthAPI", "MinecraftAccountAPI",)
Logger = getLogger(__name__)


class MicrosoftAuthAPI():
    """提供正版验证功能"""
    def __init__(self, MicrosoftAccountRefreshToken: str | None = None):
        self.RequestsSession = getSession()

        self.MicrosoftAccountRefreshToken = MicrosoftAccountRefreshToken


    def auth(self):
        NewRequestReturned: dict = self.RequestsSession.post(
            url=MICROSOFT_DEVICE_CODE_URL,
            data={"client_id": CLASET_CLIENT_ID, "scope": CLASET_SCOPE}
            ).json()
        Logger.warning(NewRequestReturned["message"])

        while True:
            sleep(NewRequestReturned["interval"])

            CheckRequestReturned = self.RequestsSession.post(
                url=MICROSOFT_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"},
                data={
                    "client_id": CLASET_CLIENT_ID,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "device_code": NewRequestReturned["device_code"]
                }
            ).json()

            match CheckRequestReturned.get("error"):
                case "authorization_pending": continue
                case "authorization_declined": raise MicrosoftOAuthDeclined
                case "expired_token": raise MicrosoftOAuthTimeOut
                case None: break
                case _: raise ValueError(CheckRequestReturned.get("error"), CheckRequestReturned.get("error_description"))

        self.MicrosoftAccountAccessToken = CheckRequestReturned["access_token"]
        self.MicrosoftAccountRefreshToken = CheckRequestReturned["refresh_token"]
        self.MicrosoftAccountAccessTokenExpiresTime = CheckRequestReturned["expires_in"] + int(time()) - 5
        Logger.info("Logging success!")


    def refresh(self, MicrosoftAccountRefreshToken: str | None = None):
        """刷新微软账户的访问 Token 与 刷新 Token"""
        if MicrosoftAccountRefreshToken is None:
            if self.MicrosoftAccountRefreshToken is None: raise ValueError
            MicrosoftAccountRefreshToken = self.MicrosoftAccountRefreshToken

        self.MicrosoftAccountAccessToken, self.MicrosoftAccountRefreshToken, self.MicrosoftAccountAccessTokenExpiresTime = self.refreshAccessTokens(MicrosoftAccountRefreshToken)


    def refreshAccessTokens(self, MicrosoftAccountRefreshToken: str | None = None) -> tuple[str, str, str]:
        """刷新微软账户的访问 Token 与 刷新 Token 并返回"""
        if MicrosoftAccountRefreshToken is None:
            RefreshToken = self.MicrosoftAccountRefreshToken
        else:
            RefreshToken = MicrosoftAccountRefreshToken

        Logger.info("Refresh Microsoft Account access token from: %s", RefreshToken)

        RefreshRequestReturned = self.RequestsSession.post(
            url=MICROSOFT_TOKEN_URL,
            data={
                "client_id": CLASET_CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": RefreshToken
            }
        ).json()

        return((
            RefreshRequestReturned["access_token"],
            RefreshRequestReturned["refresh_token"],
            RefreshRequestReturned["expires_in"] + int(time()) - 5
        ))


    def authToMinectaft(self) -> None:
        """登录至 Minecraft, 需先获取 Microsoft Account 的 Access Token"""
        self.getToken_XBoxLive()
        self.getToken_XBoxXSTS()
        self.getToken_Minecreaft()


    def getToken_XBoxLive(self) -> None:
        """获取来自 XBox Live 的 Token, 需先获取 Microsoft Account 的 Access Token"""
        XboxLiveReturned = self.RequestsSession.post(
            url=XBOX_LIVE_AUTH_URL,
            headers={"content-type": "application/json", "charset": "UTF-8"},
            json={
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT",
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": f"d={self.MicrosoftAccountAccessToken}"
                }
            }
        ).json()

        self.XboxLiveToken = XboxLiveReturned["Token"]
        self.XboxLiveTokenExpiresTime = mktime(strptime(XboxLiveReturned["NotAfter"][:26], "%Y-%m-%dT%H:%M:%S.%f")) - 5
        self.XboxLiveUserHash = XboxLiveReturned["DisplayClaims"]["xui"][0]["uhs"]


    def getToken_XBoxXSTS(self) -> None:
        """获取来自 XBox XSTS 的 Token, 需先获取 XBox Live 的 Access Token"""
        XboxXstsReturned = self.RequestsSession.post(
            url=XBOX_XSTS_AUTH_URL,
            headers={"content-type": "application/json", "charset": "UTF-8"},
            json={
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT",
                "Properties": {
                    "SandboxId": "RETAIL",
                    "UserTokens": [self.XboxLiveToken]
                }
            }
        ).json()

        self.XboxXstsToken = XboxXstsReturned["Token"]
        self.XboxXstsTokenExpiresTime = mktime(strptime(XboxXstsReturned["NotAfter"][:26], "%Y-%m-%dT%H:%M:%S.%f")) - 5
        self.XboxXstsUserHash = XboxXstsReturned["DisplayClaims"]["xui"][0]["uhs"]


    def getToken_Minecreaft(self) -> None:
        """获取来自 Mojang 的 Minecraft Access Token, 需先获取 XBox XSTS 的 Access Token"""
        MinecraftRespons = self.RequestsSession.post(
            url=MOJANG_AUTH_SERVICES_URL,
            headers={"content-type": "application/json", "charset": "UTF-8"},
            json={
                "identityToken": f"XBL3.0 x={self.XboxXstsUserHash};{self.XboxXstsToken}"
            }
        )

        MinecraftRespons.raise_for_status()
        MinecraftReturned = MinecraftRespons.json()
        self.MinecraftAccessToken = MinecraftReturned["access_token"]
        self.MinecraftAccessTokenExpiresTime = MinecraftReturned["expires_in"] + time() - 5


class MinecraftAccountAPI():
    """Minecraft 账户相关 API"""
    def __init__(self, MinecraftAccessToken: str):
        self.AccessToken = MinecraftAccessToken
        self.RequestsSession = getSession()
        self.UUID, self.Name, self.Skins, self.Capes = self.getAccountInfos()


    def getAccountInfos(self, MinecraftAccessToken: str | None = None) -> tuple[UUID, str, list, list]:
        """获取账户相关信息"""
        if MinecraftAccessToken is None:
            MinecraftAccessToken = self.AccessToken

        Infos = self.RequestsSession.get(
            url=MOJANG_PROFILE_URL,
            headers={"Authorization": "Bearer " + MinecraftAccessToken}
        ).json()

        return((UUID(Infos["id"]), Infos["name"], Infos["skins"], Infos["capes"],))

