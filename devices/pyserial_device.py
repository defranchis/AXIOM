import serial 
import logging


# Base error class
class device_error(object):
    """
    Abstract error class for RS232 devices based on pyserial.
    """
    pass



# Base device class
class device(object):
    """
    Abstract base class for RS232 devices based on pyserial.
    
    Example:
    dev = device(port='/dev/ttyUSB1')
    dev.write('KRDG? A' + '\n')
    while dev.inWaiting() > 0:
        print dev.read(1)
    dev.flushInput()
    dev.flushOutput()
    dev.close()

    Devices:
    Leakshore 335: baud rate 57600, 7 data bits, 1 start bit, 1 stop bit, odd parity, termination '\n'
    Leakshore 331: baud rate 9600, 7 data bits, 1 start bit, 1 stop bit, odd parity, termination '\r\n'
    """

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1, termination='\r\n'):

        
        ## Set up control
        self.ctrl = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_ODD,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.SEVENBITS,
            writeTimeout=timeout
        )

        ## Set up logger
        self.logging = logging.getLogger('root')
        self.logging.info("Initialising device.")
        self.logging.info(self.ctrl.query("*IDN?"))





