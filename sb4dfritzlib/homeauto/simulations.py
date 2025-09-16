from .devicemodels import HomeAutoDevice, HomeAutoSystem
import random
from time import sleep
from datetime import datetime, timedelta
from scipy.stats import skewnorm
import threading


def choose_random_string_of_integers(length:int)->str:
    random_integers = [random.randint(0, 9) for _ in range(length)]
    integer_string = ''.join(str(num) for num in random_integers)
    return integer_string

def generate_random_boolean():
    random_bool = random.choice([True, False])
    return random_bool

def generate_fake_sid():
    fake_sid = choose_random_string_of_integers(16)
    return fake_sid

def generate_fake_ain():
    # generate first five numbers
    fake_ain = choose_random_string_of_integers(5)
    # add space
    fake_ain += " "
    # generate remaining seven numbers
    fake_ain += choose_random_string_of_integers(7)
    return fake_ain

def add_network_latency(one_way=True):
    """Simulates network latency by sampling from a skew normal distribution."""
    # get sample from a suitable skew normal distribution
    two_way_latency = skewnorm.rvs(5, loc=0.74, scale=0.1, size=1)[0]
    # determine latency
    if one_way:
        latency = two_way_latency / 2
    else:
        latency = two_way_latency
    # wait a bit
    sleep(latency)


class SmartPlugSimulator(HomeAutoDevice):

    def __init__(self, name="Smart Home Simulator", id=None):
        # shared with HomeAutomationDevice
        self.sid = generate_fake_sid()
        self.ain = generate_fake_ain()
        self.name = name
        self.model = "Smart Plug Simulator"
        self.device_id = id if id else random.randint(1,16)
        # needed for simulation
        self.is_switchable = True
        self.__switch_state = True
        self.sensor:MeasurementSimulator = MeasurementSimulator()
    
    def get_switch_state(self)->bool:
        """Get current switch state (on=True ,off=False)."""
        return self.__switch_state

    def set_switch(self, state:bool)->bool:
        """Set switch state if switchable (on=True ,off=False)."""
        self.__switch_state = state 
        return state

    def toggle_switch(self)->bool:
        """Toggle switch state if switchable."""
        current_state = self.get_switch_state()
        new_state = not current_state
        self.__switch_state = new_state
        return self.get_switch_state()
    
    def get_basic_device_stats(self):
        # add a bit of latency
        add_network_latency()
        # send request for device stats
        return self.sensor.send_basic_device_stats()



class HomeAutoSystemSimulator(HomeAutoSystem):
    pass



# TODO MAKE THIS CODE LOOK MORE PRETTY
class PowerSimulator:
    """Simulates the power consumption of my coffee machine."""

    def __init__(self):
        """Simulates the power consumption of my coffee machine."""
        # states of power consumption
        self.states = ["idle", "mid", "high"]
        # current state (start with "high" consumption)
        self.current_state = "high"
        # ranges for power consumption (unit 0.01 W)
        self.state_ranges = {
            "idle": (300, 350),         #  3.0 to  3.5 W
            "mid": (40000, 85000),      #  400 to  850 W
            "high": (125000, 135000),   # 1250 to 1350 W
        }
        # probability to stick to a state
        self.stickiness_by_state = {
            "idle": 0.7,
            "mid": 0.2,
            "high": 0.6,
        }
        # probability that state is chosen
        self.chances_by_state = {
            "idle": 0.4,
            "mid": 0.3,
            "high": 0.3,
        }
    
    def select_new_state(self):
        new_region = random.choices(
            population=self.states,
            weights=self.chances_by_state.values(),
            k=1
        )[0]
        return new_region


    def get_current_power(self):
        stickiness = self.stickiness_by_state[self.current_state]
        if random.random() > stickiness:
            # Switch to a new region based on weights
            self.current_state = self.select_new_state()

        # Generate number in current region
        low, high = self.state_ranges[self.current_state]
        return random.randint(low, high)



