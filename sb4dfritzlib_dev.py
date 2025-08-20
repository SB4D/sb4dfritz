import sb4dfritzlib
import json
import requests

from os.path import abspath, relpath

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
    # print(homeauto.devices[0].model)
    # print(homeauto.devices[0].device_id)
    # print(homeauto.devices[0].ain)
    # print(homeauto.devices[0].present)
    print(homeauto.devices[0].get_basic_device_stats().keys())
    # print(homeauto.devices[0].get_basic_device_stats())
    print(homeauto.devices[0].get_basic_device_stats()['energy_2'])
    power_record = homeauto.devices[4].get_latest_power_record()
    # for key, val in power_record.items():
    #     print(f"{key:15s} {val}")


    # fritzbox_session = sb4dfritzlib.connection.FritzBoxSession(USER)
    # sid = fritzbox_session.sid

    # message = sb4dfritzlib.connection.http.getdevicelistinfos(sid)
    # print(message)
    # ains = fritzbox_session.switches
    # for ain in ains:
    #     stats = sb4dfritzlib.connection.http.getswitchpower(ain, sid)
    #     print(stats)
    
    # print("Testing stuff...\n")

    
    # sid = sb4dfritzlib.connection.get_sid(FRITZ_USER, FRITZ_PWD)
    # print("Login successful. SID:", sid)

    # params = {
    #     # 'ain': ain.replace("", " "),
    #     'ain': ANGOLO,
    #     'switchcmd': 'getswitchpower',
    #     'sid': sid
    # }
    # from time import time 
    # for _ in range(60):
    #     response = sb4dfritzlib.connection.aha_request(params)
    #     print(f"{time():10.0f}, {response.text.strip():10s}")
    # count = 0
    # while True:
    #     count += 1
    #     response = sb4dfritzlib.apis.ahahttp.ahahttp_request(params)
    #     print(f"{count:3d}", response.text.strip())
    
    # url = "http://fritz.box/data.lua"
    # params = {
    #     "xhr": "1",
    #     "sid": sid,
    #     "page": "sh_dev",   # or "homeauto" depending on what you want
    #     "lang": "en",
    # }

    # resp = requests.get(url, params=params)
    # # resp = sb4dfritzlib.apis.ahahttp.ahahttp_request(params,url)
    # print(resp)  # often JSON with device info
    # print(resp.text)  # often JSON with device info
    