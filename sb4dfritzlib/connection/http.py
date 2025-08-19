"""Implements the HTTP interface for FRITZ!Box routers provided by AVM."""

import requests


URL_BASE = 'http://fritz.box/'
AHA = 'webservices/homeautoswitch.lua'
DATA = 'data.lua'



def aha_basic_request(params:dict[str:str])->requests.Response:
    """Basa HTTP GET request for the AHA-HTTP interface."""
    # Parameters for the GET request
    params = [f"{key}={val}" for key, val in params.items()]
    params = "&".join(params)

    request_url = f"{URL_BASE}{AHA}?{params}"
    response = requests.get(request_url, verify=False)  # Use verify=False if self-signed cert
    return response


def getdevicelistinfos(sid:str)->str:
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'switchcmd':'getdevicelistinfos', 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains XML string
    # ending with a line break
    reponse = aha_basic_request(params)
    # convert into list of strings representing the AINs
    infos = reponse.text.strip()
    return infos


def getswitchlist(sid:str)->list[str]:
    """Returns the AINs of connected switches as a list of strings."""
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'switchcmd':'getswitchlist', 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains AINs of switches as comma separated list
    # ending with a line break
    reponse = aha_basic_request(params)
    # convert into list of strings representing the AINs
    ains = reponse.text.strip().split(",")
    return ains


def getswitchstate(ain:str, sid:str)->bool:
    """Returns the on/off state of the switch with given AIN as 
    "1" for on, "0" for off, and "inval" for an invalid AIN."""
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'ain':ain,
        'switchcmd':'getswitchstate', 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains "1\n" for on and "0\n" for off
    reponse = aha_basic_request(params)
    # extract state and convert to integer
    state = reponse.text.strip()
    return state


def setswitch(ain:str, sid:str, state:int=None)->bool:
    """Sets the switch state of the switch with given AIN.
    
    Parameters:
    - ain : AIN of switch
    - sid : valid session id
    - state : target state encoded as integer (off: 0, on: 1, toggle: 2)
    """
    # derive switch command in AHA-HTTP documentions from state variable
    if state == 0: command = 'setswitchoff'
    elif state == 1: command = 'setswitchon'
    elif state == 2: command = 'setswitchtoggle'
    else: command = 'getswitchstate'
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'ain':ain,
        'switchcmd': command, 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains AINs of switches as comma separated list
    # ending with a line break
    reponse = aha_basic_request(params)
    # convert into list of strings representing the AINs
    state = reponse.text.strip()
    return int(state)


def getdeviceinfos(ain:str, sid:str)->str:
    """Get basic device information."""
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'ain':ain,
        'switchcmd': 'getdeviceinfos', 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains XML string
    reponse = aha_basic_request(params)
    infos = reponse.text.strip()
    return infos


def getbasicdevicestats(ain:str, sid:str)->str:
    """Get basic statistic (temperature, power, voltage, energy) of
    device."""
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'ain':ain,
        'switchcmd': 'getbasicdevicestats', 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains XML string
    reponse = aha_basic_request(params)
    stats = reponse.text.strip()
    return stats


def getswitchpower(ain:str, sid:str)->float:
    """Returns the current power consumption."""
    """Get basic device information."""
    # assemble parameter dictionary according to AHA-HTTP documentation
    params = {
        'ain':ain,
        'switchcmd': 'getswitchpower', 
        'sid':sid, 
    }
    # send basic AHA-HTTP request
    # NOTE: response contains power consumption in mW
    reponse = aha_basic_request(params)
    # convert power value to Watt
    power = reponse.text.strip()
    power = float(power) / 1000
    return power
