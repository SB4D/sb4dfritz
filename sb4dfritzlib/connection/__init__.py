"""Handles communitaction with the FRITZ!Box and connected home
automation devices."""

# AHA-HTTP Interface
from . import http
from . import session
from .session import FritzUser, FritzBoxSession

# TR-064 Interface
from . import tr064
