# ============================================================================
# File: pyvisa_decices.py
# -----------------------
# Communication based ony py-visa.
# 
# Date: 06.06.2016
# Author: Florian Pitters
#
# ============================================================================

import visa


# Base error class
class device_error(object):
    """
    Abstract error class for gpib devices based on pyvisa.
    """
    pass



# Base device class
class device(object):
    """
    Abstract base class for gpib devices based on pyvisa.
    
    Example:
    dev = device(address=24)
    """
    
    def __init__(self, address=24):
        rm = visa.ResourceManager()
        self.ctrl = rm.open_resource('GPIB0::%s::INSTR' % address)
        self.logging("Initialising device.")
        self.logging(self.ctrl.query("*IDN?"))
    
    def logging(self, msg):
        standalone == 0
        if standalone == 1:
            print "-----> %s" % msg     
        else:
            pass
 