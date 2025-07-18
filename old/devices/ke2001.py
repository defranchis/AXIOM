import time
from pyvisa_device import device, device_error


class ke2001(device):
    """ 
    Keithley 2001 multimeter.
    
    Example:
    -------------
    dev = ke2001(address=24)
    dev.print_idn()
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
    
    def clear_status(self, debug=0):
        if debug == 1: 
            self.logging("Clearing all status bits.")
        self.ctrl.write("*CLS")
        return 0

    def self_test(self, debug=0):
        if debug == 1: 
            self.logging("Executing internal self test.")
        return self.ctrl.query("*TST?") 
    
    
    # Output functions
    # ---------------------------------

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
            self.logging.info("Choosen property cannot be measured by this device or is not implemented. Your options are ['voltage', 'current', 'resistoance', 'temperature'].")
            return -1

    def set_nplc(self, val, debug=0):
        if debug == 1: 
            self.logging.info("Setting NPLC to %d." % val)
        self.ctrl.write(":SENSE:CURR:NPLC %d" % val) 
        self.ctrl.write(":SENSE:VOLT:NPLC %d" % val)  
        return 0

    def check_nplc(self, debug=0):
        if debug == 1: 
            self.logging.info("Checking for NPLC.")
        return self.ctrl.write(":SENSE:VOLT:NPLC?"), self.ctrl.write(":SENSE:CURR:NPLC?")

    def setup_voltmeter(self, nplc=1, dig=9, range=0, debug=0):
        if debug == 1: 
            self.logging.info("Setting up device for volt measurements. Setting range %E, nplc %d and %d digits resolution. [range 0 = autorange]" % (rang, nplc, dig))
        self.ctrl.write(":SENS:VOLT")
        if rang == 0:
            self.ctrl.write(":SENS:VOLT:RANG AUTO")
        else:
            self.ctrl.write(":SENS:VOLT:RANG %E" % rang)
        self.ctrl.write(":SENS:VOLT:DIG %d" % dig)
        self.ctrl.write(":SENS:VOLT:NPLC %d" % nplc)
        return 0

    def setup_ammeter(self, nplc=1, dig=9, rang=0, debug=0):
        if debug == 1: 
            self.logging.info("Setting up device for current measurements. Setting range %E, nplc %d and %d digits resolution." % (rang, nplc, dig))
        #self.ctrl.write(":SENS:CURR")
        #if rang == 0:
        #    self.ctrl.write(":SENS:CURR:RANG AUTO 1")
        #else:
        #    self.ctrl.write(":SENS:CURR:RANG %E" % rang)
        self.ctrl.write(":CURR:DIG %d" % dig)
        self.ctrl.write(":CURR:NPLC %d" % nplc)
        return 0

        # :RANG?
        # :RANG:AUTO? 
        # :DIG?
        # :DIG:AUTO <b>
        # :DIG:AUTO?



    # Read attribute functions
    # ---------------------------------

    def read_voltage(self):
        val = self.ctrl.query(":MEAS:VOLT?")
        return float(val)

    def read_voltage_ac(self):
        val = self.ctrl.query(":MEAS:VOLT:AC?")
        return float(val)

    def read_current(self):
        val = self.ctrl.query(":MEAS:CURR?")
        return float(val[0:11])


    def read_current_ac(self):
        val = self.ctrl.query(":MEAS:CURR:AC?")
        return float(val)

    def read_resistance(self):
        val = self.ctrl.query(":MEAS:RES?")
        return float(val)

    def read_temperature(self):
        val = self.ctrl.query(":MEAS:TEMP?")
        return float(val)

    def read_frequency(self):
        val = self.ctrl.query(":MEAS:FREQ?")
        return float(val)


