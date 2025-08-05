from softcheck.logic import Com
from softcheck.logic import CommunicationTimeout
from softcheck.pp_commands import PpCom
import time
com = Com("serial", 2.1,3)
com.open("COM5", 9600) #open COMX with 9600 (address not defined)
pp = PpCom(com)


setpoint_temperature = 19

com.send('SP@{temp}\r\ni'.format(temp=int(setpoint_temperature*100)))
com.send('TM@+0001\r\n')
com.send('SP?\r\n')
com.recv()
