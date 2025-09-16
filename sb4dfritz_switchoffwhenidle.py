""" 
A script to safely turn off FRITZ!DECT smart plugs connected to a FRITZ!Box. 
Repeatedly checks whether the connected devices are idle and only turns off in 
that case. 

CHANGELOG:
0.4.3: asking for a second device improved
0.4.2: minor changes required by updates in sb4dfritzlib
0.4.1: added logging option (-log).
0.4.1: minor cosmetic changes in console interaction
0.4: complete rewrite
0.4: code self-contained (no longer relies on fritzconnection)
"""
__author__      = "Stefan Behrens"
__version__     = "0.4.3"

from sb4dfritzlib.homeauto import HomeAutoSystem, HomeAutoDevice
import json
import os
import argparse

# load config file
CONFIG_FILE = "..\\..\\_private_files\\sb4dfritz_secrets.ini"
with open(CONFIG_FILE,"r") as file:
    CONFIG = json.load(file)
# extract login data
USER = CONFIG['login']['user']
PWD = CONFIG['login']['pwd']
IP = CONFIG['login']['ip']
# width of console interface
WIDTH = 80


class SwitchOffWhenIdle():
    """"""

    def __init__(self, width:int=80, logging:bool=False, debug_mode:bool=False):
        self.width = width
        self.logging = logging
        self.debug_mode = debug_mode
        self.homeauto:HomeAutoSystem = None
        self.smart_plugs:list[HomeAutoDevice] = None
    
    def run(self):
        """Run main program."""
        self.intro()
        self.connect()
        self.switch_off_routine()

    def intro(self):
        """Run program intro."""
        width = self.width
        # Print intro
        print("")
        print("="*width)
        print(f"{' SB4DFRITZ - SWITCH OFF WHEN IDLE ':{'='}^{width}}")
        print("="*width)
        print("Connecting to FRITZ!Box to obtain list of running smart plugs...")
        print("-"*width)
    
    def connect(self):
        """Connect to home automation system and get list of connected smart plugs."""
        self.homeauto = HomeAutoSystem(USER, PWD, IP)
        self.smart_plugs = [dev for dev in self.homeauto.devices if dev.is_switchable]

    def switch_off_routine(self):
        """Run main routine: Ask user which active plug should be switched off, wait 
        for the plug to be idle, switch it off, and ask if another switch should be
        swtiched off."""
        # ask user which plug should be switched off
        plug = self.get_user_input()
        # switch off when idle and get power records
        power_records = plug.switch_off_when_idle(
            status_messages='console', 
            debug_mode=self.debug_mode)
        # print separator
        print("="*self.width)
        print("")
        # write log if something is weird
        if self.logging:
            log_power_records(power_records)
        # ask to run again
        while True:
            user_input = input(
                "Would you like to switch off another smart plug? (Y/N)\n" \
                "Enter 'Y' for yes or anything else to exit: "
            ).upper()
            if user_input == "Y":
                # print separator
                print("-"*self.width)
                self.switch_off_routine()
            else:
                print("")
                return
    
    def get_active_plugs(self):
        # make sure a connection has been established
        if not self.smart_plugs:
            self.connect()
        # Get list and count of active smart plugs ordered alphabetically by name
        active_plugs = [plug for plug in self.smart_plugs if plug.get_switch_state()]
        active_plugs.sort(key=lambda plug: plug.name.lower())
        return active_plugs
    
    def get_user_input(self):
        active_plugs = self.get_active_plugs()
        num_of_plugs = len(active_plugs)
        print("The following smart plugs were detected:\n")
        for idx, plug in enumerate(active_plugs):
            print(f"  ({idx+1}) {plug.name}")
        print("")
        # Ask user which smart plug should be switched off
        print("Which device would you like to switch off?")
        input_verified = False
        while not input_verified:
            user_input = input(f"Press 'Enter' for (1) or choose a number: ")
            if user_input == "":
                user_input = 1
            input_verified = verify_input(user_input, num_of_plugs)
        # Process user input
        plug_idx = int(user_input) - 1
        plug = active_plugs[plug_idx]
        print("-"*self.width)
        return plug


def verify_input(user_input:str,bound:int)->bool:
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

def log_power_records(power_records:list[dict], log_file:str="logs/switchoffwhenidle.log")->None:
    """Write list of power records to log file in csv format if the 
    minimal latency is either negative or over 2 seconds. """
    # check latencies, only log if minimum is not between 0 and 2 seconds
    latencies = [record['latency'] for record in power_records]
    if 0 <= min(latencies) < 2:
        return
    # check if log_file exists, if not create it and write header
    if not os.path.exists(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "w") as f:
            f.write("date,starttime,datatime,endtime,duration,latency,power\n")
    # write records to the log file
    with open(log_file, "a") as file:
        for record in power_records:
            record_str = ",".join([
                record['starttime'].strftime("%Y-%m-%d,%H:%M:%S.%f")[:-4],
                record['datatime'].strftime("%H:%M:%S"),
                record['endtime'].strftime("%H:%M:%S.%f")[:-4],
                f"{record['duration']:0.2f}",
                f"{record['latency']:0.2f}",
                f"{record['power']:0.2f}",
            ])
            file.write(record_str + "\n")


if __name__ == "__main__":
    # define command line options
    parser = argparse.ArgumentParser(
        description = \
            "SwitchOffWhenIdle can run in normal mode or in debug mode." \
            "The latter runs the algorithm, but does not switch off the device."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-debug", action="store_true", help="Run in debug mode")
    group.add_argument("-log", action="store_true", help="Write power records to log file.")
    args = parser.parse_args()

    # handle command line options
    if args.debug:
        SwitchOffWhenIdle(debug_mode=True, logging=True).run()
    elif args.log:
        SwitchOffWhenIdle(logging=True).run()
    else:
        SwitchOffWhenIdle().run()  # default option