class MeasurementSimulator():
    """Simulates the measurement mechanism in FRITZ! smart plugs and produces
    "basic_device_stats" in the fritzconnection dictionary format."""
    
    def __init__(self):
        # simulate connected appliances
        self.appliances:PowerSimulator = PowerSimulator()
        # set measure cycle base time
        self.cycle_base_time = None
        self.reset_cycle_base_time()
        # set device stats
        self.basic_device_stats = None
        self._generate_basic_device_stats()
        # attributes needed for sleep mode
        self.sleeping = False
        self._lock = threading.Lock()
        self._timer = None
        # keep awake after initialization
        self.stay_awake()
    
    def _generate_basic_device_stats(self):
        # generate template
        device_stats = self._generate_basic_device_stats_template()
        # generate sufficient data
        cats = device_stats.keys()
        max_count = max([device_stats[cat]['count'] for cat in cats])
        data = {cat:[] for cat in cats}
        for i in range(max_count):
            new_data = self._generate_measure_data()
            for cat in cats:
                data[cat].append(new_data[cat])
        # fill device_stats with the right amounts of data
        for cat in cats:
            cat_count = device_stats[cat]['count'] 
            device_stats[cat]['data'] = data[cat][:cat_count]
        # pass to the basic_device_stats attribute
        self.basic_device_stats = device_stats

    def _generate_basic_device_stats_template(self):
        # designated dictionary keys
        LEVEL_1_KEYS = ['temperature', 'voltage', 'power', 'energy']
        LEVEL_2_KEYS = ['count', 'grid', 'datatime', 'data']
        # designates values for 'count' and 'grid' in order of LEVEL_1_KEYS
        COUNT_VALUES = [96, 360, 360, 12]
        GRID_VALUES = [900, 10, 10, 2678400]
        # initializing the nested dictionary
        level2_template = {key2:None for key2 in LEVEL_2_KEYS}
        device_stats = {key1:level2_template.copy() for key1 in LEVEL_1_KEYS}
        # adding in the values in level 2
        for idx, category in enumerate(LEVEL_1_KEYS):
            device_stats[category]['count'] = COUNT_VALUES[idx]
            device_stats[category]['grid'] = GRID_VALUES[idx]
            device_stats[category]['datatime'] = self.cycle_base_time.replace(microsecond=0)
            device_stats[category]['data'] = []
        return device_stats
    
    # TODO consider loading actual sample data
    def _generate_measure_data(self):
        data_categories = ['temperature', 'voltage', 'power', 'energy']
        data = {cat:0 for cat in data_categories}
        data['power'] = self.appliances.get_current_power()
        return data
    
    def send_basic_device_stats(self):
        # wake up on request
        self.stay_awake()
        # reset measure cycle base time if sleeping
        if self.sleeping:
            self.reset_cycle_base_time()
        # update data
        self._update_basic_device_stats()
        # add a bit of latency
        add_network_latency()
        # send current device stats
        return self.basic_device_stats
    
    # TODO TEST THIS !!!
    def _update_basic_device_stats(self):
        device_stats = self.basic_device_stats
        current_time = datetime.now()
        for cat in device_stats.keys():
            old_data = device_stats[cat]['data']
            old_datatime = device_stats[cat]['datatime']
            grid = device_stats[cat]['grid']
            grid_delta = timedelta(seconds=grid)
            # update datatime
            new_datatime = old_datatime
            cycles_passed = 0
            while new_datatime + grid_delta <= current_time:
                cycles_passed += 1
                new_datatime += grid_delta
            device_stats[cat]['datatime'] = new_datatime.replace(microsecond=0)
            # add new data values
            new_data = old_data
            for _ in range(cycles_passed):
                new_value = self._generate_measure_data()[cat]
                new_data = [new_value] + new_data
                new_data = new_data[:-1]
            # update data in device_stats
            device_stats[cat]['data'] = new_data
        # update basic_device_stats
        self.basic_device_stats = device_stats

    
    def reset_cycle_base_time(self):
        # get current time minus one second
        t = datetime.now() + timedelta(seconds=-1)
        # replace the microsecond component with a random value
        t = t.replace(microsecond=random.randint(0,1000000))
        # update the cycle base time
        self.cycle_base_time = t

    def stay_awake(self, awake_time=300):
        if self.sleeping:
            self.reset_cycle_base_time()
        with self._lock:
            self.sleeping = False
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(awake_time, self._go_to_sleep)
            self._timer.daemon = True
            self._timer.start()

    def _go_to_sleep(self):
        with self._lock:
            self.sleeping = True
