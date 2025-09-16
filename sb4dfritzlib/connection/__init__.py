"""Handles communitaction with the FRITZ!Box and connected home
automation devices."""

# TR-064 Interface
from . import tr064

# AHA-HTTP Interface
from . import ahahttp
from . import session
from .session import FritzBoxSession
