"""Utilities for preparing device statistics."""

from datetime import datetime

def is_stats_dict(obj):
    """Checks if a given object is a dictionary with keys
    'count', 'grid', 'datatime', 'data'."""
    # check if dictionary
    is_dict = (type(obj) == dict)
    # if so, check keys
    ALLOWED_KEYS = {'count', 'grid', 'datatime', 'data'}
    has_correct_keys = (set(obj.keys()) == ALLOWED_KEYS) if is_dict else False
    return is_dict and has_correct_keys

def prepare_stats_dict(stats):
    """Convert device statistics in dictionaries originating from
    XML string returned by AHA-HTTP interface."""
    # check if 'obj' is dictionary with device statistics
    if not is_stats_dict:
        return stats
    # if so, it has keys the following keys:
    # - 'count'     <- integer as string
    # - 'grid'      <- integer as string
    # - 'datatime'  <- unix timestamp as string
    # - 'data'      <- list of integers as comma separated string
    # convert 'count' and 'grid' to integers
    stats['count'] = int(stats['count'])
    stats['grid'] = int(stats['grid'])
    # convert 'datatime' to datetime
    timestamp = int(stats['datatime'])
    timestamp = datetime.fromtimestamp(timestamp)
    stats['datatime'] = timestamp
    # convert 'data' to list of integers
    data = stats['data']
    data = [int(num) for num in data.split(",")]
    stats['data'] = data 
    return stats
