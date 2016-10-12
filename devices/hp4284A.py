# ============================================================================
# File: hp4284A.py
# -----------------------
# Communication for Keysight HP4284A lcr meter.
# 
# Date: 12.06.2016
# Author: Florian Pitters
#
# ============================================================================

from pyvisa_device import device, device_error


class hp4284A(device):
    """ 
    Keysight 4284A lcr meter.
    
    Example:
    -------------
    dev = hp4284A(address=24)
    dev.print_idn()
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
        self.logging("Reseting device.")
        self.ctrl.write("*RST")
        return 0
    
    def clear_status(self):
        self.logging("Clearing all status bits.")
        self.ctrl.write("*CLS")
        return 0

    def self_test(self):
        self.logging("Executing internal self test.")
        return self.ctrl.query("*TST?")  

    
    
    # Output functions
    # ---------------------------------

    def set_output_on(self):
        self.ctrl.write("OUTP ON")
        return 0



    # Configuration functions
    # ---------------------------------

    def set_voltage(self, val):
        self.logging("Setting voltage to %d mV." % val)
        self.ctrl.write("VOLT %dMV" % val)
        return 0

    def set_frequency(self, val):
        self.logging("Setting frequency to %d kHz." % val)
        self.ctrl.write("FREQ %dKHZ" % val)
        return 0

    def set_mode(self, mode='CPRP'):
        self.logging("Setting measurement mode to %s" % mode)
        self.ctrl.write("FUNC:IMP %s" % mode)
        return 0

    def check_voltage(self):
        self.logging("Checking voltage setting")
        return self.ctrl.query("VOLT?")

    def check_frequency(self):
        self.logging("Checking frequency setting")
        return self.ctrl.query("FREQ?")

    def check_mode(self):
        self.logging("Checking measurement type")
        return self.ctrl.query("FUNC:IMP?")

    def check_current(self):
        self.logging("Checking current setting.")
        return self.ctrl.query("CURR?")

    def check_range(self):
        self.logging("Checking measurement range.")
        return self.ctrl.query("FUNC:IMP:RANG?")

## Setup things
lcr.write("CURR MAX")               # Set current to max value (20 mA)
lcr.write("FUNC:IMP:RANG:AUTO ON")  # Set measurement range to auto  
lcr.write("FUNC:DEV1:MODE ABS")     # Set deviation mode for the primary parameter
lcr.query("FUNC:DEV2:MODE?")        # Check deviation mode for the secondary parameter
lcr.write("FUNC:DEV1:REF 10")       # Set reference value for the primary parameter to 10
lcr.write("FUNC:DEV1:REF:FILL")     # Do a measurement and fill the reference values


    # Correction functions
    # ---------------------------------

    def execute_closed_correction(self):
        """ """
        pass

    def execute_short_correction(self):
        """ """
        pass

    def execute_load_correction(self):
        """ """
        pass

    def set_closed_correction(self):
        """ """
        pass

    def set_short_correction(self):
        """ """
        pass

    def set_load_correction(self):
        """ """
        pass

    def check_closed_correction(self):
        """ """
        pass

    def check_short_correction(self):
        """ """
        pass

    def check_load_correction(self):
        """ """
        pass

## Do corrections
lcr.write("CORR:LENG 1M")           # Set length correction
lcr.query("CORR:LENG?")             # Check 
lcr.write("CORR:OPEN")              # Do open correction for all frequencies
lcr.write("CORR:OPEN:STAT ON")      # Set open correction status
lcr.query("CORR:OPEN:STAT?")        # Check open correction status
lcr.write("CORR:SHOR")              # Do short correction for all frequencies
lcr.write("CORR:SHOR:STAT ON")      # Set short correction status
lcr.query("CORR:SHOR:STAT?")        # Check short correction status
lcr.write("CORR:LOAD:STAT 1")       # Set load correction status
lcr.query("CORR:LOAD:STAT?")        # Check load correction status
lcr.write("CORR:LOAD:TYPE CPRP")    # Set load correction type
lcr.query("CORR:LOAD:TYPE?")        # Check load correction type

