def decode_payload_params(params:str):
    payload = {}
    for param in params.split("&"):
        key, val = param.split("=")
        payload[key] = val
    return payload