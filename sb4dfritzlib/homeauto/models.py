"""Provides classes implementing features of speific types of 
home automation devices"""

# from ..connection import ahahttp, tr064, FritzBoxSession, FritzUser
from ..connection.session import FritzUser, FritzBoxSession
from ..connection import ahahttp 
from ..utilities import bitmask, xml, is_stats_dict, prepare_stats_dict
from datetime import datetime, timedelta


#TODO: add alternative initialization within `HomeAutoSystem`
#TODO: add stats monitor
class HomeAutoDevice():

    def __init__(self, ain:str, sid:str):
        self.sid = sid
        self.ain = ain
        self.switch_mode = None
        self._info_on_init = self._get_info()
    
    def __str__(self):
        return f"{self.name} ({self.model})"
    
    def _get_info(self):
        infos = ahahttp.getdeviceinfos(self.ain, self.sid)
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
    
    def get_switch_state(self)->bool:
        """Get current switch state (on=True ,off=False)."""
        if self.is_switchable:
            state = ahahttp.getswitchstate(self.ain, self.sid)
            return bool(state)


    def set_switch(self, state:bool)->bool:
        """Set switch state if switchable (on=True ,off=False)."""
        if self.is_switchable:
            new_state = ahahttp.setswitch(self.ain, self.sid, int(state))
            return bool(new_state)
        
    def toggle_switch(self)->bool:
        """Toggle switch state if switchable."""
        if self.is_switchable:
            response = ahahttp.setswitch(self.ain, self.sid, 2)
            state = int(response.text.strip())
            return bool(state)
    
    #TODO: add logging feature
    #TODO: add timer?
    #TODO: better width option for console out?
    def switch_off_when_idle(
            self, 
            power_threshold:float=5,
            network_threshold:float=0.9,
            idle_cycles:int=2,
            status_messages:str=None,
            log_file:str=None,
            debug_mode:bool=False
            )->None:
        """Monitors the power consumption and waits for the appliances to be 
        *idle* before switching off. Here *idle* means that power values and
        request durations are reported within specified bounds (the arguments
        `power_threshold`, `network_threshold`) for a specified number of 
        measurement cycles (`idle_cycles`). 
        
        Includes options for status message output and logging.
        
        ARGUMENTS:
        - power_threshold : power consumption in idle state (in Watts)
        - network_threshold : tolerated request duration (in seconds)
        - idle_cycles : number of idle measurement cycles required
        - status_messages : target for status message output
        - log_file : path of log file
        - debug_mode : if True, the switch state is not changed
        """
        # width for console output
        WIDTH = 80
        # function to handle status messages
        def status_update(*args, output_target=status_messages):
            # available targets and their output functions
            OUTPUT_TARGETS = {
                'console' : print,
            }
            # check if `target` is admissable
            if output_target in OUTPUT_TARGETS:
                # get updater function for `target` 
                updater = OUTPUT_TARGETS[output_target]
                # run it on text
                updater(*args)
        # TODO add logging feature
        def log_data(data, log_file=log_file):
            pass

        # start main routine
        status_update(f'Switching off "{self.name}" when idle...\n')
        # check if switch is on
        switch_is_on = self.get_switch_state()
        if not switch_is_on:
            status_update("Switch is already off. Nothing to do.")
            return
        # start monitoring power consumption
        status_update("Monitoring power consumption..." + "\n" + "-" * WIDTH)
        # get initial power measurement (and wake up device)
        power_monitor = [self.get_latest_power_record()]
        while switch_is_on:
            # get the latest power measurement
            data = self.get_latest_power_record()
            # add to power_monitor if 'datatime' jumps
            if data['datatime'] != power_monitor[-1]['datatime']:
                power_monitor.append(data)
                log_data(data)
                status_update(
                    "Request Duration: {:5.2f} s | Power: {:7.2f} W | Latency: {:5.2f} s".format(
                        data['duration'], 
                        data['power'], 
                        data['latency'], 
                    )
                )
            # check the last measurements for idle status
            # NOTE: the very first measurement might be unreliable
            if len(power_monitor) > idle_cycles:
                last_measurements = power_monitor[-idle_cycles:]
                last_power_vals = [data['power'] for data in last_measurements]
                last_durations = [data['duration'] for data in last_measurements]
                last_latencies = [data['latency'] for data in last_measurements]
                appliances_are_idle = \
                    max(last_power_vals) < power_threshold and \
                    max(last_durations) < network_threshold
                if appliances_are_idle:
                    status_update(
                        "-" * WIDTH + "\n" + "Idle state detected. Switching off..."
                    )
                    if debug_mode:
                        switch_is_on = False
                    else:
                        switch_is_on = self.set_switch(False)
    
    def get_basic_device_stats(self):
        """Get statisticts (temperature, energy, power, ...) recorded 
        by device."""
        # get statistics via AHA-HTTP interface for processing
        stats_raw = ahahttp.getbasicdevicestats(self.ain, self.sid)
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


#TODO: improve initialization (takes too long)
class HomeAutoSystem():

    def __init__(self, user:FritzUser):
        self.session = FritzBoxSession(user)
        self.devices = self.get_devices()
    
    def get_devices(self):
        sid = self.session.sid
        ains = self.session.ains
        devices = [HomeAutoDevice(ain, sid) for ain in ains]
        return devices
