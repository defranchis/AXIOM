import time
from pyvisa_device import device, device_error


class tsx3510P(device):
    """
    Aim TTi TSX3510P voltmeter.

    Example:
    -------------
    dev = AimTTiTSX3510P(address=23)
    print dev.get_idn()
    dev.reset()
    dev.set_range(2E-8)
    print dev.get_range()
    dev.set_nplc(2)
    print dev.get_nplc()
    dev.setup_ammeter()
    print dev.read_current()
    """


    def __init__(self, address):
        device.__init__(self, address=address)

        self.max_current = 4
        self.max_voltage = 12

        self.ctrl.write("*RST")

    def get_idn(self):
        return self.ctrl.query("*IDN?")

    def print_idn(self, debug=0):
        self.logging.debug("Query ID.")
        self.logging.info(self.get_idn())
        return 0

    def reset(self, debug=0):
        self.logging.debug("Reseting device.""")
        self.ctrl.query("*RST")
        return 0

    def clear_status(self, debug=0):
        self.logging.debug("Clearing all status bits.")
        self.ctrl.query("*CLS")
        return 0

    def self_test(self, debug=0):
        self.logging.info("The PSU has no self-test capability and the response is always 0.")
        return self.ctrl.query("*TST?")


    # Set attribute functions
    # ---------------------------------


    def set_voltageLimit(self, fValue, iChannel=-1):
        self.ctrl.write('OVP %f' % fValue)

    def set_voltage(self, fValue, iChannel=-1):
        if fValue > self.max_voltage:
            self.logging.warning(f"Maximum voltage is {self.max_voltage} but you try to set {fValue}! Do nothing now.")
        elif fValue < 0:
            self.logging.warning(f"You try to set a negative voltage {fValue}, which is not possible! Do nothing now.")
        else:
            self.ctrl.write('V %0.2f' % fValue)

    def set_current(self, fValue, iChannel=-1):
        if fValue > self.max_current:
            self.logging.warning(f"Maximum current is {self.max_current} but you try to set {fValue}! Do nothing now.")
        elif fValue < 0:
            self.logging.warning(f"You try to set a negative current {fValue}, which is not possible! Do nothing now.")
        else:
            self.ctrl.write('I %0.2f' % fValue)



    # Read attribute functions
    # ---------------------------------
    def read_voltageLimit(self, iChannel=-1):
        sOVP = self.ctrl.query('OVP?')
        return float(sOVP[4:])

    def read_voltage(self, iChannel=-1):
        sV = self.ctrl.query('VO?')
        return float(sV[:sV.find('V')])

    def read_voltageSet(self, iChannel=-1):
        sV = self.ctrl.query('V?')
        return float(sV[2:])

    def read_current(self, iChannel=-1):
        sI = self.ctrl.query('IO?')
        return float(sI[:sI.find('A')])

    def read_currentSet(self, iChannel=-1):
        sI = self.ctrl.query('I?')
        return float(sI[2:])

    def read_power(self, iChannel=-1):
        sP = self.ctrl.query('POWER?')
        return float(sP[:sP.find('W')])
