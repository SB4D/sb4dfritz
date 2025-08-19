"""Handles communitaction with the FRITZ!Box and connected home
automation devices."""

# AHA-HTTP Interface
from . import http
from .http import aha_request
from ._login import get_sid

# TR-064 Interface
from . import tr064
