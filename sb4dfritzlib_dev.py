import sb4dfritzlib
import json
import requests

from os.path import abspath, relpath
from time import sleep

# load config file
CONFIG_FILE = "..\\..\\_private_files\\sb4dfritz_secrets.ini"
with open(CONFIG_FILE,"r") as file:
    FRITZBOX = json.load(file)
# extract login data
FRITZ_IP = FRITZBOX['login']['ip']
FRITZ_USER = FRITZBOX['login']['user']
FRITZ_PWD = FRITZBOX['login']['pwd']
# extract device ains
DEVICES = FRITZBOX['ains']
AINS = list(DEVICES.values())

ANGOLO, TV = AINS

if __name__ == "__main__":

    USER = sb4dfritzlib.connection.FritzUser(FRITZ_USER, FRITZ_PWD, FRITZ_IP)

    homeauto = sb4dfritzlib.homeauto.HomeAutoSystem(USER)

    print(homeauto.devices[0].name)
    print(homeauto.devices[0].get_basic_device_stats().keys())
    # print(homeauto.devices[0].get_basic_device_stats())
    # print(homeauto.devices[0].get_basic_device_stats()['energy_2'])
    power_record = homeauto.devices[4].get_latest_power_record()
