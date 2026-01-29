"""Classes and functions related to home automation devices"""

from time import sleep
from datetime import datetime
import xml.etree.ElementTree as ET
import requests

from ..connection import FritzSession
from .aha import FunctionBitMask
from .aha import SwitchCmd
from ..utilities.xml import process_xml_stats
from .webui import WebUITemplate
from .webui import add_weekly_timer_data


class HomeAutoDevice:
    """Base class for home automation devices"""

    def __init__(self):
        self._session:FritzSession = None
        # device name and identifiers
        self.name:str = None
        self.ain:str|int = None
        self.id:int = None
        # product details
        self.manufacturer:str = None
        self.productname:str = None
        self.features:FunctionBitMask = None

    @property
    def sid(self):
        """Displays the current session ID"""
        return self._session.sid if self._session else None

    @classmethod
    def from_dict(cls, device_info:dict):
        """Create a HomeAutoDevice instance from a suitable dictionary"""
        device = HomeAutoDevice()
        # device name and identifiers
        device.name = device_info['name']
        device.ain = device_info['ain']
        device.id = device_info['id']
        # product details
        device.manufacturer = device_info['manufacturer']
        device.productname = device_info['productname']
        device.features = FunctionBitMask(device_info['functionbitmask'])
        return device

    ### AHA-HTTP INTERFACE ###
    def _execute_switchcmd(self, switchcmd:SwitchCmd, params:dict=None) -> requests.Response:
        # make sure a dictionary called 'params' exists
        params = params if params else {}
        # set device identifier
        params['ain'] = self.ain
        # send the HTTP request
        return self._session.aha_command(switchcmd, params)

    ## Feature Checks ##
    def is_switchable(self):
        """Check if the device has an on/off switch"""
        return self.features.switchable

    def has_heat_control(self):
        """Check if the device has a temperature control"""
        return self.features.temp_control

    ## Basic Stats ##
    def get_basic_device_stats(self):
        """Get statisticts (temperature, energy, power, ...) recorded 
        by device."""
        # get statistics via AHA-HTTP interface for processing
        response = self._execute_switchcmd(SwitchCmd.getbasicdevicestats)
        device_stats_xml = response.text
        device_stats = process_xml_stats(device_stats_xml)
        return device_stats

    ## Specific functions: electricity ##
    def get_switch_state(self)->bool:
        """Get current switch state (on=True ,off=False)."""
        if not self.features.switchable:
            return
        response = self._execute_switchcmd(SwitchCmd.getswitchstate)
        return bool(int(response.text.strip()))

    def get_switch_mode(self) -> str:
        """Get the current autoswitch mode"""
        if not self.is_switchable():
            return
        device_info_xml = self._execute_switchcmd(SwitchCmd.getdeviceinfos).text
        device_info_tree = ET.fromstring(device_info_xml)
        return device_info_tree.find('switch').find('mode').text

    def set_switch_state(self, state:bool) -> bool:
        """Change the switch state to on (True) or off (False)"""
        if not self.features.switchable:
            return
        params = {'onoff': 1 if state else 0}
        response = self._execute_switchcmd(SwitchCmd.setsimpleonoff, params)
        return bool(int(response.text.strip()))

    def switch_on(self) -> bool:
        """Switch the device on"""
        if not self.features.switchable:
            return
        response = self._execute_switchcmd(SwitchCmd.setswitchon)
        return bool(int(response.text.strip()))

    def switch_off(self) -> bool:
        """Switch the device off"""
        if not self.features.switchable:
            return
        response = self._execute_switchcmd(SwitchCmd.setswitchoff)
        return bool(int(response.text.strip()))

    def get_power(self) -> int:
        """Get current power consumption as a multiple of 0.1 W."""
        if not self.features.energy_sensor:
            return
        response = self._execute_switchcmd(SwitchCmd.getswitchpower)
        power = response.text.strip()
        power = int(power)
        return power

    def get_power_readout(self) -> float:
        """Get current power consumption in Watts."""
        stats = self.get_basic_device_stats()
        return stats['power']

    def get_timed_power_readout(self) -> dict:
        """Returns the current power consumption along with timing information."""
        if not self.features.energy_sensor:
            return
        start = datetime.now()
        power_stats = self.get_power_readout()
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
            'grid': power_stats['grid']
        }
        return power_record

    def switch_off_when_idle(
            self,
            power_threshold:float=5,
            network_threshold:float=0.95,
            idle_cycles:int=2,
            status_updater=None,
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
        - status_messenger : vesseltarget for status message output
        - log_file : path of log file
        - debug_mode : if True, the switch state is not changed
        """
        def status_update(message:str):
            if status_updater:
                status_updater(message)
            else:
                pass
        # check if switch is on
        switch_is_on = self.get_switch_state()
        if not switch_is_on:
            status_update(f"{self.name} is off")
            return switch_is_on
        status_update(f"Switching off {self.name} when idle... (this may take a while)")
        # start monitoring power consumption
        status_update(f"Monitoring power consumption of {self.name}:")
        # get initial power measurement (and wake up device)
        initial_power = self.get_timed_power_readout()
        #TODO tweak sleep time if needed
        sleep_time = initial_power['grid'] - 4
        power_monitor = [initial_power]
        while switch_is_on:
            # get the latest power measurement
            data = self.get_timed_power_readout()
            # debugging: priont data
            if debug_mode:
                print(data)
            # add to power_monitor if 'datatime' jumps
            if data['datatime'] != power_monitor[-1]['datatime']:
                time_string = data['endtime'].strftime('%X')
                status_update(f" -- Power: {data['power']:0.2f} W | Time: {time_string}")
                sleep(sleep_time)
                power_monitor.append(data)
            # check the last measurements for idle status
            # NOTE: the very first measurement might be unreliable
            if len(power_monitor) > idle_cycles:
                last_measurements = power_monitor[-idle_cycles:]
                last_power_vals = [data['power'] for data in last_measurements]
                last_durations = [data['duration'] for data in last_measurements]
                # last_latencies = [data['latency'] for data in last_measurements]
                appliances_are_idle = \
                    max(last_power_vals) < power_threshold and \
                    max(last_durations) < network_threshold
                if appliances_are_idle:
                    status_update(f"Switching off {self.name}")
                    if debug_mode:
                        switch_is_on = False
                    else:
                        switch_is_on = self.switch_off()
                    status_update(f"Done: {self.name} was switched off")
        # return power records for logging (discard first record)
        return switch_is_on
        # return power_monitor[1:]


    ## Specific functions: heating ##

    def get_temperature(self):
        """Get the currently measured temperature"""
        if not self.features.temp_sensor:
            return
        # get current temperature
        response = self._execute_switchcmd(SwitchCmd.gettemperature)
        return int(response.text) / 10

    #TODO review this and improve if needed
    def get_target_temperature(self):
        """Get the current target temperature"""
        if not self.features.temp_control:
            return
        response = self._execute_switchcmd(SwitchCmd.gethkrtsoll)
        temp = int(response.text)
        if temp in {254, 253}:
            return temp
        elif 16 <= temp <= 56:
            return temp / 2

    #TODO this is too clunky (too many requests, takes too long)
    def get_temperature_settings(self):
        """Get the current temperature settings (target, comfort, saving)"""
        if not self.features.temp_control:
            return
        # initialize temperature dictionary
        temperatures = {}
        # get target temperature
        response = self._execute_switchcmd(SwitchCmd.gethkrtsoll)
        temperatures['target'] = int(response.text) / 2
        # get "comfort" temperature
        response = self._execute_switchcmd(SwitchCmd.gethkrkomfort)
        temperatures['comfort'] = int(response.text) / 2
        # get "saving" temperature
        response = self._execute_switchcmd(SwitchCmd.gethkrabsenk)
        temperatures['saving'] = int(response.text) / 2
        return temperatures

    def set_temperature(self, temp:float|str):
        """Set the target temperature.
        
        - Allowed floats: values between 8 and 28
        - Allowed strings: 'comfort', 'saving', 'on', 'off'
        """
        # Mit dem „param“ Get-Parameter wird die Solltemperatur übergeben.
        # Temperatur-Wert in  0,5 °C,
        # Wertebereich:
        # - 16 – 56 8 bis 28°C, 16 <= 8°C, 17 = 8,5°C...... 56 >= 28°C
        # - 254 = ON , 253 = OFF
        modes = ['on', 'off', 'comfort', 'saving']
        if isinstance(temp, str) and temp.lower() == 'on':
            temp = 254
        elif isinstance(temp, str) and temp.lower() == 'off':
            temp = 253
        elif isinstance(temp, str) and temp.lower() in {'comfort', 'saving'}:
            temp = self.get_temperature_settings()[temp.lower()]
            temp = int(temp * 2)
        else:
            try:
                temp = int(temp * 2)
                if not 16 <= temp <= 56:
                    raise ValueError("Target temperature must be between 8°C and 28°C")
            except Exception as e:
                raise ValueError(f"Target temperature must be between 8°C and 28°C \
                                 or in {modes}") from e
        params = {'param': temp}
        response = self._execute_switchcmd(SwitchCmd.sethkrtsoll, params)
        return response


    ### EXPERIMENTAL: requests to data.lua ###
    def get_web_ui_device_config(self):
        """Get configuration data via web UI"""
        # data = f"xhr=1&sid={self.sid}&lang=de&page=sh_dev&xhrId=all"
        data = WebUITemplate.DevicesConfig
        data['sid'] = self.sid
        full_web_ui_info = self._session.web_ui_request(data).json()
        # extract device configuration
        all_devices_info = full_web_ui_info['data']['devices']
        for device_info in all_devices_info:
            if str(device_info['id']) == self.id:
                return device_info

    def set_automatic_switching(self, autoswitch:bool, timer_mode:str="weekly"):
        """Set automatic switching on (True) or off (False)"""
        # check if switch
        if not self.features.outlet:
            return
        # get timer config
        device_config = self.get_web_ui_device_config()
        socket_config = [unit for unit in device_config['units'] \
                         if unit['type']=='SOCKET'][0]
        switch_config = [skill for skill in socket_config['skills'] \
                         if skill['type']=='SmartHomeSwitch'][0]
        timer_config = switch_config['timeControl']['timeSchedules']
        # basic POST request data
        data = {
            "xhr":"1",
            "sid": self.sid,
            "device": self.id,
            "switchtimer": timer_mode,
            "apply":"",
            "lang":"de",
            "page":"home_auto_timer_view",
        }
        # handle autoswitch instruction
        if autoswitch:
            data["switchautomatic"] = "on"
        # add weekly timer settings
        data["graphState"] = 1
        add_weekly_timer_data(timer_config, data)
        # send POST request
        response = self._session.web_ui_request(data)
        return response
