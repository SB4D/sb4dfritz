"""
The various functions of a smart home device (switchable, temperature sensor, etc) 
are encoded in a bit mask. According to the AHA-HTTP documentation (German):

    functionbitmask: Bitmaske der Geräte-Funktionsklassen, beginnen mit Bit 0, es können mehrere Bits gesetzt sein
    Bit 0: HAN-FUN Gerät
    Bit 2: Licht/Lampe
    Bit 4: Alarm-Sensor
    Bit 5: AVM Button
    Bit 6: AVM Heizkörperregler
    Bit 7: AVM Energie Messgerät
    Bit 8: Temperatursensor
    Bit 9: AVM Schaltsteckdose
    Bit 10: AVM DECT Repeater
    Bit 11: AVM Mikrofon
    Bit 13: HAN-FUN-Unit
    Bit 15: an-/ausschaltbares Gerät/Steckdose/Lampe/Aktor
    Bit 16: Gerät mit einstellbarem Dimm-, Höhen- bzw. Niveau-Level
    Bit 17: Lampe mit einstellbarer Farbe/Farbtemperatur
    Bit 18: Rollladen(Blind) - hoch, runter, stop und level 0% bis 100 %
    Bit 20: Luftfeuchtigkeitssensor

    Die Bits 5,6,7,9,10 und 11 werden nur von FRITZ!-Geräten verwendet und nicht von HANFUN- oder Zigbee-Geräten.
    
    Beispiel FD300: binär 101000000(320), Bit6(HKR) und Bit8(Temperatursensor) sind gesetzt
"""

BIT_MASK_DECODER = {
    0: "HAN-FUN device",
    2: "light/lamp",
    4: "alarm sensor",
    5: "AVM button",
    6: "AVM radiator control",
    7: "AVM eneger sensor",
    8: "temperature sensor",
    9: "AVM switch",
    10: "AVM DECT repeater",
    11: "AVM mikrofone",
    13: "HAN-FUN unit",
    15: "switchable device",
    16: "dimmable/adjustable (height, level)",
    17: "lamp with adjustable color temperature",
    18: "blind (up, down, stop, level 0-100)",
    20: "humidity sensor",
}

def decode(num:int)->list[bool]:
    # NOTE `(num >> k) & 1` miraculously returns the k-th bit in the 
    # binary expansion of `num` as an integer
    return [bool((num >> k) & 1) for k in range(24)]

def features(num:int)->list[str]:
    bitmask = decode(num)
    decoded = [BIT_MASK_DECODER[k] for k in BIT_MASK_DECODER if bitmask[k]]
    return decoded
