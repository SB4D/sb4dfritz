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



if __name__ == "__main__":
    sid = sb4dfritzlib.apis.ahahttp.get_sid(FRITZ_USER, FRITZ_PWD, FRITZ_IP)
    print(sid)
    