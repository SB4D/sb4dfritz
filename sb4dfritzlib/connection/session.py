from . import ahahttp
from ._login import get_sid, check_sid_validity

import threading
from threading import Thread
from time import sleep


class FritzBoxSession():

    def __init__(self, user, pwd, ip):
        # extract login data
        self.user = user
        self.pwd = pwd
        self.ip = ip
        # get initial sid
        self.sid = self.get_sid()
        # run daemon thread to keep valid sid
        self.sid_manager = Thread(
            name="sb4dfritz SID manager", 
            target=self.__sid_updater__,
            daemon=True
        )
        self.sid_manager.start()
        # get device info
        self.ains = self.get_ains()
        # self.switches = ahahttp.getswitchlist(self.sid)

    def get_sid(self):
        """Obtains a valid session id (sid) using the FRITZ!Box
        login procedure."""
        return get_sid(self.user, self.pwd, self.ip)
    
    def update_sid(self):
        """Checks if the current SID is valid and gets a new one
        if needed."""
        sid = self.sid 
        all_good = bool(sid) and check_sid_validity(sid)
        if not all_good:
            new_sid = self.get_sid()
            self.sid = new_sid
    
    def __sid_updater__(self, minutes=15):
        """
        Infinite loop that checks the current SID and updates it
        if needed periodically. Note: SIDs expire automatically after
        20 minutes of inactivity.
        
        Args:
        - minutes : Time between updates in minutes (default: 15)
        """
        while True:
            sleep(minutes * 60)
            self.update_sid()

    def get_ains(self):
        devices = ahahttp.getdevicelistinfos(self.sid)
        ains = [dev['identifier'].replace(" ", "") for dev in devices]
        return ains
    

