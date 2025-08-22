""" 
A script to safely turn off FRITZ!DECT smart plugs connected to a FRITZ!Box. 
Repeatedly checks whether the connected devices are idle and only turns off in 
that case. 
"""
__author__      = "Stefan Behrens"
__version__     = "0.4"

# from sb4dfritz import FritzBoxSession, SmartPlug
from sb4dfritzlib.connection import FritzUser
from sb4dfritzlib.homeauto import HomeAutoSystem
import argparse
import json

# load config file
CONFIG_FILE = "..\\..\\_private_files\\sb4dfritz_secrets.ini"
with open(CONFIG_FILE,"r") as file:
    CONFIG = json.load(file)
# extract login data
IP = CONFIG['login']['ip']
USER = CONFIG['login']['user']
PWD = CONFIG['login']['pwd']
# width of console interface
WIDTH = 80


def main(width=WIDTH, debug_mode=False):
    """The main routine"""
    # Print intro
    print("")
    print("="*width)
    print(f"{' SB4DFRITZ - SWITCH OFF WHEN IDLE ':{'='}^{width}}")
    print("="*width)
    print("Connecting to FRITZ!Box to obtain list of running smart plugs...")
    print("-"*width)
    # Connect to FRITZ!Box router
    FRITZ_USER = FritzUser(USER, PWD, IP)
    fritzbox = HomeAutoSystem(FRITZ_USER)
    # Get list and count of active smart plugs
    smart_plugs = [device for device in fritzbox.devices if device.is_switchable]
    active_plugs = [plug for plug in smart_plugs if plug.get_switch_state()]
    num_of_plugs = len(active_plugs)
    print("The following smart plugs were detected:\n")
    for idx, plug in enumerate(active_plugs):
        print(f"  ({idx+1}) {plug.name}")
    print("")
    # Ask user which smart plug should be switched off
    input_verified = False
    print("Which device would you like to switch off?")
    while not input_verified:
        user_input = input(f"Enter a number: ")
        input_verified = verify_user_input(user_input, num_of_plugs)
    # Process user input
    plug_idx = int(user_input) - 1
    plug = active_plugs[plug_idx]
    print("-"*width)
    # turn off when idle
    plug.switch_off_when_idle(
        status_messages='console', 
        debug_mode=debug_mode)
    print("="*width)
    print("")
    # ask to run again
    while True:
        user_input = input(
            "Would you like to switch off another smart plug? (Y/N)\n" \
            "Enter 'Y' for yes or 'N' for no: "
        ).upper()
        if user_input == "Y":
            main(debug_mode=debug_mode)
        elif user_input == "N":
            print("")
            return
        else:
            print("Please enter 'Y' for yes or 'N' for no.")

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


if __name__ == "__main__":
    # define command line options
    parser = argparse.ArgumentParser(
        description = \
            "SwitchOffWhenIdle can run in normal mode or in debug mode." \
            "The latter does runs the algorithm, but does not switch off the device."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    # handle command line options
    if args.debug:
        main(debug_mode=True)
    else:
        main()  # default option