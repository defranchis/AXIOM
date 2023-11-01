import time, sys
from devices.pyvisa_device import device, device_error


class ke2410(device):
    """
    Keithley 2410 source meter.

    Example:
    -------------
    dev = ke2410(address=24)
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
        #self.ctrl.write("*RST")

    def print_idn(self, debug=0):
        if debug == 1:
            self.logging.info("Query ID.")
        self.logging.info(self.ctrl.query("*IDN?"))
        return 0

    def get_idn(self):
        return self.ctrl.query("*IDN?")

    def reset(self, debug=0):
        if debug == 1:
            self.logging.info("Reseting device.")
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
        if ctrl == 1:
            self.ctrl.write(":SOUR:CLE:AUTO ON")
        else:
            self.ctrl.write(":SOUR:CLE:AUTO OFF")
        return 0

    def check_output(self, debug=0):
        if debug == 1:
            self.logging("Check output.")
        return self.ctrl.query("OUTP:STAT?")

    def set_interlock_on(self, debug=0):
        if debug == 1:
            self.logging("Set interlock on.")
        self.ctrl.write(":OUTP:INT:STAT ON")
        return 0

    def set_interlock_off(self, debug=0):
        if debug == 1:
            self.logging("Set interlock off.")
        self.ctrl.write(":OUTP:INT:STAT OFF")
        return 0

    def check_output(self, debug=0):
        if debug == 1:
            self.logging("Check if interlock tripped.")
        return self.ctrl.query(":OUTP:INT:TRIP?")

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
        now = float(self.read_voltage())
        if debug == 1:
            self.logging.info("Ramping voltage from %.2f V to %.2f V." % (now, val))
        ## MARC if now > val:
        ## MARC     for v in range(now, val, -25):
        ## MARC         self.ctrl.write(":SOUR:VOLT %f" % v)
        ## MARC         time.sleep(1)
        ## MARC         if debug == 1:
        ## MARC             print(self.read_voltage())
        ## MARC     self.ctrl.write(":SOUR:VOLT %f" % val)
        ## MARC else:
        ## MARC     for v in range(now, val, +25):
        ## MARC         self.ctrl.write(":SOUR:VOLT %f" % v)
        ## MARC         time.sleep(1)
        ## MARC         if debug == 1:
        ## MARC             print(self.read_voltage())
        ## MARC     self.ctrl.write(":SOUR:VOLT %f" % val)
        self.ctrl.write(":SOUR:VOLT %f" % val)
        return 0

    def ramp_down(self, debug=0):
        if debug == 1:
            self.logging.info("Ramping down to 0.00 V. in 3 seconds")
        time.sleep(3)
        now = int(round(self.read_voltage()))


        for v in range(now, 0, -10 if now > 0 else 10):
            sys.stdout.write('ramping down to 0 V, currently at {b:4.1f}\r'.format(b=v))
            sys.stdout.flush()
            #print('ramping down to 0 V, currently at {b:4.1f}'.format(b=now))
            self.ctrl.write(":SOUR:VOLT %f" % v)
            time.sleep(1)
            if debug == 1:
                print(self.read_voltage())

        self.ctrl.write(":SOUR:VOLT 0")
        return 0

    def ramp_up(self, val, debug=0):
        if debug == 1:
            self.logging.info("Ramping up to %.2f V." % val)
        now = int(round(self.read_voltage()))
        ## don't know why this is necessary for v in range(now, val, +25):
        ## don't know why this is necessary     self.ctrl.write(":SOUR:VOLT %f" % val)
        ## don't know why this is necessary     time.delay(1)
        for v in range(now, int(val), -10 if now > int(val) else 10):
            sys.stdout.write('ramping to {a} V, currently at {b:4.1f}\r'.format(a=val,b=v))
            sys.stdout.flush()
            #print('ramping down to 0 V, currently at {b:4.1f}'.format(b=now))
            self.ctrl.write(":SOUR:VOLT %f" % v)
            time.sleep(1)
            if debug == 1:
                print(self.read_voltage())
        self.ctrl.write(":SOUR:VOLT %f" % val)
        return 0

    def set_voltage_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting voltage range to %.2fV." % val)
        self.ctrl.write(":SENS:VOLT:RANG %.2f" % val)
        return 0

    def set_current_range(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current range to %E" % val)
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
        self.ctrl.write(':SENS:VOLT:PROT %f' % val)
        return self.ctrl.query(":SENS:VOLT:PROT:LEV?")

    def set_current_limit(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting current limit to %.6fA." % val)
        self.ctrl.write(":SENS:CURR:PROT %f" % val)
        return self.ctrl.query(":SENS:CURR:PROT:LEV?")

    def set_nplc(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting NPLC to %f ." % val)
        self.ctrl.write(":SENSE:CURR:NPLC %f" % val)
        #self.ctrl.write(":SENSE:VOLT:NPLC %f" % val)
        return 0

    def check_voltage_limit(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for voltage limit.")
        return float(self.ctrl.query(":SENS:VOLT:PROT:LEV?"))

    def check_current_limit(self, debug=0):
        if debug == 1:
            self.logging.info("Checking for current limit.")
        return float(self.ctrl.query(":SENS:CURR:PROT:LEV?"))



    # Read attribute functions
    # ---------------------------------

    def read_voltage(self):
        # self.ctrl.write(":SENS:FUNC VOLT")
        self.ctrl.write(":FORM:ELEM:SENS VOLT")
        val = self.ctrl.query(":MEAS:VOLT?")
        return float(val)

    def read_current(self):
        # self.ctrl.write(":SENS:FUNC CURR")
        self.ctrl.write(":FORM:ELEM:SENS CURR")
        val = self.ctrl.query(":MEAS:CURR?")
        return float(val)

    def read_resistance(self):
        # self.ctrl.write(":SENS:FUNC RES")
        self.ctrl.write(":FORM:ELEM:SENS RES")
        val = self.ctrl.query(":MEAS:RES?")
        return float(val)
