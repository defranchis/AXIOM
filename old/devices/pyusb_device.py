# ============================================================================
# File: pyusb_devices.py
# -----------------------
# Communication based ony pyusb.
# 
# Date: 06.06.2016
# Author: Florian Pitters
#
# ============================================================================

import logging
import usb.core
import usb.util



# Base error class
class device_error(object):
    """
    Abstract error class for usb devices based on pyusb.
    """
    pass




# Base device class
class device(object):
    """
    Abstract base class for usb devices based on pyusb.
    
    Example:
    dev = device(address=24)
    """
    
    def __init__(self, idVendor=0xfffe, idProduct=0x0001):

        # Open communication line
        dev = usb.core.find(idVendor, idProduct)
        if dev is None:
            raise ValueError('Device not found')
        
        # Set configuration. With no arguments, the first configuration will be the active one
        dev.set_configuration()
        
        # Get an endpoint instance
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        
        # Set up control
        self.ctrl = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)
        
        assert self.ctrl is not None
        

        ## Set up logger
        self.logging = logging.getLogger('root')
        self.logging.info("Initialising device.")
        self.logging.info(self.ctrl.write("*IDN?"))




    def findInstruments(self):
        return usb.core.find()   





 