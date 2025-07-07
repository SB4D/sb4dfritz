from sb4dfritz import SmartPlug
from time import sleep
from datetime import datetime, timedelta
import random
from scipy.stats import skewnorm
import threading


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


# TODO MAKE THIS CODE LOOK MORE PRETTY
class PowerSimulator:
    """Simulates the power consumption of my coffee machine."""
    def __init__(self):
        self.regions = {
            "idle": (250, 350),
            "mid": (75000, 85000),
            "high": (125000, 135000)
        }

        self.stickiness_by_region = {
            "idle": 0.7,
            "mid": 0.2,
            "high": 0.6,
        }

        self.weights = [0.6, 0.2, 0.2]
        self.region_names = ["idle", "mid", "high"]

        self.current_region = random.choices(
            population=self.region_names,
            weights=self.weights,
            k=1
        )[0]

    def get_current_power(self):
        stickiness = self.stickiness_by_region[self.current_region]
        if random.random() > stickiness:
            # Switch to a new region based on weights
            self.current_region = random.choices(
                population=self.region_names,
                weights=self.weights,
                k=1
            )[0]

        # Generate number in current region
        low, high = self.regions[self.current_region]
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
    
    # STATUS THIS IS LOOKING GOOD
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

    # TODO THE WAY KEAYS ARE DEALT WITH FEELS CLUMSY
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
    
    # TODO FIND A MORE REALISTIC WAY TO GENERATE RANDOM DATA
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



class HomeAutomationDeviceSimulator:
    """Simulates an instance of HomeAutomationDevice in fritzconnection."""

    def __init__(self, name="Smart Plug Simulator"):
        # attributes explicitly used by SmartPlug
        self.DeviceName = name 
        self.Manufacturer = "SB4D" 
        self.ProductName = "FRITZ! Smart Plug Simulator"
        self.identifier = "12345 1234567"
        # attributes implicitly used by SmartPlug 
        # by way of the methods below
        self._switch_state = True
        self.sensor:MeasurementSimulator = MeasurementSimulator()
    
    def is_switchable(self):
        """Checks whether a switchable device is simulated."""
        # Assuming that all devices are smart plugs...
        return True

    def get_switch_state(self):
        """Check whether the simulated device's power switch 
        is on or off."""
        return self.__switch_state
    
    def set_switch(self,target_state:bool):
        """Sets the power switch state of the simulated device."""
        self._switch_state = target_state
    
    def get_basic_device_stats(self):
        # add a bit of latency
        add_network_latency()
        # send request for device stats
        return self.sensor.send_basic_device_stats()


if __name__ == "__main__":
    plug_simulator = HomeAutomationDeviceSimulator()

    simulated_plug = SmartPlug(plug_simulator)

    print(simulated_plug.get_basic_device_stats())

