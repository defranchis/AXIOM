import time
from devices.pyvisa_device import device, device_error


class ke7001(device):
    """
    Keithley 7001 switch.

    Example:
    -------------
    dev = ke7001(address=7)
    dev.print_idn()
    dev.close_channels(3) ## closes channel 3
    dev.open_channels(3)  ## opens channel 3
    dev.reset()
    """

    def __init__(self, address):
        device.__init__(self, address=address)
        self.ctrl.write("*RST")

    def print_idn(self, debug=0):
        if debug == 1:
            self.logging.info("Query ID.")
        self.logging.info(self.ctrl.query("*IDN?"))
        return 0

    def get_idn(self):
        return self.ctrl.query("*IDN?")

    def reset(self, debug=0):
        if debug == 1:
            self.logging.info("Reseting device.""")
        self.ctrl.write("*RST")
        return 0



    # Output functions
    # ---------------------------------
    def close_channel(self, chan, debug=0):
        if debug == 1:
            self.logging("Trying to close channel {a}".format(a=chan))
        self.ctrl.write(":CLOSE (@1!{a})".format(a=chan))
        return 0

    def open_channel(self, chan, debug=0):
        if debug == 1:
            self.logging("Trying to open channel {a}".format(a=chan))
        self.ctrl.write(":OPEN (@1!{a})".format(a=chan))
        return 0

    def close_channels(self, channels, debug=0):
        if debug == 1:
            self.logging("Trying to close channels {a}".format(a=','.join(channels)))
        chanlist =  '(@'+', '.join('1!'+str(i) for i in channels)+')'
        self.ctrl.write(":CLOSE "+chanlist)
        return 0

    def open_channels(self, channels, debug=0):
        if debug == 1:
            self.logging("Trying to open channels {a}".format(a=','.join(chs)))
        chanlist =  '(@'+', '.join('1!'+str(i) for i in channels)+')'
        self.ctrl.write(":OPEN "+chanlist)
        return 0

    def open_all(self, debug=0):
        if debug == 1:
            self.logging("Trying to open all channels")
        self.ctrl.write(":OPEN ALL")
        return 0

    def close_all(self, debug=0):
        ## probably not the best idea to try and close all channels.
        ## it shoudln't break anything, but not all of them are even
        ## connected. function just for completeness

        if debug == 1:
            self.logging("Trying to close all channels")
        self.ctrl.write(":CLOSE ALL")
        return 0


    # Read attribute functions
    # ---------------------------------

    ## MARC: TO BE DONE

    def read_closed_channels(self):
        self.ctrl.write(":CLOS:STAT?")
        val = self.ctrl.write("A$")
        print(val)
        return 0

