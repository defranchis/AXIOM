import pyvisa as visa
from utils import logging


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
    
    def __init__(self, address=24, verbose=3):

        ## Set up control
        rm = visa.ResourceManager()
        self.ctrl = rm.open_resource('GPIB0::%s::INSTR' % address)

        self.logging = logging.setup_logger(__file__, verbose)

        self.logging.info("Initialising device.")

        self.logging.info(self.ctrl.query("*IDN?"))

    def findInstruments(self):
        return visa.get_instruments_list()
 

 
