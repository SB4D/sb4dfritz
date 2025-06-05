""" 
A script to safely turn off Fritz!DECT smart switches connected to a Fritz!Box. 
Repeatedly checks whether the connected devices are idle and only turns off in 
that case. 
"""
__author__      = "Stefan Behrens"
__version__     = "0.2"

import fritzconnection
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation
import datetime
import time
import json


### ESTABLISH CONNECTIONS TO FRITZ BOX AND HOME AUTOMATION DEVICES
def connectToFritzServices():
    """Connects to the Fritz!Box and its home automation services."""
    # TODO: make sure login information is available
    try:
        with open("fritz_access.ini","r") as file:
            config = json.load(file)
        fritzbox_ip = config['ip']
        fritzbox_user = config['user']
        fritzbox_pw = config['pw']
    except:
        print("Please enter the login information for your Fritz!Box.")
        fritzbox_ip =   input("IP address: ")
        fritzbox_user = input("user name:  ")
        fritzbox_pw =   input("password:   ")
    # Connect to FritzBox
    fc = FritzConnection(address=fritzbox_ip, user=fritzbox_user, password=fritzbox_pw)
    # Connect to home automation services
    fh = FritzHomeAutomation(fc)
    return fc, fh 

def getDectSwitches(fh):
    """Gets the smart switches as HomeAutomationDevice() instances."""
    dect_devices = fh.get_homeautomation_devices()
    dect_switches = [device for device in dect_devices if device.is_switchable]
    return dect_switches


### A CUSTOM CLASS HOLDING THE TURN OFF WHEN IDLE METHOD
class SmartSwitch():
    """Provides convenient methods to interact with Fritz!DECT smart switches. 
    Some methods and attributes are shared with the HomeAutomationDevice class
    from the firtzconnection library.
    
    Attributes:
    - __device: hidden atrribute holding an instance of HomeAutomationDevice
    - ain: identifier used to communicate the the smart switch
    - name: name of the smart switch as assigned by the used
    - product_name: model name and number of the smart switch
    - idle_threshold: threshold for power in idle state (measured in Watts)

    Methods:
    - is_switchable(): checks if the HomeAutomationDevice is actually a switch
    - get_switch_state(): get the on/off status of the switch as a boolean
    - set_switch(): changes the current switch state
    - get_basic_device_stats(): get statistics recorded by the smart switch
    - get_power_stats(): gets only the statistics related to power 
    - get_latest_power_record(): gets only the latest power record and related time information
    - get_reliable_power_record(): specialized method to get a reliable power record
    - get_next_power_record(): specialized method to schedule a new power record
    - turn_off_if_idle(): checks if the switch is idle, and if so, turns it off
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

    # some methods inherited from the HomeAutomationDevice() instance
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
        """Get the power statistics recorded by the smart switch."""
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
        information after no power stats have been requested from the device 
        in a while. This can be seen by an outdated timestamp in the power 
        record. The way out is to send a few requests a few seconds apart 
        until the timestamp changes. This process may take up to ~12 seconds.

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
    
    def get_next_power_record(self, base_time, cycle=10):
        """Schedules the next iteration in a cycle of power record requests
        starting at a given timestamp (base_time) repeating every (cycle) seconds.

        Arguments:
        - base_time: the timestamp of the start of the cycle
        - cycle: the cycle length in seconds
        Returns:
        - power_record: a power record as returned by .get_latest_power_record()
        """
        exec_time = base_time
        while exec_time < datetime.datetime.now():
            exec_time += datetime.timedelta(seconds=cycle)
        sleep_time = (exec_time - datetime.datetime.now()).total_seconds()
        time.sleep(sleep_time)
        power_record = self.get_latest_power_record()
        return power_record


    def turn_off_if_idle(self,power_record,latency_threshold=2.5):
        """Check if the switch was reported idle with an acceptable latency, and if so, 
        turn it off.
        
        Arguments:
        - power_record: a power record as returned by .get_latest_power_record()
        - latency_threshold: maximal latency considered to be reliable
        Returns:
        - boolean indicating the final switch state (True indicates that)
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
        """Turns the switch off only when a power record with acceptable latency
        indicates idle state. 

        The strategy is to set up a request cycle that and synchronize it to
        the power measurement cycle of the switch. The latter is approximated 
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
        # check if switch is on
        switch_is_on = self.get_switch_state()
        # if not, do nothing
        if not switch_is_on:
            _status_update(f"{self.DeviceName} is already off.")
            return
        # get first reliable power record
        _status_update("Requesting current power data...") 

        power_record = self.get_reliable_power_record()
        _power_update(power_record, initial=True)
        # check if switch is idle with near optimal latency
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
            # check if switch is reported idle with allowed latency, if so, turn off
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


# some helper function
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


### THE COMMAND LINE INTERACTION
def runFromCommandLine(width=80):
    """Command line interface for turnOffWhenIdle."""
    ## PRINT INTRO
    print("="*width)
    print(f"{' TURN OFF WHEN IDLE ':{'='}^{width}}")
    print("="*width)
    print("Connecting to Fritz!Box to obtain list of running smart switches...")
    print("-"*width)
    ## CONNECT TO FRITZ!BOX AND GET SWITCHES
    # connect to Fritz!Box and get list of switches
    fc, fh = connectToFritzServices()
    dect_switches = getDectSwitches(fh)
    switches = [SmartSwitch(switch) for switch in dect_switches if switch.get_switch_state()]
    num_of_switches = len(switches)
    ## GET USER INPUT
    print("The following smart switches were detected:")
    for idx, switch in enumerate(switches):
        print(f"  ({idx+1}) {switch.DeviceName}")
    input_verified = False
    print("Which device would you like to be turned off?")
    while not input_verified:
        user_input = input(f"Enter a number: ")
        input_verified = verify_user_input(user_input, num_of_switches)
    # convert verified user input
    switch_idx = int(user_input) - 1
    switch = switches[switch_idx]
    ## RUN MAIN PROCEDURE
    # print("-"*width)
    print(f'Alright. Turning off "{switch.DeviceName}" when the connected devices are idle...')
    print("-"*width)
    # turn off when idle
    switch.turn_off_when_idle(
        # latency_threshold=1, 
        # cycle_detection_precision=3,
        silent=False, 
    )
    print("="*width)

# function to verify user input
def verify_user_input(user_input:str,bound:int)->bool:
    """Checks if user_input is an integer between 1 and the given bound."""
    input_ok = False 
    try:
        user_input = int(user_input)
    except:
        print(f"Input invalid. Please enter a number between 1 and {bound}.")
        return False
    input_ok = (type(user_input) == 'int') # and (0 < int(user_input) <= bound)
    if 0 < user_input <= bound:
        input_ok = True 
    else:
        print(f"Input invalid. Please enter a number between 1 and {bound}.")
    return input_ok

if __name__ == '__main__':
    runFromCommandLine()
