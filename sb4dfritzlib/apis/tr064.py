import requests, warnings
from requests.auth import HTTPDigestAuth


def get_specific_device_info(user:str, pwd:str, ip:str, device_ain:str)->requests.Response:
    """GetSpecificDeviceInfos action for TR-064 interfaces."""
    UPNP_URL = "https://" + ip + ":49443/upnp/control/x_homeauto"
    TR064_SERVICE = "urn:dslforum-org:service:X_AVM-DE_Homeauto:1"
    SOAP_ACTION = "GetSpecificDeviceInfos"
    # header for POST request
    request_headers = {
        'Content-Type': 'text/xml; charset="utf-8"', 
        'SoapAction': TR064_SERVICE + "#" + SOAP_ACTION
        # 'SoapAction': 'urn:dslforum-org:service:X_AVM-DE_Homeauto:1#GetSpecificDeviceInfos'
    }
    # data for POST request
    request_data = f"""
        <?xml version=\"1.0\"?> 
        <s:Envelope 
         xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" 
         s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"> 
            <s:Body> 
                <u:{SOAP_ACTION} xmlns:u=\"{TR064_SERVICE}\"> 
                    <NewAIN>{device_ain}</NewAIN> 
                </u:{SOAP_ACTION}> 
            </s:Body> 
        </s:Envelope>
        """
    # temporary ignore warnings (caused by self-signed certificate of FRITZ!Box)
    warnings.simplefilter('ignore')
    # send POST request
    request_result = requests.post(
        url=UPNP_URL, 
        auth=HTTPDigestAuth(user, pwd), 
        headers=request_headers, 
        data=request_data, 
        verify=False
    )
    # allow warning again
    warnings.resetwarnings()
    return request_result


def set_switch(user:str, pwd:str, ip:str, device_ain:str, target_state:str)->requests.Response:
    """GetSpecificDeviceInfos action for TR-064 interfaces."""
    UPNP_URL = "https://" + ip + ":49443/upnp/control/x_homeauto"
    TR064_SERVICE = "urn:dslforum-org:service:X_AVM-DE_Homeauto:1"
    SOAP_ACTION = "SetSwitch"

    ALLOWED_STATES = ["ON", "OFF", "TOGGLE"]
    if not target_state in ALLOWED_STATES:
        print("Target state must be 'ON', 'OFF', or 'TOGGLE'.")
        return
    # header for POST request
    request_headers = {
        'Content-Type': 'text/xml; charset="utf-8"', 
        'SoapAction': TR064_SERVICE + "#" + SOAP_ACTION
        # 'SoapAction': 'urn:dslforum-org:service:X_AVM-DE_Homeauto:1#GetSpecificDeviceInfos'
    }
    # data for POST request
    request_data = f"""
        <?xml version=\"1.0\"?> 
        <s:Envelope 
         xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" 
         s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"> 
            <s:Body> 
                <u:{SOAP_ACTION} xmlns:u=\"{TR064_SERVICE}\"> 
                    <NewAIN>{device_ain}</NewAIN> 
                    <NewSwitchState>{target_state}</NewSwitchState> 
                </u:{SOAP_ACTION}> 
            </s:Body> 
        </s:Envelope>
        """
    # temporary ignore warnings (caused by self-signed certificate of FRITZ!Box)
    warnings.simplefilter('ignore')
    # send POST request
    request_result = requests.post(
        url=UPNP_URL, 
        auth=HTTPDigestAuth(user, pwd), 
        headers=request_headers, 
        data=request_data, 
        verify=False
    )
    # allow warning again
    warnings.resetwarnings()
    return request_result


def get_generic_device_infos(user:str, pwd:str, ip:str, device_index:str)->requests.Response:
    """GetSpecificDeviceInfos action for TR-064 interfaces."""
    UPNP_URL = "https://" + ip + ":49443/upnp/control/x_homeauto"
    TR064_SERVICE = "urn:dslforum-org:service:X_AVM-DE_Homeauto:1"
    SOAP_ACTION = "GetGenericDeviceInfos"
    # header for POST request
    request_headers = {
        'Content-Type': 'text/xml; charset="utf-8"', 
        'SoapAction': TR064_SERVICE + "#" + SOAP_ACTION
        # 'SoapAction': 'urn:dslforum-org:service:X_AVM-DE_Homeauto:1#GetSpecificDeviceInfos'
    }
    # data for POST request
    request_data = f"""
        <?xml version=\"1.0\"?> 
        <s:Envelope 
         xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" 
         s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"> 
            <s:Body> 
                <u:{SOAP_ACTION} xmlns:u=\"{TR064_SERVICE}\"> 
                    <NewIndex>{device_index}</NewIndex> 
                </u:{SOAP_ACTION}> 
            </s:Body> 
        </s:Envelope>
        """
    # temporary ignore warnings (caused by self-signed certificate of FRITZ!Box)
    warnings.simplefilter('ignore')
    # send POST request
    request_result = requests.post(
        url=UPNP_URL, 
        auth=HTTPDigestAuth(user, pwd), 
        headers=request_headers, 
        data=request_data, 
        verify=False
    )
    # allow warning again
    warnings.resetwarnings()
    return request_result


def get_info(user:str, pwd:str, ip:str)->requests.Response:
    """GetInfo action for TR-064 interfaces."""
    UPNP_URL = "https://" + ip + ":49443/upnp/control/x_homeauto"
    TR064_SERVICE = "urn:dslforum-org:service:X_AVM-DE_Homeauto:1"
    SOAP_ACTION = "GetInfo"
    # header for POST request
    request_headers = {
        'Content-Type': 'text/xml; charset="utf-8"', 
        'SoapAction': TR064_SERVICE + "#" + SOAP_ACTION
        # 'SoapAction': 'urn:dslforum-org:service:X_AVM-DE_Homeauto:1#GetSpecificDeviceInfos'
    }
    # data for POST request
    request_data = f"""
        <?xml version=\"1.0\"?> 
        <s:Envelope 
         xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" 
         s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"> 
            <s:Body> 
                <u:{SOAP_ACTION} xmlns:u=\"{TR064_SERVICE}\"> 
                </u:{SOAP_ACTION}> 
            </s:Body> 
        </s:Envelope>
        """
    # temporary ignore warnings (caused by self-signed certificate of FRITZ!Box)
    warnings.simplefilter('ignore')
    # send POST request
    request_result = requests.post(
        url=UPNP_URL, 
        auth=HTTPDigestAuth(user, pwd), 
        headers=request_headers, 
        data=request_data, 
        verify=False
    )
    # allow warning again
    warnings.resetwarnings()
    return request_result

