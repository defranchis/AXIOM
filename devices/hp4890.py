import time
from pyvisa_device import device, device_error


class hp4890(device):
    """ 
    Keysight E4890 lcr meter.
    
    Example:
    -------------
    dev = hp4890(address=24)
    dev.print_idn()
    dev.reset()
    
    "FUNC:IMP:RANG 1E4"
    
    "COMP ON" dev.set_comparator(0)
    "INIT:CONT OFF" dev.set_trigger_continous(0)
    "INIT:IMM" dev.set_trigger_immediate()
    "TRIG:IMM" dev.send_trigger()
    "FETCh?" dev.execute_measurement()
    """

    def __init__(self, address):
        device.__init__(self, address=address)
        self.ctrl.write("*RST")

    def print_idn(self, debug=0):
        if debug == 1: 
            self.logging("Query ID.")
        self.logging(self.ctrl.query("*IDN?"))
        return 0
    
    def get_idn(self):
        return self.ctrl.query("*IDN?")
    
    def reset(self, debug=0):
        if debug == 1: 
            self.logging("Reseting device.")
        self.ctrl.write("*RST")
        return 0

    def restart(self, debug=0):
        if debug == 1: 
            self.logging("Restarting device.")
        self.ctrl.write(":SYST:REST")
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



    # Configuration functions
    # ---------------------------------

    def set_voltage(self, val, debug=0):
        if debug == 1: 
            self.logging("Setting voltage to %f V." % val)
        self.ctrl.write("VOLT %fV" % val)
        return 0

    def set_frequency(self, val, debug=0):
        if debug == 1:
            self.logging("Setting frequency to %s Hz." % val)
        self.ctrl.write("FREQ %sHZ" % val)
        return 0

    def set_mode(self, mode='CSRS', debug=0):
        if debug == 1: 
            self.logging("Setting measurement mode to %s. Options are ['CSRS', 'CPRP', 'ZTD']." % mode)
        self.ctrl.write("FUNC:IMP %s" % mode)
        return 0

    def set_range_auto(self, mode=0, debug=0):
        if debug == 1:
            self.logging("Setting auto range %s. Options are [0, 1]." % mode)
        self.ctrl.write("FUNC:IMP:RANG:AUTO %d" % mode)
        return 0

    def set_imp_range(self, val, debug=0):
        if debug == 1:
            self.logging("Setting impedance measurement range to %E." % val)
        self.ctrl.write("FUNC:IMP:RANG %E" % val)
        return 0
    

    def set_read_format(self, mode='ASC:LONG', debug=0):
        if debug == 1:
            self.logging("Setting read format to %s. Options are ['BIN', 'ASC']." % mode)
        self.ctrl.write(":FORM:%s" % mode)
        return 0

    def set_comparator(self, mode=0, debug=0):
        if debug == 1:
            self.logging("Switching comparator to %d. Options are [0, 1]." % mode)
        self.ctrl.write("COMP %d" % mode)
        return 0

    def set_aperture_time(self, mode='LONG', val=1, debug=0):
        if debug == 1:
            self.logging("Setting the measurement time mode and the averaging rate to %s and %d. Options are [SHOR, MED, LONG] and [1-256]." % (mode, val))
        self.ctrl.write("APER %s, %d" % (mode, val))
        return 0

    def set_dc_isolation_auto(self, mode=1, debug=0):
        if debug == 1:
            self.logging("Setting dc isolation auto level to %d. Options are [0, 1]." % mode)
        self.ctrl.write(":OUTP:DC:ISOL:LEV:AUTO %d" % mode)
        return 0

    def set_alc(self, mode=0, debug=0):
        if debug == 1:
            self.logging("Setting the Automatic Level Control (ALC) to %d. Options are [0, 1]." % mode)
        self.ctrl.write(":AMPL:ALC %d" % mode)
        return 0

    def check_voltage(self, debug=0):
        if debug == 1: 
            self.logging("Checking voltage setting.")
        return self.ctrl.query("VOLT?")

    def check_frequency(self, debug=0):
        if debug == 1: 
            self.logging("Checking frequency setting.")
        return self.ctrl.query("FREQ?")

    def check_mode(self, debug=0):
        if debug == 1:     
            self.logging("Checking measurement type.")
        return self.ctrl.query("FUNC:IMP?")

    def check_current(self, debug=0):
        if debug == 1:     
            self.logging("Checking current setting.")
        return self.ctrl.query("CURR?")

    def check_range(self, debug=0):
        if debug == 1: 
            self.logging("Checking measurement range.")
        return self.ctrl.query("FUNC:IMP:RANG?")




    # Correction functions
    # ---------------------------------

    def set_correction_cable_length(self, val, debug=0):
        if debug == 1: 
            self.logging("Setting correction cable length to %d meters. Options are [0, 1, 2, 4]." % val)
        self.ctrl.write("CORR:LENG %dM" % val) 
        return 0

    def check_correction_cable_length(self, debug=0):
        if debug == 1: 
            self.logging("Checking correction cable length.")
        return self.ctrl.query("CORR:LENG?")

    def execute_closed_correction(self, debug=0):
        if debug == 1: 
            self.logging("Do open correction for all frequencies.")
        self.ctrl.write("CORR:OPEN")
        return 0

    def execute_short_correction(self, debug=0):
        if debug == 1: 
            self.logging("Do short correction for all frequencies.")
        self.ctrl.write("CORR:SHOR")
        return 0

    def execute_load_correction(self, debug=0):
        if debug == 1:
            self.logging("Do load correction for all frequencies.")
        pass
        return -1

    def set_open_correction(self, val, debug=0):
        if debug == 1:
            self.logging("Setting open correction status to %d." % val) 
        self.ctrl.write("CORR:OPEN:STAT %d" % val) 
        return 0

    def set_short_correction(self, val, debug=0):
        if debug == 1:
            self.logging("Setting short correction status to %d." % val) 
        self.ctrl.write("CORR:SHOR:STAT %d" % val) 
        return 0 

    def set_load_correction(self, val, debug=0):
        if debug == 1: 
            self.logging("Setting load correction status to %d." % val)
        self.ctrl.write("CORR:LOAD:STAT %d" % val) 
        return 0

    def check_open_correction(self, debug=0):
        if debug == 1: 
            self.logging("Checking open correction status.")
        return self.ctrl.query("CORR:OPEN:STAT?")

    def check_short_correction(self, debug=0):
        if debug == 1: 
            self.logging("Checking short correction status.")
        return self.ctrl.query("CORR:SHOR:STAT?")

    def check_load_correction(self, debug=0):
        if debug == 1: 
            self.logging("Checking load correction status.")
        return self.ctrl.query("CORR:LOAD:STAT?")

    def set_load_correction_type(self, val='CPRP', debug=0):
        if debug == 1: 
            self.logging("Setting load correction type to %d." % val)
        self.ctrl.write("CORR:LOAD:TYPE %d" % val)
        return 0

    def check_load_correction_type(self, debug=0):
        if debug == 1: 
            self.logging("Checking load correction type.")
        return self.ctrl.query("CORR:LOAD:TYPE?")



    # Measurement functions
    # ---------------------------------

    def set_trigger_continous(self, mode=1, debug=0):
        if debug == 1:
            self.logging("Setting auto trigger %d. This enables the automatic trigger to change state from 'idle' state to 'wait for trigger' state." % mode)
        self.ctrl.write(":INIT:CONT %d" % mode)
        return 0

    def set_trigger_immediate(self, debug=0):
        if debug == 1:
            self.logging("Initiates the trigger to change from 'idle' state to 'wait for trigger' state one time.")
        self.ctrl.write(":INIT:IMM")
        return 0

    def set_trigger_source(self, mode='BUS', debug=0):
        if debug == 1:
            self.logging("Setting trigger source to %s. [INT, EXT, HOLD, BUS]" % mode)
        self.ctrl.write(":TRIG:SOUR %s" % mode)
        return 0

    def send_trigger(self, debug=0):
        if debug == 1:
            self.logging("Sending a trigger.")
        self.ctrl.write("TRIG:IMM")
        return 0

    def execute_measurement(self, debug=0):
        if debug == 1:
            self.logging("Fetching data.")
        vals = self.ctrl.query("FETC?").split(",")
        return float(vals[0]), float(vals[1])
