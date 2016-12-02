import time
import lcr_meter


class hp4284A(lcr_meter):
    """ 
    Keysight 4284A lcr meter.
    
    Example:
    -------------
    dev = hp4284A(address=24)
    dev.print_idn()
    dev.reset()
    dev.set_mode('ZTD')
    dev.set_voltage(1E6)
    dev.set_frequency(1)
    dev.set_trigger_source('BUS')
    dev.set_read_format('ASC')
    dev.set_aperture('LONG', 4)

    "AMPL:ALC ON" 
    "OUTP:DC:ISOL ON" 
    "FUNC:IMP:RANG 1E4"
    
    "FUNC:SMON:VAC ON" 
    "FUNC:SMON:IAC ON" 
    "FUNC:DEV1:MODE ABS" 
    "FUNC:DEV2:MODE ABS" 
    "FUNC:DEV1:REF 10000" 
    "FUNC:DEV2:REF 1"
    
    
    
    "COMP ON"
    "INIT:CONT OFF"
    "INIT:IMM"
    "TRIG:IMM"
    "FETCh?"
    """
