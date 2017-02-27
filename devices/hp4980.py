import time
from lcr_meter import lcr_meter


class hp4980(lcr_meter):
    """ 
    Keysight E4890 lcr meter.
    
    Example:
    -------------
    dev = hp4890(address=24)
    dev.print_idn()
    dev.reset()
    """

    def __init__(self, address):
        lcr_meter.__init__(self, address=address)


