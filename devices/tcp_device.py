import socket
import logging


# Base error class
class device_error(object):
    """
    Abstract error class for ethernet devices based on socket.
    """
    pass



# Base device class
class device(object):
    """
    Abstract base class for ethernet devices based on socket.
    
    Example:
    dev = device(address=24)
    """
    
    def __init__(self, ip):
        pass

    def findInstruments(self):
        pass
 