# -*- coding: utf-8 -*-

from logging import getLogger
from requests import Session
from time import sleep

from .Exceptions import MicrosoftOAuthDeclined, MicrosoftOAuthTimeOut

Logger = getLogger(__name__)


class MicrosoftOAuth():
    CLASET_CLIENT_ID = "baadb158-b1d7-424d-b2cd-a5957c70348a"
    CLASET_SCOPE = "XboxLive.signin offline_access"
    MICROSOFT_TENANT = "consumers"
    MICROSOFT_DEVICE_CODE_URL = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/devicecode"
    MICROSOFT_TOKEN_URL = f"https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/token"

    def __init__(self, RefreshToken: str | None = None):
        self.RequestsSession = Session()
        self.RequestsSession.trust_env = False
        self.RequestsSession.headers = {"Content-Type": "application/x-www-form-urlencoded", "charset": "UTF-8"}

        self.RefreshToken = RefreshToken


    def auth(self):
        self.AccessToken, self.RefreshToken = self.getTokens()


    def refresh(self):
        if self.RefreshToken == None: raise ValueError
        self.AccessToken, self.RefreshToken = self.refreshAccessTokens()


    def getTokens(self) -> tuple[str, str]:
        ParamsOne = {"client_id": self.CLASET_CLIENT_ID, "scope": self.CLASET_SCOPE}
        NewRequestReturned: dict = self.RequestsSession.post(url=self.MICROSOFT_DEVICE_CODE_URL, data=ParamsOne).json()
        Logger.info(NewRequestReturned["message"])

        ParamsTwo = {
            "client_id": self.CLASET_CLIENT_ID,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": NewRequestReturned["device_code"]
        }

        while True:
            sleep(NewRequestReturned["interval"])
            CheckRequestReturned = self.RequestsSession.post(url=self.MICROSOFT_TOKEN_URL, data=ParamsTwo).json()
            match CheckRequestReturned.get("error"):
                case "authorization_pending": continue
                case "authorization_declined": raise MicrosoftOAuthDeclined
                case "expired_token": raise MicrosoftOAuthTimeOut
                case None: break
                case _: raise ValueError(CheckRequestReturned.get("error"), CheckRequestReturned.get("error_description"))

        return((CheckRequestReturned["access_token"], CheckRequestReturned["refresh_token"],))


    def refreshAccessTokens(self, RefreshToken: str | None = None) -> tuple[str, str]:
        if RefreshToken != None: self.RefreshToken = RefreshToken

        Params = {
            "client_id": self.CLASET_CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": self.RefreshToken
        }

        RefreshRequestReturned: dict = self.RequestsSession.post(url=self.MICROSOFT_TOKEN_URL, data=Params).json()
        if RefreshToken != None: self.AccessToken = RefreshRequestReturned["access_token"]
        return((RefreshRequestReturned["access_token"], RefreshRequestReturned["refresh_token"],))

