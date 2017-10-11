import time
from pyvisa_device import device, device_error


class ke2450(device):
    """
    Keithley 2450 source meter.

    Example:
    -------------
    dev = ke2450(address=24)
    dev.print_idn()
    dev.set_source('voltage')
    dev.set_voltage(10)
    dev.set_sense('current')
    dev.set_current_limit(0.00005)
    dev.set_output_on()
    print dev.read_current()
    print dev.read_voltage()
    print dev.read_resistance()
    dev.set_output_off()
    dev.reset()
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



    # Output functions
    # ---------------------------------

    def set_output_on(self, debug=0):
        if debug == 1:
            self.logging("Set output on.")
        self.ctrl.write("OUTP ON")
        return 0

    def set_output_off(self, debug=0):
        if debug == 1:
            self.logging("Set output off.")
        self.ctrl.write("OUTP OFF")
        return 0

    def set_output_auto(self, ctrl=0, debug=0):
        if debug == 1:
            self.logging("Set output to auto.")
        if cntr == 1:
            self.ctrl.write(":SOUR:CLE:AUTO ON")
        else:
            self.ctrl.write(":SOUR:CLE:AUTO OFF")
        return 0

    def check_output(self, debug=0):
        if debug == 1:
            self.logging("Check output.")
        return self.ctrl.query("OUTP:STAT?")

    def set_terminal(self, term, debug=0):
        if debug == 1:
            self.logging("Set terminal to %s. Options are [front, rear]." % term)
        if term =='front':
            self.ctrl.write(":ROUT:TERM FRON")
            return 0
        elif term =='rear':
            self.ctrl.write(":ROUT:TERM REAR")
            return 0
        else:
            self.logging.info("This terminal doesn't exist on this device.")
            return -1

    def check_terminal(self, debug=0):
        if debug == 1:
            self.logging("Check terminals.")
        return self.ctrl.query(":ROUT:TERM?")



    # Set attribute functions
    # ---------------------------------

    def set_voltage(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting voltage to %.2fV." % val)
        self.ctrl.write(":SOUR:VOLT %f" % val)
        return 0

    def set_current(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current to %.6fA." % val)
        self.ctrl.write(":SOUR:CURR %f" % val)
        return 0

    def ramp_voltage(self, val, debug=0):
        now = int(round(self.read_voltage()))
        if debug == 1:
            self.logging.info("Ramping voltage from %.2f V to %.2f V." % (now, val))
        if now > val:
            for v in range(now, val, -25):
                self.ctrl.write(":SOUR:VOLT %d" % v)
                time.sleep(1)
                if debug == 1:
                    print self.read_voltage()
            self.ctrl.write(":SOUR:VOLT %d" % val)
        else:
            for v in range(now, val, +25):
                self.ctrl.write(":SOUR:VOLT %d" % v)
                time.sleep(1)
                if debug == 1:
                    print self.read_voltage()
            self.ctrl.write(":SOUR:VOLT %d" % val)
        return 0

    def ramp_down(self, debug=0):
        if debug == 1:
            self.logging.info("Ramping down to 0.00 V.")
        now = int(round(self.read_voltage()))
        for v in range(now, 0, -25):
            self.ctrl.write(":SOUR:VOLT %f" % v)
            time.delay(1)
        self.ctrl.write(":SOUR:VOLT 0")
        return 0

    def ramp_up(self, val, debug=0):
        if debug == 1:
            self.logging.info("Ramping up to %.2f V." % val)
        now = int(round(self.read_voltage()))
        for v in range(now, val, +25):
            self.ctrl.write(":SOUR:VOLT %f" % val)
            time.delay(1)
        self.ctrl.write(":SOUR:VOLT %f" % val)
        return 0

    def set_voltage_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting voltage range to %.2fV." % val)
        self.ctrl.write(":SENS:VOLT:RANG %.2f" % val)
        return 0

    def set_current_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current range to %.2EA." % val)
        self.ctrl.write(":SENS:CURR:RANG %E" % val)
        return 0

    def check_compliance(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for compliance.")
        return self.ctrl.query(":SENS:CURR:PROT:TRIP?")

    def set_sense(self, prop, debug=0):
        if prop == 'voltage':
            if debug == 1:
                self.logging.info("Setting sense to voltage.")
            self.ctrl.write(":SENS:FUNC 'VOLT' ")
        elif prop == 'current':
            if debug == 1:
                self.logging.info("Setting sense to current.")
            self.ctrl.write(":SENS:FUNC 'CURR' ")
        elif prop == 'resistance':
            if debug == 1:
                self.logging.info("Setting sense to resistance.")
            self.ctrl.write(":SENS:FUNC 'RES' ")
        else:
            self.logging.info("Choosen property cannot be measured by this device.")
            return -1

    def set_source(self, prop, debug=0):
        if prop == 'voltage':
            if debug == 1:
                self.logging.info("Setting source to voltage.")
            self.ctrl.write(":SOUR:FUNC VOLT")
        elif prop == 'current':
            if debug == 1:
                self.logging.info("Setting source to current.")
            self.ctrl.write(":SOUR:FUNC CURR")
        else:
            self.logging.info("Choosen property cannot be supplied by this device.")
            return -1

    def set_voltage_limit(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting voltage limit to %.2fV." % val)
        self.ctrl.write(':SOUR:VOLT:ILIM %f' % val)
        return self.ctrl.query(":SOUR:VOLT:ILIM:LEV?")

    def set_current_limit(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current limit to %.6fA." % val)
        self.ctrl.write(':SOUR:CURR:VLIM %f' % val)
        return self.ctrl.query(":SOUR:CURR:VLIM:LEV?")

    def set_outout_state(self, state, debug=0):
        if debug == 1:
            self.logging.info("Setting output mode to %s. Options are [NORM, ZERO, HIMP, GUAR]." % state)
        self.ctrl.write(':OUTP:SMOD %s' % state)

    def set_nplc(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting NPLC to %d." % val)
        self.ctrl.write(":SENSE:CURR:NPLC %d" % val)
        self.ctrl.write(":SENSE:VOLT:NPLC %d" % val)
        return 0



    # Read attribute functions
    # ---------------------------------

    def read_voltage(self):
        # self.ctrl.write(":SENS:FUNC VOLT")
        #self.ctrl.write(":FORM:ELEM:SENS VOLT")
        val = self.ctrl.query(":MEAS:VOLT?")
        return float(val)

    def read_current(self):
        # self.ctrl.write(":SENS:FUNC CURR")
        val = self.ctrl.query(":MEAS:CURR?")
        return float(val)

    def read_resistance(self):
        # self.ctrl.write(":SENS:FUNC RES")
        #self.ctrl.write(":FORM:ELEM:SENS RES")
        val = self.ctrl.query(":MEAS:RES?")
        return float(val)
