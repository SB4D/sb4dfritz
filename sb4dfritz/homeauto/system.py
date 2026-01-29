"""Class for entire home automation system"""

import xml.etree.ElementTree as ET
import requests

from ..connection import FritzSession
from .devices import HomeAutoDevice
from .aha import SwitchCmd

class HomeAutoSystem:
    """Class for home automation system"""

    def __init__(self):
        self._session = FritzSession()
        self.devices:list[HomeAutoDevice] = []
        self.get_devices()

    @property
    def sid(self):
        """Returns the current session ID"""
        return self._session.sid

    def request(self, switchcmd:SwitchCmd, params:dict=None) -> requests.Response:
        """Invokes the AHA-HTTP interface with given switchcmd and params"""
        self._session.aha_command(switchcmd, params)

    def get_devices(self):
        """Initialize smart home devices"""
        device_infos = self.get_device_list_info()
        devices = []
        for device_info in device_infos:
            device = HomeAutoDevice.from_dict(device_info)
            device._session = self._session
            devices.append(device)
        self.devices = devices

    def get_device_list_info(self) -> list[dict]:
        """Get device infos"""
        # retrieve device list and information as raw XML and convert to XLM tree object
        device_list_xml = self._session.aha_command(SwitchCmd.getdevicelistinfos).text
        device_list_tree = ET.fromstring(device_list_xml)
        # extract relevant information
        device_infos = []
        for device in device_list_tree:
            name = device.find("name").text
            ain = device.items()[0][1]
            dev_id = device.items()[1][1]
            functionbitmask = device.items()[2][1]
            manufacturer = device.items()[4][1]
            productname = device.items()[5][1]
            device_info = {
                "name": name,
                "ain": ain,
                "id": dev_id,
                "functionbitmask": functionbitmask,
                "manufacturer": manufacturer,
                "productname": productname,
            }
            device_infos.append(device_info)
        return device_infos

    ### EXPERIMENTAL: requests to data.lua ###
    def get_web_ui_devices_config(self):
        """Get configuration details for all devices via the web ui"""

        data = f"xhr=1&sid={self.sid}&lang=de&page=sh_dev&xhrId=all"

        response = self._session.web_ui_request(data)
        if response.status_code == 200:
            info_dict = response.json()
            return info_dict
        return response
