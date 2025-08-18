import sb4dfritzlib
import json

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
    print("Testing stuff...\n")

    sid = sb4dfritzlib.apis.ahahttp.get_sid(FRITZ_USER, FRITZ_PWD)
    print("Login successful. SID:", sid)

    params = {
        # 'ain': ain.replace("", " "),
        'ain': TV,
        'switchcmd': 'getbasicdevicestats',
        'sid': sid
    }
    response = sb4dfritzlib.apis.ahahttp.ahahttp_request(params)
    print(response)
    print(response.text)
    # print(sb4dfritzlib.apis.tr064.get_info(FRITZ_USER, FRITZ_PWD, FRITZ_IP).text)

    # results = sb4dfritzlib.apis.tr064.set_switch(FRITZ_USER, FRITZ_PWD, FRITZ_IP, TV, "TOGLE")
    # print(results.text)
    
    # for ain in AINS:
    #     results = sb4dfritzlib.apis.tr064.get_specific_device_info(FRITZ_USER, FRITZ_PWD, FRITZ_IP, ain)
    #     print(results.text)
