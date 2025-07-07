from sb4dfritz import SmartPlug
from sb4dfritz_test import HomeAutomationDeviceSimulator
from time import sleep

if __name__ == "__main__":
    hline = "-"*80
    intro_text= """This is a demonstration of sb4dfritz. 

The script does the following things:
- simulate an electric appliance with irregular power consumption connected 
  to a smart plug from the AVM FRITZ! series as an instance of the class 
  'HomeAutomationDeviceSimulator' defined in sb4dfritz_test.py
- convert it to an instance of the class 'SmartPlug' defined in sb4dfritz.py
- call the method 'turn_off_when_idle_low_latency' from 'SmartPlug'

The entire process simulates turning off the author's espresso machine, which 
has irregular heating cycles, after waiting for an idle period while making 
sure that the power read-outs are reported with low latency.

NOTE: Implementing this is much less straight forward than one might expect. 
This is due to undocumented quirks in the "real time monitoring" features of 
AVM FRITZ! smart plugs. In fact, power data is only provided every 10 seconds
and synchronizing the power read-out requests with the measurement cycle is 
somewhat tedious. For more on this, see the Jupyter notebook
./Notebooks/NOTES--toggle_automatic_switching.ipynb

WARNING: The script can take over 2 minutes to finish! 

The gap length must reach a value below 0.2 s and two idle cycles are required, 
where idle means a power consumption below 5 W.
"""
    print(hline)
    print(intro_text)
    print(hline)
    sleep(5)
    appliance_simulation = HomeAutomationDeviceSimulator()
    smartplug_simulation = SmartPlug(appliance_simulation)
    print("\nStarting simulation...\n")
    print(hline)
    sleep(5)
    print("""
Virtual appliance and smart plug created. Waiting for the virtual appliance 
to be idle to switch it off...
""")

    sleep(2)
    smartplug_simulation.turn_off_when_idle_low_latency(cycle_detection_precision=0.2)
