""" 
Provide some specialized functionality for AVM FRITZ! smart home devices. 
Built on top of the `fritzconnection` API for .
"""
__author__      = "Stefan Behrens"
__version__     = "0.3.1"

import fritzconnection
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation
import datetime
import time
import json
import csv
import os

# Location of config file. Replace with your own. 
CONFIG_FILE = "..\\..\\_private_files\\sb4dfritz_access.ini"
# NOTE: A config file must be a text file (JSON) containing the following:
# {"ip": "<IP address FRITZ!BOX>", "user": "<user name>", "pw": "<password>"}

##  THE MAIN CLASSES: FritzBoxSession, SmartPlug  ##

class FritzBoxSession():
    """ Connects to an AVM FRITZ!Box router using the `fritzconnection` API."""

    def __init__(self,config_file=CONFIG_FILE):
        # get login infor from config file
        with open(config_file,"r") as file:
            config = json.load(file)
        fritzbox_ip = config['ip']
        fritzbox_user = config['user']
        fritzbox_pw = config['pw']
        # connection to FRITZ!Box
        self.connection:FritzConnection = FritzConnection(address=fritzbox_ip, user=fritzbox_user, password=fritzbox_pw)
        # connection to home automation services
        self.home_auto:FritzHomeAutomation = FritzHomeAutomation(self.connection)
    
    def getSmartPlugs(self):
        """Gets the smart plugs as HomeAutomationDevice() instances."""
        home_auto_devices = self.home_auto.get_homeautomation_devices()
        smart_plugs = [SmartPlug(device) for device in home_auto_devices if device.is_switchable]
        return smart_plugs

class SmartPlug():
    """Provides convenient methods to interact with Fritz!DECT smart plugs. 
    Some methods and attributes are shared with the HomeAutomationDevice class
    from the firtzconnection library.
    
    Attributes:
    - __device: hidden atrribute holding an instance of HomeAutomationDevice
    - ain: identifier used to communicate the the smart plug
    - name: name of the smart plug as assigned by the used
    - product_name: model name and number of the smart plug
    - idle_threshold: threshold for power in idle state (measured in Watts)

    Methods:
    - is_switchable(): checks if the HomeAutomationDevice is actually a plug
    - get_switch_state(): get the on/off status of the plug as a boolean
    - set_switch(): changes the current plug state
    - get_basic_device_stats(): get statistics recorded by the smart plug
    - get_power_stats(): gets only the statistics related to power 
    - get_latest_power_record(): gets only the latest power record and related time information
    - get_reliable_power_record(): specialized method to get a reliable power record
    - get_next_power_record(): specialized method to schedule a new power record
    - turn_off_if_idle(): checks if the plug is idle, and if so, turns it off
    - turn_off_when_idle(): waits for the device to be reliably idle and turns it off
    """

    def __init__(self,fritzdevice,idle_threshold=5):
        # private attribute containing a HomeAutomationDevice() instance
        self.__device = fritzdevice
        # some attributes borrowed from the HomeAutomationDevice() instance
        self.identifier = self.__device.identifier
        self.DeviceName = self.__device.DeviceName
        self.model = f"{self.__device.Manufacturer} {self.__device.ProductName}"
        # additional attribute: threshold for power in idle state (measured in Watts)
        self.idle_threshold = idle_threshold
    
    def __str__(self):
        return f"{self.DeviceName} ({self.model}, AIN: {self.identifier})"

    # some methods borrowed from the HomeAutomationDevice() instance
    def is_switchable(self):
        return self.__device.is_switchable()
    def get_switch_state(self):
        return self.__device.get_switch_state()
    def set_switch(self,arg):
        return self.__device.set_switch(arg)
    def get_basic_device_stats(self):
        return self.__device.get_basic_device_stats()
    
    # some customized methods
    def get_power_stats(self):
        """Get the power statistics recorded by the smart plug."""
        power_stats = self.__device.get_basic_device_stats()['power']
        return power_stats
    
    def get_latest_power_record(self):
        """Returns information regarding the latest power value recorded
        by a FritzDECT device.

        Returns:
            info : dictionary containing the following information:
                'power' : lastest power value recorded by device
                'datatime' : timestamp of record
                'request time' : timestamp of request
                'repsonse time' : timestamp of response
                'duration' : time between request and response in seconds
                'latency' : time between record time and response in seconds
        """
        # Get timestamp of request time
        request_time = datetime.datetime.now()
        # Get stats
        power_stats = self.get_power_stats()
        # Get timestamp of response time
        response_time = datetime.datetime.now()
        # Extract latest power record and convert to Watt
        # (Note: power is recorded as integer multiple of 0.01 W)
        power = power_stats['data'][0] / 100
        # Extract time stamp of record
        record_time = power_stats['datatime']
        # Compute latency and duration
        duration = (response_time - request_time).total_seconds()
        latency = (response_time - record_time).total_seconds()
        # Package the information in dictionary and return
        data = {
            'request time' : request_time,
            'response time' : response_time,
            'duration' : duration,
            'datatime' : record_time,
            'power' : power,
            'latency' : latency,
        }
        return data

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
        status_update(f'Switching off "{self.DeviceName}" when idle...\n')
        # check if switch is on
        switch_is_on = self.get_switch_state()
        if not switch_is_on:
            status_update("Switch is already off. Nothing to do.")
            return
        # start monitoring power consumption
        status_update("Monitoring power consumption..." + "\n" + "-" * WIDTH)
        power_monitor = []
        while switch_is_on:
            # get the latest power measurement
            data = self.get_latest_power_record()
            # add to power_monitor on first pass or if 'datatime' jumps
            L = len(power_monitor)
            if L == 0 or data['datatime'] != power_monitor[-1]['datatime']:
                power_monitor.append(data)
                log_data(data)
                status_update(
                    "Power: {:7.2f} W | Duration: {:5.2f} s | Latency: {:5.2f} s".format(
                        data['power'], 
                        data['duration'], 
                        data['latency'], 
                    )
                )
            # check the last measurements for idle status
            # NOTE: the very first measurement might be unreliable
            if L > idle_cycles:
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
    