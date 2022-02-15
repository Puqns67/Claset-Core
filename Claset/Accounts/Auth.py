# -*- coding: utf-8 -*-

from logging import getLogger
from time import sleep, time

from Claset.Utils import getSession

from .Exceptions import MicrosoftOAuthDeclined, MicrosoftOAuthTimeOut

CLASET_CLIENT_ID = "baadb158-b1d7-424d-b2cd-a5957c70348a"
CLASET_SCOPE = "XboxLive.signin offline_access"
MICROSOFT_TENANT = "consumers"
MICROSOFT_DEVICE_CODE_URL = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/devicecode"
MICROSOFT_TOKEN_URL = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/token"
XBOX_LIVE_AUTH_URL = "https://user.auth.xboxlive.com/user/authenticate"
XBOX_XSTS_AUTH_URL = "https://xsts.auth.xboxlive.com/xsts/authorize"
MINECRAFT_AUTH_SERVICES_URL = "https://api.minecraftservices.com/authentication/login_with_xbox"
Logger = getLogger(__name__)


class Auth():
    def __init__(self, MicrosoftAccountRefreshToken: str | None = None):
        self.RequestsSession = getSession()

        self.MicrosoftAccountRefreshToken = MicrosoftAccountRefreshToken


    def auth(self):
        NewRequestReturned: dict = self.RequestsSession.post(
            url=MICROSOFT_DEVICE_CODE_URL,
            data={"client_id": CLASET_CLIENT_ID, "scope": CLASET_SCOPE}
            ).json()
        Logger.info(NewRequestReturned["message"])

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


    def refresh(self, MicrosoftAccountRefreshToken: str | None = None):
        if MicrosoftAccountRefreshToken == None:
            if self.MicrosoftAccountRefreshToken == None: raise ValueError
            MicrosoftAccountRefreshToken = self.MicrosoftAccountRefreshToken

        self.MicrosoftAccountAccessToken, self.MicrosoftAccountRefreshToken = self.refreshAccessTokens()


    def refreshAccessTokens(self, MicrosoftAccountRefreshToken: str | None = None) -> tuple[str, str]:
        if MicrosoftAccountRefreshToken == None:
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

        return((RefreshRequestReturned["access_token"], RefreshRequestReturned["refresh_token"],))


    def authToMinectaft(self) -> None:
        """登录至 Minecraft, 需先获取 Microsoft Account 的 Access Token"""
        self.getToken_XBoxLive()
        self.getToken_XBoxXSTS()
        self.getToken_Minecreaft()


    def getToken_XBoxLive(self) -> None:
        """获取来自 XBox Live 的 Token, 需先获取 Microsoft Account 的 Access Token"""
        XboxReturned = self.RequestsSession.post(
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

        self.XboxLiveToken = XboxReturned["Token"]


    def getToken_XBoxXSTS(self) -> None:
        """获取来自 XBox XSTS 的 Token, 需先获取 XBox Live 的 Access Token"""
        MinecraftXstsReturned = self.RequestsSession.post(
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

        self.XboxXstsToken = MinecraftXstsReturned["Token"]
        self.XboxXstsUserHash = MinecraftXstsReturned["DisplayClaims"]["xui"][0]["uhs"]


    def getToken_Minecreaft(self) -> None:
        """获取来自 Mojang 的 Minecraft Access Token, 需先获取 XBox XSTS 的 Access Token"""
        MinecraftRespons = self.RequestsSession.post(
            url=MINECRAFT_AUTH_SERVICES_URL,
            headers={"content-type": "application/json", "charset": "UTF-8"},
            json={
                "identityToken": f"XBL3.0 x={self.XboxXstsUserHash};{self.XboxXstsToken}"
            }
        )

        MinecraftRespons.raise_for_status()
        MinecraftReturned = MinecraftRespons.json()
        self.MinecraftAccessToken = MinecraftReturned["access_token"]
        self.MinecraftAccessTokenExpiresAt = int(time()) + MinecraftReturned["expires_in"]

