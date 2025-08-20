"""Provides classes implementing features of speific types of 
home automation devices"""

from ..connection import tr064, http, FritzBoxSession, FritzUser
from ..utilities import bitmask, xml, is_stats_dict, prepare_stats_dict
from datetime import datetime, timedelta



class HomeAutoDevice():

    def __init__(self, ain:str, sid:str):
        self.sid = sid
        self.ain = ain
        self.switch_mode = None
        self._info_on_init = self._get_info()
    
    def __str__(self):
        return f"{self.name} ({self.model})"
    
    def _get_info(self):
        infos = http.getdeviceinfos(self.ain, self.sid)
        self.name = infos['name']
        self.model = f"{infos['manufacturer']} {infos['productname']}"
        self.device_id = infos['id']
        self.present = bool(int(infos['present']))
        functionbitmask = int(infos['functionbitmask'])
        functionbitmask = bitmask.decode(functionbitmask)
        self.is_switchable = functionbitmask[15]
        if self.is_switchable: 
            self.switch_mode = infos['switch']['mode']
        return infos
    
    def set_switch(self, state:bool)->bool:
        """Set switch state if switchable (on=True ,off=False)."""
        if self.is_switchable:
            response = http.setswitch(self.ain, self.sid, int(state))
            state = int(response.text.strip())
            return bool(state)
        
    def toggle_switch(self)->bool:
        """Toggle switch state if switchable."""
        if self.is_switchable:
            response = http.setswitch(self.ain, self.sid, 2)
            state = int(response.text.strip())
            return bool(state)
    
    # TODO implement 
    # def get_basic_device_stats(self):
    #     stats = http.getbasicdevicestats(self.ain, self.sid)
    #     for key in stats:
    #         stat = stats[key]['stats']
    #         if type(stat) == dict:
    #             stats[key]['stats'] = xml.prepare_stats_dict(stat)
    #         else:
    #             for idx, sta in enumerate(stat):
    #                 stats[key]['stats'][idx] = xml.prepare_stats_dict(sta)
    #     return stats

    def get_basic_device_stats(self):
        """Get statisticts (temperature, energy, power, ...) recorded 
        by device."""
        # get statistics via AHA-HTTP interface for processing
        stats_raw = http.getbasicdevicestats(self.ain, self.sid)
        # process statistics
        stats_processed = {}
        for quantity, data in stats_raw.items():
            stats = data['stats']
            if is_stats_dict(stats):
                stats = prepare_stats_dict(stats)
                stats_processed[quantity] = stats
            elif type(stats) == list:
                for idx, item in enumerate(stats):
                    if is_stats_dict(item):
                        item = prepare_stats_dict(item)
                        stats_processed[f"{quantity}_{idx+1}"] = item
        return stats_processed


    def get_power_measurements(self):
        stats = self.get_basic_device_stats()
        return stats['power']

    def get_latest_power_record(self):
        start = datetime.now()
        power_stats = self.get_power_measurements()
        end = datetime.now()
        datatime:datetime = power_stats['datatime']
        duration = (end - start).total_seconds()
        latency = (end - datatime).total_seconds()
        offset = (datatime - start).total_seconds() 
        power = power_stats['data'][0] / 100
        power_record = {
            'power':power,
            'datatime':datatime,
            'starttime':start,
            'endtime':end,
            'duration':duration,
            'latency':latency,
            'offset':offset,
        }
        return power_record

# TODO Figure out how to write this
class StatsMonitor:

    def __init__(self):
        self.grid:int
        self.basetime:datetime
        self.offset:timedelta
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def adjust(self, power_record):
        self.basetime = power_record['datatime']
        pass


class HomeAutoSystem():

    def __init__(self, user:FritzUser):
        self.session = FritzBoxSession(user)
        self.devices = self.get_devices()
    
    def get_devices(self):
        sid = self.session.sid
        ains = self.session.ains
        devices = [HomeAutoDevice(ain, sid) for ain in ains]
        return devices
