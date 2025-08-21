from sb4dfritz import SmartPlug
from sb4dfritz_test import SmartPlugSimulator
from time import sleep

if __name__ == "__main__":
    hline = "-"*80
    intro_text= """This is a demonstration of sb4dfritz. 

The script does the following things:
- simulate an electric appliance with irregular power consumption connected 
  to a smart plug from the AVM FRITZ! series as an instance of the class 
  'HomeAutomationDeviceSimulator' defined in sb4dfritz_test.py
- convert it to an instance of the class 'SmartPlug' defined in sb4dfritz.py
- call the method '.switch_off_when_idle()' from 'SmartPlug'

The entire process simulates turning off the author's espresso machine, which 
has irregular heating cycles, after waiting for an idle period while making 
sure that the power read-outs are reported with low latency.

NOTE: Implementing this is less straight forward than one might expect. 
This is because AVM FRITZ! smart plugs do not provide true real time 
information. In fact, the power consumption is only provided every 10 seconds.
"""
    print(hline)
    print(intro_text)
    print(hline)
    sleep(5)
    appliance_simulation = SmartPlugSimulator()
    smartplug_simulation = SmartPlug(appliance_simulation)
    print("\nStarting simulation...\n")
    print(hline)
    sleep(5)
    print("""
Virtual appliance and smart plug created. Waiting for the virtual appliance 
to be idle to switch it off...
""")

    sleep(2)
    smartplug_simulation.switch_off_when_idle(status_messages='console')
