# ============================================================================
# File: pygpib_devices.py
# -----------------------
# Communication based ony linux gpib.
# 
# Date: 06.06.2016
# Author: Florian Pitters
#
# ============================================================================

import logging
import gpib


# Base error class
class device_error(object):
    """
    Abstract error class for gpib devices based on .
    """
    pass




# Base device class
class device(object):
    """
    Abstract base class for gpib devices based on py.
    
    Example:
    dev = device(address=24)
    """
    
    def __init__(self, id):
        pass

    def findInstruments(self):
        pass  





 