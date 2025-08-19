"""Handles communitaction with the FRITZ!Box and connected home
automation devices."""

# AHA-HTTP Interface
from . import http
from .http import aha_request
from ._login import get_sid

# TR-064 Interface
from . import tr064


class FritzUser():
    
    def __init__(self, user, pwd, ip):
        self.user = user 
        self.pwd = pwd 
        self.ip = ip 

class FritzBoxConnection():

    def __init__(self, fritz_user):
        self.user = fritz_user.user
        self.pwd = fritz_user.pwd
        self.ip = fritz_user.ip
        self.update_sid()

    def update_sid(self):
        self.sid = get_sid(self.user, self.pwd, self.ip)
    

