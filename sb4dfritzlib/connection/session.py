from . import http
from ._login import get_sid

class FritzUser():
    
    def __init__(self, user, pwd, ip):
        self.user = user 
        self.pwd = pwd 
        self.ip = ip 

class FritzBoxSession():

    def __init__(self, fritz_user):
        self.user = fritz_user.user
        self.pwd = fritz_user.pwd
        self.ip = fritz_user.ip
        self.sid = self.update_sid()
        self.ains = self.get_ains()
        self.switches = http.getswitchlist(self.sid)

    def update_sid(self):
        return get_sid(self.user, self.pwd, self.ip)
    
    def get_ains(self):
        devices = http.getdevicelistinfos(self.sid)
        ains = [dev['identifier'].replace(" ", "") for dev in devices]
        return ains
    

