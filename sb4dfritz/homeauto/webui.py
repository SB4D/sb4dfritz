"""Utilities for interacting via the web ui"""

from enum import Enum


WEB_UI_HEADERS = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,de;q=0.8,nl;q=0.7,fr;q=0.6,it;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "referer": "http://fritz.box/",
    }

class WebUITemplate:
    """Templates for web ui request parameters"""
    Headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9,de;q=0.8,nl;q=0.7,fr;q=0.6,it;q=0.5",
        "content-type": "application/x-www-form-urlencoded",
        "referer": "http://fritz.box/",
    }
    DevicesConfig = {
        "xhr": 1,
        "sid": None,
        "lang": "de",
        "page": "sh_dev",
        "xhrId": "all"
    }
    AutoSwitching = {
        "xhr":"1",
        "sid": None,
        "device": None,
        "switchtimer": None,
        "apply":"",
        "lang":"de",
        "page":"home_auto_timer_view",
    }


class WeekDay(Enum):
    """Enum class for weekdays"""
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6

    def __init__(self, day_id):
        self.id = day_id
        self.bitmask = 1 << self.id


class WeeklyTimerAction:
    """Class for weekly timer actions"""

    def __init__(self, week_day:WeekDay, time_hhmm:str, switch_on:bool):
        self.week_day:WeekDay = week_day
        self.time = time_hhmm
        self.switch_on:bool = switch_on

    @classmethod
    def from_config(cls, action_config):
        """Get user friendly representation of timer action config data"""
        # get week day
        week_day = action_config['timeSetting']['dayOfWeek']
        for day in WeekDay:
            if day.name == week_day:
                week_day = day
                break
        # get time as string (HHMM)
        time = action_config['timeSetting']['startTime']
        time = time.replace(":", "")[:4]
        # get action (on/off)
        action = action_config['description']['action']
        switch_on = True if action=='SET_ON' else False
        return WeeklyTimerAction(week_day, time, switch_on)

def add_weekly_timer_data(timer_config:dict, data:dict):
    # check for weekly timer settings
    try:
        config_weekly = [timer for timer in timer_config if timer['kind']=='WEEKLY_TIMETABLE'][0]
    except IndexError:
        return
    # start processing weekly timer actions
    timer_actions = [WeeklyTimerAction.from_config(action) for action in config_weekly['actions']]
    # parse timer parameter values for post request
    action_times = set([action.time for action in timer_actions])
    action_strings = []
    for time in action_times:
        actions_at_time = [action for action in timer_actions if action.time==time]
        switch_on_state = actions_at_time[0].switch_on
        week_day_bitmask = 0
        for action in actions_at_time:
            assert action.switch_on == switch_on_state
            week_day_bitmask += action.week_day.bitmask
        week_day_bitmask = str(week_day_bitmask)
        switch_on_str = "1" if switch_on_state else "0"
        action_str = ";".join([time, switch_on_str, week_day_bitmask])
        action_strings.append(action_str)
    action_strings = sorted(action_strings)
    # add to data dictionary
    data["graphState"] = 1 #TODO get the previous state
    for n, action in enumerate(action_strings):
        data[f"timer_item_{n}"] = action
