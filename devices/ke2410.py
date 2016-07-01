# ============================================================================
# File: ke2410.py
# -----------------------
# Communication for Keithley 2410 source meter.
# 
# Date: 06.06.2016
# Author: Florian Pitters
#
# ============================================================================

from pyvisa_device import device, device_error


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
        self.ctrl.write("*RST")
    
    def print_idn(self):
        self.logging("Query ID.")
        self.logging(self.ctrl.query("*IDN?"))
        return 0
    
    def get_idn(self):
        return self.ctrl.query("*IDN?")
    
    def reset(self):
        self.logging("Reseting device."""
        self.ctrl.write("*RST")
        return 0
    
    
    
    # Output functions
    # ---------------------------------

    def set_output_on(self):
        self.ctrl.write("OUTP ON")
        return 0

    def set_output_off(self):
        self.ctrl.write("OUTP OFF")
        return 0
        
    def set_output_auto(self, ctrl=0):
        if cntr == 1:
            self.ctrl.write(":SOUR:CLE:AUTO ON")
        else:
            self.ctrl.write(":SOUR:CLE:AUTO OFF")
        
    def check_output(self):
        return self.ctrl.query("OUTP:STAT?")
    
    def set_terminal(self, term):
        if term =='front':
            self.ctrl.write(":ROUT:TERM FRON")
            return 0
        elif term =='rear':
            self.ctrl.write(":ROUT:TERM REAR")
            return 0
        else:
            self.logging("This terminal doesn't exist on this device.")
            # rise some error
            return -1
     
    def check_terminal(self):
        return self.ctrl.query(":ROUT:TERM?")



    # Set attribute functions
    # ---------------------------------

    def set_voltage(self, val):
        self.logging("Setting voltage to %.2fV." % val)
        self.ctrl.write(":SOUR:VOLT %f" % val)
        return 0

    def set_current(self, val):
        self.logging("Setting current to %.6fA." % val)
        self.ctrl.write(":SOUR:CURR %f" % val)
        return 0

    def set_voltage_limit(self, val):
        self.logging("Setting voltage limit to %.2fV." % val)
        self.ctrl.write(':SENS:VOLT:PROT %f' % val)
        return self.ctrl.query(":SENS:CURR:PROT:TRIP?")

    def set_current_limit(self, val):
        self.logging("Setting current limit to %.6fA." % val)
        self.ctrl.write(":SENS:CURR:PROT %f" % val)
        return self.ctrl.query(":SENS:CURR:PROT:TRIP?")
    
    def set_voltage_range(self, val):
        self.ctrl.write(":SENS:VOLT:RANG %.2f" % val)
        return 0
    
    def set_current_range(self, val):
        self.ctrl.write(":SENS:CURR:RANG %.6f" % val)
        return 0

    def check_compliance(self):
        self.logging("Checking for compliance.")
        return self.ctrl.query(":SENS:CURR:PROT:TRIP?")

    def set_sense(self, prop):
        if prop == 'voltage':
            self.logging("Setting sense to voltage.")
            self.ctrl.write(":SENS:FUNC 'VOLT' ")
        elif prop == 'current':
            self.logging("Setting sense to current.")
            self.ctrl.write(":SENS:FUNC 'CURR' ")
        elif prop == 'resistance':
            self.logging("Setting sense to resistance.")
            self.ctrl.write(":SENS:FUNC 'RES' ")
        else:
            self.logging("Choosen property cannot be measured by this device.")
            # rise some error
            return -1

    def set_source(self, prop):
        if prop == 'voltage':
            self.logging("Setting source to voltage.")
            self.ctrl.write(":SOUR:FUNC VOLT")
        elif prop == 'current':
            self.logging("Setting source to current.")
            self.ctrl.write(":SOUR:FUNC CURR")
        else:
            self.logging("Choosen property cannot be supplied by this device.")
            # rise some error
            return -1



    # Read attribute functions
    # ---------------------------------

    def read_voltage(self):
        self.ctrl.write(":SENS:FUNC VOLT")
        self.ctrl.write(":FORM:ELEM:SENS VOLT")
        val = self.ctrl.query(":MEAS:VOLT:DC?")
        return float(val)

    def read_current(self):
        self.ctrl.write(":SENS:FUNC CURR")
        self.ctrl.write(":FORM:ELEM:SENS CURR")
        val = self.ctrl.query(":MEAS:CURR:DC?")
        return float(val)

    def read_resistance(self):
        self.ctrl.write(":SENS:FUNC RES")
        self.ctrl.write(":FORM:ELEM:SENS RES")
        val = self.ctrl.query(":MEAS:RES?")
        return float(val)
        


# self.ctrl.write("SOUR:VOLT:READ:BACK ON")
# self.ctrl.write("SENS:VOL:UNIT VOL")
# self.wr("SOUR:VOLT %.4f"%voltage)
# self.wr("SOUR:VOLT:ILIM %.9f"%limit)
# self.wr(":SENSE:CURR:NPLC 10")   




