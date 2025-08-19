"""Implements the HTTP interface for FRITZ!Box routers provided by AVM."""

import requests


URL_BASE = 'http://fritz.box/'
AHA = 'webservices/homeautoswitch.lua'
DATA = 'data.lua'



def aha_request(params:dict[str:str])->requests.Response:
    """Basa HTTP GET request for the AHA-HTTP interface."""
    # Parameters for the GET request
    params = [f"{key}={val}" for key, val in params.items()]
    params = "&".join(params)

    request_url = f"{URL_BASE}{AHA}?{params}"
    response = requests.get(request_url, verify=False)  # Use verify=False if self-signed cert
    return response

# ain = AINS[0].replace(" ", "")              # AIN of your smart device
# # cmd = 'getswitchlist'               # Example command (see command list below)
# cmd = 'getswitchpower'               # Example command (see command list below)
# cmd = 'getbasicdevicestats'               # Example command (see command list below)
