from enum import Enum


class SwitchCmd(Enum):
    getswitchlist = {"switchcmd":"getswitchlist", "sid":None}
    setswitchon = {"switchcmd":"setswitchon", "sid":None, "ain":None}
    setswitchoff = {"switchcmd":"setswitchoff", "sid":None, "ain":None}
    setswitchtoggle = {"switchcmd":"setswitchtoggle", "sid":None, "ain":None}
    getswitchstate = {"switchcmd":"getswitchstate", "sid":None, "ain":None}
    getswitchpresent = {"switchcmd":"getswitchpresent", "sid":None, "ain":None}
    getswitchpower = {"switchcmd":"getswitchpower", "sid":None, "ain":None}
    getswitchenergy = {"switchcmd":"getswitchenergy", "sid":None, "ain":None}
    getswitchname = {"switchcmd":"getswitchname", "sid":None, "ain":None}
    getdevicelistinfos = {"switchcmd":"getdevicelistinfos", "sid":None, "ain":None}
    gettemperature = {"switchcmd":"gettemperature", "sid":None, "ain":None}
    gethkrtsoll = {"switchcmd":"gethkrtsoll", "sid":None, "ain":None, "param":None}
    gethkrkomfort = {"switchcmd":"gethkrkomfort", "sid":None, "ain":None}
    gethkrabsenk = {"switchcmd":"gethkrabsenk", "sid":None, "ain":None}
    sethkrtsoll = {"switchcmd":"sethkrtsoll", "sid":None, "ain":None}
    getbasicdevicestats = {"switchcmd":"getbasicdevicestats", "sid":None, "ain":None}
    gettriggerlistinfos = {"switchcmd":"gettriggerlistinfos", "sid":None}
    settriggeractive = {"switchcmd":"settriggeractive", "sid":None, "ain":None, "active":None}
    gettemplatelistinfos = {"switchcmd":"gettemplatelistinfos", "sid":None}
    applytemplate = {"switchcmd":"applytemplate", "sid":None, "ain":None}
    setsimpleonoff = {"switchcmd":"setsimpleonoff", "sid":None, "ain":None, "onoff":None}
    setlevel = {"switchcmd":"setlevel", "sid":None, "ain":None, "level":None}
    setlevelpercentage = {"switchcmd":"setlevelpercentage", "sid":None, "ain":None, "level":None}
    setcolor = {"switchcmd":"setcolor", "sid":None, "ain":None, "hue":None, "saturation":None, "duration":None}
    setunmappedcolor = {"switchcmd":"setunmappedcolor", "sid":None, "ain":None, "hue":None, "saturation":None, "duration":None}
    setcolortemperature = {"switchcmd":"setcolortemperature", "sid":None, "ain":None, "temperature":None, "duration":None}
    addcolorleveltemplate = {"switchcmd":"addcolorleveltemplate", "sid":None, "ain":None}
    getcolordefaults = {"switchcmd":"getcolordefaults", "sid":None}
    sethkrboost = {"switchcmd":"sethkrboost", "sid":None, "ain":None, "endtimestamp":None}
    sethkrwindowopen = {"switchcmd":"sethkrwindowopen", "sid":None, "ain":None, "endtimestamp":None}
    setblind = {"switchcmd":"setblind", "sid":None, "ain":None, "target":None}
    setname = {"switchcmd":"setname", "sid":None, "ain":None, "name":None}
    setmetadata = {"switchcmd":"setmetadata", "sid":None, "ain":None, "metadata":None}
    startulesubscription = {"switchcmd":"startulesubscription", "sid":None}
    getsubscriptionstate = {"switchcmd":"getsubscriptionstate", "sid":None}
    getdeviceinfos = {"switchcmd":"getdeviceinfos", "sid":None, "ain":None}


class FunctionBitMask:

    def __init__(self, functionbitmask:int|str):
        # convert to integer if needed
        try:
            functionbitmask = int(functionbitmask)
        except:
            ValueError("Argument must be integer or convertible using int(...)")
        # convert to bit string (big endian)
        bits = format(functionbitmask, '024b')[::-1]
        # converts to list of booleans
        bools = [bool(int(bit)) for bit in bits]
        # interpret bit flags
        self.han_fun_device = bools[0]
        self.light = bools[2]
        self.alarm = bools[4]
        self.button = bools[5]
        self.temp_control = bools[6]
        self.energy_sensor = bools[7]
        self.temp_sensor = bools[8]
        self.outlet = bools[9]
        self.dect_repeater = bools[10]
        self.microphone = bools[11]
        self.han_fun_unit = bools[13]
        self.switchable = bools[15]
        self.adjustable_level = bools[16]
        self.adjustable_color = bools[17]
        self.blind = bools[18]
        self.humidity_sensor = bools[20]