import serial
from time import time
import numpy as np


class Chiller_CC_505:
    """
    This class enables the communication between Python and the Huber CC-505 chiller.

    Manual: https://www.huber-online.com/fileadmin/user_upload/huber-online.com/Downloads/Handb%C3%BCcher_Software/Handbuch_Datenkommunikation_PB_en.pdf
    """

    def __init__(self, port: str = 'COM5'):
        """
        This constructor sets up the communication to the Huber CC-505 chiller.

        :param port: string; The name of the serial port to the ciller.
        """

        self.chiller_start_time = None

        self.ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        self.ser.reset_input_buffer()

    def turn_on_off(self, mode: str, min_runtime: int = 300):
        """
        This method can turn the chiller on or off. If it is called to turn the chiller off and the
        chiller has not been on for the minimum runtime, the method waits until the chiller can be turned off.

        :param mode: string; This parameter can be set to "on" or "off".
        :param min_runtime: integer; The minimum runtime of the chiller in seconds.

        :return: Optional[string]; If an error occured, a string with information is returned. Otherwise, None is returned.
        """

        if mode == 'on':
            self.chiller_start_time = time()
            self._send_value(command_type='14', value=1)

        elif mode == 'off':
            if self.chiller_start_time is None or (time() - self.chiller_start_time) > min_runtime:
                self._send_value(command_type='14', value=0)
            else:
                return 'The minimum run-time of the chiller is not yet lapsed!'

        else:
            print('The value for the parameter "mode" can only be "on" or "off"!')

    def set_point(self, setpoint_temperature: int):
        """
        This method sets a new temperature setpoint for the chiller.

        :param setpoint_temperature: integer; The new temperature in °C.
        """

        self._send_value(command_type='00', value=setpoint_temperature*100)

    def read_setpoint(self):
        return self._request_value(command_type='00')/100

    def read_internal_temperature(self):
        return self._request_value(command_type='01')/100

    def read_external_temperature(self):
        return self._request_value(command_type='07')/100
    
    def check_status(self):
        return self._request_value(command_type='14')
    
    def close(self):
        self.ser.close()
    
    def _send_value(self, command_type: str, value: float) -> bytes:
        if not len(command_type) == 2:
            raise ValueError('The command_type must consist of 2 characters!')

        command = '{M' + command_type + format(np.uint16(value), 'X').zfill(4) + '\r\n'
        self.ser.write(command.encode())

        return self.ser.read(size=10)
    
    def _request_value(self, command_type: str):
        if not len(command_type) == 2:
            raise ValueError('The command_type must consist of 2 characters!')

        command = '{M' + command_type + '****\r\n'
        self.ser.write(command.encode())

        value = self.ser.read(size=10)
        try:
            numeric_value = np.int16(int(value.decode()[4:8], 16))
        except ValueError:
            numeric_value = float('nan')

        return numeric_value
