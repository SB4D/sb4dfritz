""" 
A script to safely turn off FRITZ!DECT smart plugs connected to a FRITZ!Box. 
Repeatedly checks whether the connected devices are idle and only turns off in 
that case. 
"""
__author__      = "Stefan Behrens"
__version__     = "0.3"


from sb4dfritz import FritzBoxSession, SmartPlug

WIDTH = 80

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
    # Print intro
    print("")
    print("="*WIDTH)
    print(f"{' TURN OFF WHEN IDLE ':{'='}^{WIDTH}}")
    print("="*WIDTH)
    print("Connecting to FRITZ!Box to obtain list of running smart plugs...")
    print("-"*WIDTH)
    # Connect to FRITZ!Box router
    fritzbox = FritzBoxSession()
    # Get list and count of active smart plugs
    smart_plugs = fritzbox.getSmartPlugs()
    active_plugs = [plug for plug in smart_plugs if plug.get_switch_state()]
    num_of_plugs = len(active_plugs)
    print("The following smart plugs were detected:")
    for idx, plug in enumerate(active_plugs):
        print(f"  ({idx+1}) {plug.DeviceName}")
    print("")
    # Ask user which smart plug should be switched off
    input_verified = False
    print("Which device would you like to be turned off?")
    while not input_verified:
        user_input = input(f"Enter a number: ")
        input_verified = verify_user_input(user_input, num_of_plugs)
    print("")
    # Process user input
    plug_idx = int(user_input) - 1
    plug = active_plugs[plug_idx]
    print(f'Switching off "{plug.DeviceName}" when the connected devices are idle...')
    print("-"*WIDTH)
    # turn off when idle
    plug.turn_off_when_idle(silent=False)
    print("="*WIDTH)
    print("")