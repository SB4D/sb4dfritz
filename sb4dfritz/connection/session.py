import keyring
import requests

from .._config import SERVICE_NAME
from . import get_sid
from ..homeauto.aha import SwitchCmd
from ..homeauto.webui import WEB_UI_HEADERS


BASE_URL = 'http://fritz.box/'
AHA_API_URL = BASE_URL + 'webservices/homeautoswitch.lua'
WEB_UI_DATA_URL = BASE_URL + 'data.lua'


class FritzSession:

    def __init__(self):
        self.sid = None
        self.__cred = None
        self.load_credentials()
        self.get_new_sid()
    
    @property
    def user(self):
        cred = self.__cred
        return cred.username if cred else None
    @property
    def pwd(self):
        cred = self.__cred
        return cred.password if cred else None

    def load_credentials(self):
        self.__cred = keyring.get_credential(SERVICE_NAME, username=None)

    def ask_for_credentials(self):
        print("Login information needed")
        user = input("Username:")
        pwd = input("Password:")
        keyring.set_password(SERVICE_NAME, user, pwd)
        self.load_credentials()
    
    def delete_credentials(self):
        if self.user:
            keyring.delete_password(SERVICE_NAME, self.user)
    
    def get_new_sid(self):
        try:
            self.sid = get_sid(self.user, self.pwd)
        except Exception as e:
            print(e)
            self.delete_credentials()
            self.ask_for_credentials()
            self.get_new_sid()
    
    ###  AHA-HTTP Interface  ###
    def aha_request(self, params:dict):
        params['sid'] = self.sid
        response = requests.get(AHA_API_URL, params)
        return response
    
    def aha_command(self, switchcmd:SwitchCmd, params:dict={}):
        # get default parameters for command
        full_params = switchcmd.value
        # set the provided parameters
        for key, val in params.items():
            full_params[key] = val
        # send the get request
        response = self.aha_request(full_params)
        # handle invalid session ID
        if response.status_code == 403:
            self.get_new_sid()
            self.aha_request(params)
        # handle parameter issues
        elif response.status_code == 400:
            raise Exception("Some parameter(s) are invalid or out of bounds")
        # handle server error
        elif response.status_code == 500:
            raise Exception("Server error")
        return response
    
    ### EXPERIMENTAL: requests to data.lua ###
    def web_ui_request(self, data, headers=WEB_UI_HEADERS):
        response = requests.post(WEB_UI_DATA_URL, headers=headers, data=data)
        # normal behavior
        if response.status_code == 200:
            return response
        # handle invalid session ID
        elif response.status_code() == 403:
            self.get_new_sid()
            self.web_ui_request(data, headers)
        else:
            raise Exception("Unknown error")
