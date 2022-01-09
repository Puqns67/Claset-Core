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

    def __init__(self):
        self.RequestsSession = Session()
        self.RequestsSession.trust_env = False
        self.RequestsSession.headers = {"Content-Type": "application/x-www-form-urlencoded"}


    def auth(self):
        self.Access_Token, self.RefreshToken = self.getMicrosoftTokens()


    def refresh(self, RefreshToken):
        self.RefreshToken = RefreshToken
        Params = {
            "client_id": self.CLASET_CLIENT_ID,
            "scope": self.CLASET_SCOPE
        }
        RefreshRequestReturned: dict = self.RequestsSession.get(url=self.MICROSOFT_TOKEN_URL, params=Params).json()


    def getMicrosoftTokens(self) -> tuple[str]:
        ParamsOne = {"client_id": self.CLASET_CLIENT_ID, "scope": self.CLASET_SCOPE}
        NewRequestReturned: dict = self.RequestsSession.get(url=self.MICROSOFT_DEVICE_CODE_URL, params=ParamsOne).json()
        Logger.info(NewRequestReturned["message"])

        ParamsTwo = {
            "client_id": self.CLASET_CLIENT_ID,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "code": NewRequestReturned["device_code"]
        }

        while True:
            sleep(NewRequestReturned["interval"])
            CheckRequestReturned = self.RequestsSession.post(url=self.MICROSOFT_TOKEN_URL, params=ParamsTwo)
            match CheckRequestReturned.json().get("error"):
                case "authorization_pending": continue
                case "authorization_declined": raise MicrosoftOAuthDeclined
                case "expired_token": raise MicrosoftOAuthTimeOut
                case None: break
                case _: raise ValueError(CheckRequestReturned.json().get("error"), CheckRequestReturned.json().get("error_description"))

        return((CheckRequestReturned["access_token"], CheckRequestReturned["refresh_token"],))

