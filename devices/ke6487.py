import time
from devices.pyvisa_device import device, device_error


class ke6487(device):
    """
    Keithley 6487 pico ammeter.

    Example:
    -------------
    dev = ke6487(address=23)
    print dev.get_idn()
    dev.reset()
    dev.self_test()
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

    def setup_ohmmeter(self, nplc=1, dig=9, range=0, debug=0):
        if debug == 1:
            self.logging.info("Setting up device for volt measurements. Setting range %E, nplc %d and %d digits resolution. [range 0 = autorange]" % (rang, nplc, dig))
        self.ctrl.write("FORM:ELEM READ,UNIT")
        self.ctrl.write("SOUR:VOLT:RANG 10")
        self.ctrl.write("SOUR:VOLT 10")
        self.ctrl.write("SOUR:VOLT:ILIM 2.5e-3")
        self.ctrl.write("SENS:OHMS ON")
        self.ctrl.write("SOUR:VOLT:STAT ON")
        self.ctrl.write("SYST:ZCH OFF")
        return 0

    def setup_ammeter(self, debug=0):
        if debug == 1:
            self.logging.info("Setting up device for current measurements. Setting range %E, nplc %d and %d digits resolution." % (rang, nplc, dig))
        self.ctrl.write("FUNC 'CURR'")
        self.ctrl.write("SYST:ZCH OFF")
        self.ctrl.write(":CURR:RANG:AUTO ON")
        self.ctrl.write(":CURR:RANG:AUTO:ULIM 2E-4")
        self.ctrl.write(":CURR:RANG:AUTO:LLIM 2E-7")
        return 0

    def zero_correction(self):
        print('Nothing there yet.')
        # SYST:ZCH ON ' Enable zero check.'
        # CURR:RANG 2e-9 ' Select the 2nA range.'
        # INIT ' Trigger reading to be used as zero correction'

        # SYST:ZCOR:STAT OFF ' Turn zero correct off.'
        # SYST:ZCOR:ACQ ' Use last reading taken as zero correct value.'
        # SYST:ZCOR ON ' Perform zero correction.'
        # CURR:RANG:AUTO ON ' Enable auto range.'
        # SYST:ZCH OFF ' Disable zero check.'
        return 0



    # Read attribute functions
    # ---------------------------------

    def read_current(self):
        try:
            val = self.ctrl.query("READ?")
            return float(val.split(',')[0][:-1])
        except ValueError:
            print(val.split(','))
            return -1

    def read_resistance(self):
        try:
            val = self.ctrl.query("READ?")
            return float(val.split(',')[1][:-1])
        except ValueError:
            print(val.split(','))
            return -1


## new from here, copied from ke2410
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
        self.ctrl.write(':SOUR:VOLT:STAT ON')
        return 0

    def ramp_down(self, debug=0):
        if debug == 1:
            self.logging.info("Ramping down to 0.00 V.")
        now = float(round(self.read_voltage()))
        ## don't know why this is happening to be honest MARC for v in range(now, 0, -25):
        ## don't know why this is happening to be honest MARC     self.ctrl.write(":SOUR:VOLT %f" % v)
        ## don't know why this is happening to be honest MARC     time.delay(1)
        self.ctrl.write(":SOUR:VOLT 0")
        self.ctrl.write("SOUR:VOLT:STAT OFF")
        return 0

    def ramp_up(self, val, debug=0):
        if debug == 1:
            self.logging.info("Ramping up to %.2f V." % val)
        now = float(round(self.read_voltage()))
        ## don't know why this is necessary for v in range(now, val, +25):
        ## don't know why this is necessary     self.ctrl.write(":SOUR:VOLT %f" % val)
        ## don't know why this is necessary     time.delay(1)
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
        #self.ctrl.write(":FORM:ELEM:SENS VOLT")
        val = self.ctrl.query("READ?").split(',')[-1]
        return float(val)

