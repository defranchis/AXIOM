import time
from pyserial_device import device, device_error


class switchcard(device):
    """
    Costum made CERN switch card.

    Example:
    -------------
    dev = switchcard(port='/dev/tty.usbserial-A5064T4T')
    print dev.check_connection()
    print dev.idn()

    print dev.reboot()
    time.sleep(1)
    print dev.get_idn()
    print dev.print_info()
    print dev.get_probecard_humidity()
    print dev.get_probecard_temperature()
    print dev.get_matrix_humidity()
    print dev.get_matrix_temperature()
    print dev.print_matrix_info()
    print dev.set_measurement_type('IV')
    print dev.get_measurement_type()
    print dev.open_channel(104)
    print dev.get_channel()
    print dev.shortall()
    print dev.get_channel()
    print dev.set_representation('OCT')
    print dev.get_representation()
    print dev.set_display_mode('ON')
    print dev.get_display_mode()
    print dev.set_display_timeout(2)
    print dev.get_display_timeout()

    time.sleep(1)
    dev.close_connection()
    """

    def __init__(self, port):
        device.__init__(self, port=port, baudrate=115200, termination='\r\n')
        recv = self.query("SYS.INFO")
        info = [''.join(i).strip() for i in recv]
        self.logging.info(' | '.join(info))
        print('\t')
        self.flush_input()
        self.flush_output()

    def get_idn(self):
        return self.query("SYS.INFO")

    def print_idn(self):
        print(self.query("SYS.INFO"))
        return 0

    def print_info(self, debug=0):
        if debug == 1:
            self.logging.info("Displaying information about board, cpu, build and uptime.")
        print(self.query("SYS.BOARD"))
        print(self.query("SYS.CPU"))
        print(self.query("SYS.BUILD"))
        print(self.query("SYS.UPTIME"))
        return 0

    def print_help(self, debug=0):
        if debug == 1:
            self.logging.info("Query Help.")
        print(self.query("HELP"))
        return 0

    def reboot(self, debug=0):
        if debug == 1:
            self.logging.info("Rebooting device.")
        return self.write("SYS.REBOOT")

    def halt(self, debug=0):
        if debug == 1:
            self.logging.info("Freezing CPU.")
        return self.write("SYS.HALT")



    # Switch functions
    # ---------------------------------

    def get_matrix_humidity(self, debug=0):
        if debug == 1:
            self.logging.info("Displaying humidity (in %) from the sensor on the switching matrix.")
        try:
            val = self.query("MATRIX.HUMIDITY", debug)[0].strip()
            return val
        except StandardError:
            self.logging.info("Value Error.")
            return -1

    def get_matrix_temperature(self, debug=0):
        if debug == 1:
            self.logging.info("Displaying temperature (deg C) from the sensor on the switching matrix.")
        try:
            val = float(self.query("MATRIX.TEMPERATURE", debug)[0].strip())
            return val
        except StandardError:
            self.logging.info("Value Error.")
            return -1

    def print_matrix_info(self, debug=0):
        if debug == 1:
            self.logging.info("Displaying matrix current settings.")
        return self.query("MATRIX.INFO")

    def get_measurement_type(self, debug=0):
        if debug == 1:
            self.logging.info("Query measurement type.")
        try:
            val = self.query("MATRIX.MEASUREMENT ?", debug)[0].strip()
            return val
        except StandardError:
            self.logging.info("Value Error.")
            return -1

    def get_channel(self, debug=0):
        if debug == 1:
            self.logging.info("Query selected channel.")
        try:
            try:
                val = float(self.query("MATRIX.CHANNEL ?", debug)[0].strip())
                return val
            except ValueError:
                string = self.query("MATRIX.CHANNEL ?", debug)[0].strip()
                return string
        except StandardError:
            self.logging.info("Error.")
            return -1

    def set_measurement_type(self, typ, debug=0):
        if debug == 1:
            self.logging.info("Setting measurement type. Valid values are ['IV','CV'].")
        return self.write("MATRIX.MEASUREMENT %s" % typ)

    def set_cv_resistance(self, val, debug=0):
        if debug == 1:
            self.logging.info("Setting measurement type. Valid values are [1e5, 5e5, 1e6, 2e6, 5e6, 1e7, 5e7, 1e8].")
        try:
            d = self.write("MATRIX.CVRES %d" % val)
            return 0
        except StandardError:
            self.logging.info("This switchcard or firmware version does not have variable CV resistance.")
            return -1

    def open_channel(self, channel, debug=0):
        if debug == 1:
            self.logging.info("Selecting measurement channel. Valid values are [0-511].")
        return self.write("MATRIX.CHANNEL %d" % channel)

    def shortall(self, debug=0):
        if debug == 1:
            self.logging.info("Shorting all channels to ground.")
        return self.write("MATRIX.SHORTALL")



    # Probecard functions
    # ---------------------------------

    def get_probecard_humidity(self, debug=0):
        if debug == 1:
            self.logging.info("Displaying humidity (in %) from the sensor on the probecard.")
        try:
            val = self.query("PROBECARD.HUMIDITY", debug)[0].strip()
            return val
        except StandardError:
            self.logging.info("Error. Probecard not connected.")
            return -1

    def get_probecard_temperature(self, debug=0):
        if debug == 1:
            self.logging.info("Displaying temperature (deg C) from the sensor on the probecard.")
        try:
            val = float(self.query("PROBECARD.TEMPERATURE", debug)[0].strip())
            return val
        except StandardError:
            self.logging.info("Error. Probecard not connected.")
            return -1



    # UI functions
    # ---------------------------------

    def get_representation(self, debug=0):
        if debug == 1:
            self.logging.info("Query the representation of the channel number displayed on the 7 segment display.")
        try:
            val = self.query("UI.REPRESENTATION ?", debug)[0].strip()
            return val
        except StandardError:
            self.logging.info("Error.")
            return -1

    def get_display_timeout(self, debug=0):
        if debug == 1:
            self.logging.info("Query how long the display should be on in the AUTO mode.")
        try:
            val = self.query("UI.TIMEOUT ?", debug)[0].strip()
            return val
        except StandardError:
            self.logging.info("Error.")
            return -1

    def get_display_mode(self, debug=0):
        if debug == 1:
            self.logging.info("Query display mode.")
        try:
            val = self.query("UI.DISPLAY ?", debug)[0].strip()
            return val
        except StandardError:
            self.logging.info("Error.")
            return -1

    def get_ui_info(self, debug=0):
        if debug == 1:
            self.logging.info("Query the representation of the channel number displayed on the 7 segment display.")
        return self.query("UI.INFO")

    def set_representation(self, val='HEX', debug=0):
        if debug == 1:
            self.logging.info("Setting the representation of the channel number displayed on the 7 segment display. Valid values are ['DEC','OCT','HEX'].")
        return self.write("UI.REPRESENTATION %s" % val)

    def set_display_timeout(self, val=5, debug=0):
        if debug == 1:
            self.logging.info("Setting how long the display should be on in the AUTO mode. Unit is [s].")
        return self.write("UI.TIMEOUT %d" % val)

    def set_display_mode(self, val='OFF', debug=0):
        if debug == 1:
            self.logging.info("Setting display mode. Valid values are ['ON','OFF','AUTO'].")
        return self.write("UI.DISPLAY %s" % val)
