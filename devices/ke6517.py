import time
from pyvisa_device import device, device_error


class ke6517(device):
    """
    Keithley 6517 electrometer.

    Example:
    -------------
    dev = ke517(address=23)
    print dev.get_idn()
    dev.reset()
    dev.set_range(2E-8)
    print dev.get_range()
    dev.set_nplc(2)
    print dev.get_nplc()
    dev.setup_ammeter()
    print dev.read_current()
    """


    def __init__(self, address):
        device.__init__(self, address=address)
        self.ctrl.write("*RST")

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
        return self.ctrl.write(":SENS:CURR:RANG %E" % val)

    def get_range(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for range settings.")
        return self.ctrl.query(":SENS:CURR:RANG?")

    def set_auto_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current to auto range.")
        return self.ctrl.write(":SENS:CURR:RANG:AUTO %d" % val)

    def get_auto_range(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for auto range settings.")
        return self.ctrl.query(":SENS:CURR:RANG:AUTO?")

    def set_nplc(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting NPLC to %d." % val)
        self.ctrl.write(":SENS:CURR:NPLC %d" % val)
        return 0

    def get_nplc(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for NPLC.")
        return self.ctrl.query(":SENS:CURR:NPLC?")

    def setup_ammeter(self, debug=0):
        if debug == 1:
            self.logging.info("Setting up device for current measurements. Setting range %E, nplc %d and %d digits resolution." % (rang, nplc, dig))
        self.ctrl.write(":SENS:FUNC 'CURR'")
        self.ctrl.write(":SENS:CURR:RANG:AUTO ON")
        self.ctrl.write(":SENS:CURR:RANG:AUTO:LLIM 1E-8)
        self.ctrl.write(":SENS:CURR:RANG:AUTO:ULIM 1E-4)
        self.ctrl.write(":SENS:FUNC:NPLC 1")
        self.ctrl.write(":SYST:ZCH OFF")
        return 0



    # Read attribute functions
    # ---------------------------------

    def read_current(self):
        val = self.ctrl.query("READ?")
        return float(val)
