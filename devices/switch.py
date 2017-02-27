import time
from pyserial_device import device, device_error


class switch(device):
    """ 
    Costum made CERN switch card.
    
    Example:
    -------------
    dev = switch(port='/dev/ttyUSB1')
    dev.print_idn()
    dev.print_info()
    dev.reset()
    """
    
    def __init__(self, port):
        device.__init__(self, port=port, baudrate=115200)
        ret = self.ctrl.query("SYS.REBOOT")
        ret = self.ctrl.query("UI.DISPLAY OFF")

    def get_idn(self):
        return self.ctrl.query("SYS.INFO")

    def print_idn(self):
        self.logging.info(self.ctrl.query("SYS.INFO"))
        return 0

    def print_info(self, debug=0):
        if debug == 1: 
            self.logging.info("Displaying information about board, cpu, build and uptime.")
        self.logging.info(self.ctrl.query("SYS.BOARD"))
        self.logging.info(self.ctrl.query("SYS.CPU"))
        self.logging.info(self.ctrl.query("SYS.BUILD"))
        self.logging.info(self.ctrl.query("SYS.UPTIME"))
        return 0

    def print_help(self, debug=0):
        if debug == 1: 
            self.logging.info("Query Help.")
        self.logging.info(self.ctrl.query("HELP"))
        return 0
    
    def reboot(self, debug=0):
        if debug == 1: 
            self.logging.info("Rebooting device.")
        return self.ctrl.query("SYS.REBOOT")

    def halt(self, debug=0):
        if debug == 1: 
            self.logging.info("Freezing CPU.")
        return self.ctrl.query("SYS.HALT")



    # Switch functions
    # ---------------------------------

    def get_matrix_humidity(self, debug=0):
        if debug == 1: 
            self.logging.info("Displaying humidity (in %) from the sensor on the switching matrix.")
        return self.ctrl.query("MATRIX.HUMIDITY")

    def get_matrix_temperature(self, debug=0):
        if debug == 1: 
            self.logging.info("Displaying temperature (deg C) from the sensor on the switching matrix.")
        return self.ctrl.query("MATRIX.TEMPERATURE")

    def print_matrix_info(self, debug=0):
        if debug == 1: 
            self.logging.info("Displaying matrix current settings.")
        self.logging.info(self.ctrl.query("MATRIX.INFO"))
        return 0

    def get_measurement_type(self, debug=0):
        if debug == 1: 
            self.logging.info("Query measurement type.")
        return self.ctrl.query("MATRIX.MEASUREMENT ?")

    def get_channel(self, debug=0):
        if debug == 1: 
            self.logging.info("Query selected channel")
        return self.ctrl.query("MATRIX.CHANNEL ?")

    def set_measurement_type(self, typ, debug=0):
        if debug == 1: 
            self.logging.info("Setting measurement type. Valid values are ['IV','CV'].")
        return self.ctrl.query("MATRIX.MEASUREMENT %s" % typ)

    def open_channel(self, channel, debug=0):
        if debug == 1: 
            self.logging.info("Selecting measurement channel. Valid values are [0-511].")
        self.ctrl.query("MATRIX.CHANNEL %d" % channel)
        return 0

    def shortall(self, debug=0):
        if debug == 1: 
            self.logging.info("Shorting all channels to ground.")
        self.ctrl.query("MATRIX.SHORTALL")
        return 0




    # Probecard functions
    # ---------------------------------

    def get_probecard_humidity(self, debug=0):
        if debug == 1: 
            self.logging.info("Displaying humidity (in %) from the sensor on the probecard.")
        return self.ctrl.query("PROBECARD.HUMIDITY")

    def get_probecard_temperature(self, debug=0):
        if debug == 1: 
            self.logging.info("Displaying temperature (deg C) from the sensor on the probecard.")
        return self.ctrl.query("PROBECARD.TEMPERATURE")




    # UI functions
    # ---------------------------------

    def get_representation(self, debug=0):
        if debug == 1: 
            self.logging.info("Query the representation of the channel number displayed on the 7 segment display.")
        return self.ctrl.query("UI.REPRESENTATION ?")

    def get_display_timeout(self, debug=0):
        if debug == 1: 
            self.logging.info("Query how long the display should be on in the AUTO mode.")
        return self.ctrl.query("UI.TIMEOUT ?")

    def get_display_mode(self, debug=0):
        if debug == 1: 
            self.logging.info("Query display mode.")
        return self.ctrl.query("UI.DISPLAY ?")

    def print_ui_info(self, debug=0):
        if debug == 1: 
            self.logging.info("Query the representation of the channel number displayed on the 7 segment display.")
        self.logging.info(self.ctrl.query("UI.INFO"))
        return 0

    def set_representation(self, val='HEX', debug=0):
        if debug == 1: 
            self.logging.info("Setting the representation of the channel number displayed on the 7 segment display. Valid values are ['DEC','OCT','HEX'].")
        return self.ctrl.query("UI.REPRESENTATION %s" % val)
    
    def set_display_timeout(self, val=5, debug=0):
        if debug == 1: 
            self.logging.info("Setting how long the display should be on in the AUTO mode. Unit is [s].")
        return self.ctrl.query("UI.TIMEOUT %d" % val)

    def set_display_mode(self, val='OFF', debug=0):
        if debug == 1: 
            self.logging.info("Setting display mode. Valid values are ['ON','OFF','AUTO'].")
        return self.ctrl.query("UI.DISPLAY %s" % val)





