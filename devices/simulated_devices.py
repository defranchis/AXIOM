import time


class simulatedPsu(object):
    def __init__(self, *args, **kwargs):
        self.v = 0
        self.current_limit = 1
        self.i = 0

    #anytime you try to call a method that isn't already defined
    # just return a dummy function instead
    def __getattr__(self, name):
        def dummy_function(*args, **kwargs):
            pass
        return dummy_function

    def check_voltage_limit(self):
        return 1000

    def set_current_limit(self, i):
        self.i = i

    def check_current_limit(self):
        return self.current_limit

    def ramp_voltage(self, v):
        time.sleep(0.1)
        self.v = v

    def read_current(self):
        return self.i

    def read_voltage(self):
        return self.v


class simulatedMultimeter(object):
    def __init__(self, *args, **kwargs):
        self.v = 0
        self.i = 0

    def __getattr__(self, name):
        def dummy_function(*args, **kwargs):
            pass
        return dummy_function

    def read_current(self):
        return self.i

    def read_voltage(self):
        return self.v


if __name__ == '__main__':
    psu = simulatedPsu()
    psu.reset()
    psu.set_source('voltage')
    psu.set_sense('current')
    psu.set_current_limit(1000)
    psu.set_voltage(0)
    psu.set_terminal('rear')
    psu.set_output_on()
