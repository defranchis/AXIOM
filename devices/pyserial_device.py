import serial 
import logging
import time


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

    dev = device(port='/dev/tty.usbserial-A5064T4T')
    print dev.check_connection()
    print dev.idn()
    print dev.write('UI.DISPLAY OFF', 1)
    print dev.query('MATRIX.HUMIDITY ?', 1)
    time.sleep(0.1)
    time.sleep(0.1)
    dev.close_connection()

    Devices:
    Leakshore 335: baud rate 57600, 7 data bits, 1 start bit, 1 stop bit, odd parity, termination '\n'
    Leakshore 331: baud rate 9600, 7 data bits, 1 start bit, 1 stop bit, odd parity, termination '\r\n'
    Switchcard: baud rate 115200, 8 data bits, 0 start bit, 1 stop bit, no parity bit, termination '\r\n'
    """

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, termination='\r\n', timeout=1):

        self.termination = termination
        self.timeout = timeout

        ## Set up control
        self.ctrl = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            write_timeout=self.timeout,
            timeout=0.001, 
            xonxoff=False, 
            rtscts=False, 
            dsrdtr=False
        )



        ## Set up logger
        self.logging = logging.getLogger('root')
        self.logging.info("Initialising device.")
        self.logging.info("Costum made switch board.")

    def list_ports(self):
        print serial.tools.list_ports()

    def idn(self):
        return self.ctrl.name

    def open_connection(self):
        return self.ctrl.open()

    def check_connection(self):
        return self.ctrl.isOpen()

    def close_connection(self):
        return self.ctrl.close()

    def flush_input(self):
        return self.ctrl.flushInput()

    def flush_output(self):
        return self.ctrl.flushOutput()

    def write(self, cmd, debug=0):
        lines = []
        start = time.time()
        
        self.ctrl.write(cmd + self.termination)
        while True:
            try:
                while self.ctrl.inWaiting() > 0:
                    lines.append(self.ctrl.readline())
                for line in reversed(lines):
                    if line.find('>') != -1:
                        if debug == 1:
                            print lines
                        return 0
            except:
                if (time.time() - start > self.timeout):
                    if debug == 1: 
                        print "Timeout"
                    return -1

    def query(self, cmd, debug=0):
        lines = []
        start = time.time()
        
        self.ctrl.write(cmd + self.termination)
        while True:
            try:
                while self.ctrl.inWaiting() > 0:
                    lines.append(self.ctrl.readline())
                for line in reversed(lines):
                    if line.find('>') != -1:
                        if debug == 1:
                            print lines
                        return lines[1:-1]
            except:
                if (time.time() - start > self.timeout):
                    if debug == 1: 
                        print "Timeout"
                    return -1


















