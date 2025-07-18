import time
from pyvisa_device import device, device_error


class ke6510(device):
    """
    Keithley 6510 pico ammeter.

    Example:
    -------------
    dev = ke6510(address=23)
    """


    def __init__(self, address):
        device.__init__(self, address=address)
        self.ctrl.write("*RST")
        self.ctrl.write("*LANG SCPI")

    def print_idn(self, debug=0):
        if debug == 1:
            self.logging.info("Query ID.")
        self.logging.info(self.ctrl.query("*IDN?"))
        return 0

    def get_idn(self):
        return self.ctrl.query("*IDN?")

    def reset(self, debug=0):
        if debug == 1:
            self.logging.info("Reseting device.""")
        self.ctrl.write("*RST")
        return 0

    def clear_status(self, debug=0):
        if debug == 1:
            self.logging("Clearing all status bits.")
        self.ctrl.write("*CLS")
        return 0

    def self_test(self, debug=0):
        if debug == 1:
            self.logging("Executing internal self test.")
        return self.ctrl.query("*TST?")




    # Set attribute functions
    # ---------------------------------

    def set_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current range to %.2EA." % val)
        return self.ctrl.write("CURR:RANG %E" % val)

    def get_range(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for range settings.")
        return self.ctrl.query(":RANG?")

    def set_auto_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current to auto range.")
        return self.ctrl.write(":RANG:AUTO %d" % val)

    def get_auto_range(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for auto range settings.")
        return self.ctrl.query(":RANG:AUTO?")

    def set_digits(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting displayed digits to %.1f." % val)
        return self.ctrl.write(":DISP:DIG %.1f" % val)

    def get_digits(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for digits settings.")
        return self.ctrl.query(":DIG?")

    def set_nplc(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting NPLC to %d." % val)
        self.ctrl.write("CURR:NPLC %d" % val)
        return 0

    def get_nplc(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for NPLC.")
        return self.ctrl.query("CURR:NPLC?")


    def setup_ammeter(self, debug=0):
        if debug == 1:
            self.logging.info("Setting up device for current measurements. Setting range %E, nplc %d and %d digits resolution." % (rang, nplc, dig))
        self.ctrl.write("FUNC 'CURR:DC'")
        self.ctrl.write("CURR:DC:RANG:AUTO ON")
        self.ctrl.write("CURR:DC:RANG:ULIM 2E-4")
        self.ctrl.write("CURR:DC:RANG:LLIM 2E-7")
        self.ctrl.write("CURR:DC:NPLC 1")
        self.ctrl.write("CURR:DC:AZER OFF") # Set autozero function to OFF
        self.ctrl.write("CURR:DC:")
        return 0





    # Read attribute functions
    # ---------------------------------

    def read_current(self):
        try:
            val = self.ctrl.query("READ?")
            return float(val.split(',')[0][:-1])
        except ValueError:
            print val.split(',')
            return -1

    def read_resistance(self):
        try:
            val = self.ctrl.query("READ?")
            return float(val.split(',')[1][:-1])
        except ValueError:
            print val.split(',')
            return -1
