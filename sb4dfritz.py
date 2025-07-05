""" 
Provide some specialized functionality for AVM FRITZ! smart home devices. 
Built on top of the `fritzconnection` API for .
"""
__author__      = "Stefan Behrens"
__version__     = "0.3"

import fritzconnection
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation
import datetime
import time
import json

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
        # some attributes inherited from the HomeAutomationDevice() instance
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
                'record time' : timestamp of record
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
            'power' : power,
            'record time' : record_time,
            'request time' : request_time,
            'response time' : response_time,
            'duration' : duration,
            'latency' : latency,
        }
        return data
    
    def get_reliable_power_record(self, interval=2):
        """Returns a reliable power record. 
        
        Explanation:
        Note that .get_latest_power_record() does not always give reliable 
        information. If no power stats have been requested from the smart  
        plug in a while, it usually returns an outdated power record, as 
        can be seen by the time stamp. To remedy this, one has to "wake up"
        the smart plug by sending a few requests until up to date information
        is returned. This may take up to ~15 seconds.

        Arguments:
        - interval: time to pause until the next request
        Returns:
        - power_record: a power record as returned by .get_latest_power_record()
        """
        # get initial power record and extract its timestamp
        power_record = self.get_latest_power_record()
        init_time = power_record['record time']
        # do the same once more right away
        power_record = self.get_latest_power_record()
        next_time = power_record['record time']
        # unless the timestamp has changed, way a bit and repeat until it changes
        while next_time == init_time:
            time.sleep(interval)
            power_record = self.get_latest_power_record()
            next_time = power_record['record time']
        # return the final power record
        return power_record
    
    def get_next_power_record(self, base_time, cycle_time=10):
        """Schedules the next iteration in a cycle of power record requests
        starting at a given timestamp (base_time) repeating every (cycle) seconds.

        Arguments:
        - base_time: the timestamp of the start of the cycle
        - cycle_time: the cycle length in seconds
        Returns:
        - power_record: a power record as returned by .get_latest_power_record()
        """
        exec_time = base_time
        while exec_time < datetime.datetime.now():
            exec_time += datetime.timedelta(seconds=cycle_time)
        sleep_time = (exec_time - datetime.datetime.now()).total_seconds()
        time.sleep(sleep_time)
        power_record = self.get_latest_power_record()
        return power_record


    def turn_off_if_idle(self,power_record,latency_threshold=2.5):
        """Check if the plug was reported idle with an acceptable latency, and if so, 
        turn it off.
        
        Arguments:
        - power_record: a power record as returned by .get_latest_power_record()
        - latency_threshold: maximal latency considered to be reliable
        Returns:
        - boolean indicating the final plug state (True indicates that)
        """
        # compare the power record to the idle threshold
        device_idle = power_record['power'] < self.idle_threshold
        # check the latency against 
        latency_ok = 0 <= power_record['latency'] < latency_threshold
        # act accordingly
        if device_idle and latency_ok:
            self.set_switch(False)
            return False
        else:
            return True
        
    def turn_off_when_idle(self, ideal_latency:float=0.5, cycle_detection_precision:int=1, silent:bool = True) -> None:
        """Turns the smart plug off only when a power record with acceptable latency
        indicates idle state. 

        The strategy is to set up a request cycle that and synchronize it to
        the power measurement cycle of the smart plug. The latter is approximated 
        with the specified precision using a divide and conquer strategy.

        Arguments:
        - ideal_latency: sets the ideal latency in seconds (default = 0.5)
        - cycle_detection_precision: determines the precision of the approximation
        as 10**(-cycle_detection_precision)
        - silent: controls if status updates are given as console output
        Returns:
        - None
        """
        # Help functions for console output
        def _status_update(status_string:str)->None:
            """Print input string to console if silent==False."""
            if not silent:
                print(status_string)
        def _power_update(power_record:dict,initial:bool=False)->None:
            """Print formatted extract of power record."""
            power = f"{power_record['power']:7.2f} W"
            record_time = print_timestamp(power_record['record time'],dig=0)
            request_time = print_timestamp(power_record['request time'],dig=cycle_detection_precision)
            latency = f"{power_record['latency']:5.2f} s"
            if initial:
                status_string = f"Power: {power:12} Latency: {latency:10}"
            else:
                status_string = f"Power: {power:12} Latency: {latency:10}"
                # status_string = f"Power: {power:12} Latency: {latency:10} (Increment: +/-{increment:0.3f} s, Offset: {offset:0.6f} s, Lower Bound: {lower_bound:0.6f} s, Minimal Latency: {minimal_latency:0.6f}, Threshold: {latency_threshold:0.6f} s)"
            _status_update(status_string)
        def _power_off_update(switch_is_on:bool)->None:
            """Power off notification."""
            if not switch_is_on:
                _status_update("Device reported idle with low latency. Turning off...")

        ## MAIN ROUTINE
        # check if smart plug is on
        switch_is_on = self.get_switch_state()
        # if not, do nothing
        if not switch_is_on:
            _status_update(f"{self.DeviceName} is already off.")
            return
        # get first reliable power record
        _status_update("Requesting current power data...") 

        power_record = self.get_reliable_power_record()
        _power_update(power_record, initial=True)
        # check if smart plug is idle with near optimal latency
        switch_is_on = self.turn_off_if_idle(power_record,latency_threshold=ideal_latency)
        _power_off_update(switch_is_on)

        # start detection loop
        # set initial base time of detection loop to latest power record time
        base_time = power_record['record time']
        # initialize parameters to adjust base time for detection
        latency_threshold = ideal_latency
        minimal_latency = power_record['latency']
        offset = 0
        lower_bound = -1
        increment = 1/4
        precision_is_low = (increment > 10**(-cycle_detection_precision))
        _status_update("Optimizing latency...")
        while switch_is_on:
            # get next power record
            power_record = self.get_next_power_record(base_time)
            _power_update(power_record)
            # extract information
            record_time = power_record['record time']
            latency = power_record['latency']
            if 0 <= latency < minimal_latency:
                minimal_latency = latency
            # check if smart plug is reported idle with allowed latency, if so, turn off
            switch_is_on = self.turn_off_if_idle(power_record,latency_threshold)
            _power_off_update(switch_is_on)
            # adjust parameters if needed
            # at this point the latency should be between 0 and 12.5 seconds
            # latency 10 or higher indicates that the request was sent too soon
            if 9 < latency < 12.5 or 0 > latency > -0.5:
                # adjust offset and its lower bound accordingly
                lower_bound = max([offset,lower_bound])
                offset += increment
            # in case of reasonably low latency, keep the lower bound, and reduce
            # the offset. 
            elif 0 < latency < 2.5:
                precision_can_be_increased = ((offset - increment) == lower_bound)
                precision_is_low = (increment > 10**(-cycle_detection_precision))
                if precision_is_low and precision_can_be_increased:
                    increment /= 2
                if (offset - increment) > lower_bound:
                    offset -= increment
            # in all other cases, something went wrong and the offset is reset to 0
            else:
                offset = 0
            if not precision_is_low:
                latency_threshold = minimal_latency + 0.25
            # update the base time of the detection cycle
            base_time = nudge_timestamp(record_time,seconds=offset)

    def turn_off_when_idle_low_latency(self, cycle_detection_precision=0.1, idle_cycles_required=2):
        print("-"*50)
        print("Optimizing latency for power value readouts...")
        print("-"*50)
        # initialize utility variables
        iterations = -1
        power_log = []
        latencies = []
        offset = 1
        good_offsets = {3}
        bad_offsets = {-1}
        offset_gap = min(good_offsets) - max(bad_offsets)
        ### FIRST LOOP - establish power read out request cycle with low latency ###
        while offset_gap > cycle_detection_precision:
            # update counter
            iterations += 1
            # get power record
            if iterations == 0:
                power_record = self.get_reliable_power_record()
                measure_cycle_base_time = power_record['record time']
                request_cycle_base_time = measure_cycle_base_time
            else:
                request_cycle_base_time = nudge_timestamp(measure_cycle_base_time,offset)
                power_record = self.get_next_power_record(request_cycle_base_time)
            # update log 
            power_record['base time'] = request_cycle_base_time
            power_record['offset'] = offset
            power_log.append(power_record)
            # extract time parameters for console output
            request_time = power_record['request time']
            response_time = power_record['response time']
            record_time = power_record['record time']
            # extract latency and store separately
            latency = power_record['latency']
            latencies.append(latency)
            duration = power_record['duration']
            power = power_record['power']
            # categorize current offset
            if iterations > 0 and latency >= 10:
                bad_offsets.add(offset)
            if iterations > 0 and 0 <= latency < 10:
                good_offsets.add(offset + cycle_detection_precision)
            # good_offsets.difference_update(bad_offsets)
            good_offsets = set([t for t in good_offsets if t > max(bad_offsets)])
            # print(f"Base Time: {request_cycle_base_time} | Response: {response_time} | Record: {record_time} | Latency: {latency:5.2f} | Offset: {offset:6.3f}")
            # print(f"    bad offsets -> {sorted(bad_offsets)}, {sorted(good_offsets)} <- good offsets")
            print(f"({iterations}) Power: {power:7.2f} W | Latency: {latency:5.2f} s | Response Time: {duration:4.2f} s | Offset: {offset:6.3f} s")
            # update offset
            offset_gap = min(good_offsets) - max(bad_offsets)
            assert offset_gap > 0, "Negative gap!"
            if offset_gap > cycle_detection_precision:
                offset = (min(good_offsets) + max(bad_offsets)) / 2
            else:
                offset = min(good_offsets)
        print("-"*50)
        print("Latency optimized. Switching off if devices are idle...")
        print("-"*50)
        request_cycle_base_time = nudge_timestamp(measure_cycle_base_time,offset)
        idle_count = 0
        ### SECOND LOOP - turn off when idle ###
        while True:
            # update counter
            iterations += 1
            # get next power read out
            power_record = self.get_next_power_record(request_cycle_base_time)
            # update power log
            power_record['base time'] = request_cycle_base_time
            power_record['offset'] = offset
            power_log.append(power_record)
            # extract information for concole output
            power = power_record['power']
            latency = power_record['latency']
            # adjust offset if needed
            if latency > 10:
                offset += cycle_detection_precision
                request_cycle_base_time = nudge_timestamp(measure_cycle_base_time,offset)
            print(f"({iterations}) Power: {power:7.2f} W | Latency: {latency:5.2f} s | Response Time: {duration:4.2f} s | Offset: {offset:6.3f} s")
            # count idle cycles and turn off if requirement is met
            if power < self.idle_threshold and 0 <= latency < 5:
                idle_count += 1
            else:
                idle_count = 0
            if idle_count == idle_cycles_required:
                self.set_switch(False)
                break
        print("-"*50)
        print(f"{self.DeviceName} was switched off.")
        print("-"*50)
        return power_log


##  SOME HELPER FUNCTIONS  ##

def nudge_timestamp(timestamp,seconds):
    """Nudges a timestamp by a given number of seconds."""
    # create timedelta from seconds
    timedelta= datetime.timedelta(seconds=seconds)
    # add timedelta to timestamp
    nudged_timestamp = timestamp + timedelta
    return nudged_timestamp

def print_timestamp(timestamp, dig=None):
    """Convert timestamp to a string in the format HH:MM:SS.digits with 
    digits controlling the number of digits for the seconds value."""
    try:
        if dig == 0:
            time_string = timestamp.strftime("%H:%M:%S")
        elif 0 < dig <=6:
            time_string = timestamp.strftime("%H:%M:%S.%f")[:dig-6]
    except:
        time_string = timestamp.strftime("%H:%M:%S.%f")
    return time_string

# NOTE: This script is not meant to be executed by itself.
# The following is just for testing during development.
if __name__ == "__main__":
    print("Trying to get list of smart plugs...")
    fritzbox = FritzBoxSession()
    plugs = fritzbox.getSmartPlugs()
    print("The following smart plugs were detected:")
    for plug in plugs:
        print(plug.DeviceName)
    # plugs[0].turn_off_when_idle_low_latency()
    