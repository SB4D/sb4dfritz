import requests
from datetime import datetime
from time import sleep
import xml.etree.ElementTree as ET

from ..connection import FritzSession
from .devices import HomeAutoDevice
from .aha import FunctionBitMask
from .aha import SwitchCmd
from ..utilities.xml import process_xml_stats
from .webui import WebUITemplate
from .webui import add_weekly_timer_data

class HomeAutoSystem:
    
    def __init__(self):
        self._session = FritzSession()
        self.devices:list[HomeAutoDevice] = []
        self.get_devices()
    
    @property
    def sid(self):
        return self._session.sid
    
    def request(self, switchcmd:SwitchCmd, params:dict=None) -> requests.Response:
        self._session.aha_command(switchcmd, params)
    
    def get_devices(self):
        device_infos = self.get_device_list_info()
        devices = []
        for device_info in device_infos:
            device = HomeAutoDevice.from_dict(device_info)
            device._session = self._session
            devices.append(device)
        self.devices = devices

    def get_device_list_info(self) -> list[dict]:
        # retrieve device list and information as raw XML and convert to XLM tree object
        device_list_xml = self._session.aha_command(SwitchCmd.getdevicelistinfos).text
        device_list_tree = ET.fromstring(device_list_xml)
        # extract relevant information
        device_infos = []
        for device in device_list_tree:
            name = device.find("name").text
            ain = device.items()[0][1]
            id = device.items()[1][1]
            functionbitmask = device.items()[2][1]
            manufacturer = device.items()[4][1]
            productname = device.items()[5][1]
            device_info = {
                "name": name,
                "ain": ain,
                "id": id,
                "functionbitmask": functionbitmask,
                "manufacturer": manufacturer,
                "productname": productname,
            }
            device_infos.append(device_info)
        return device_infos

    ### EXPERIMENTAL: requests to data.lua ###
    def get_web_ui_devices_config(self):

        data = f"xhr=1&sid={self.sid}&lang=de&page=sh_dev&xhrId=all"

        response = self._session.web_ui_request(data)
        if response.status_code == 200:
            info_dict = response.json()
            return info_dict
        return response

