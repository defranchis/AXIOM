from softcheck.logic import Com
from softcheck.logic import CommunicationTimeout
from softcheck.pp_commands import PpCom
import time
com = Com("serial", 2.1, 3)
com.open("COM4", 9600) #open COM1 with 9600 (address not defined)
pp = PpCom(com, 1)
internal_temp = pp.request_echo("TI")
#pp.request("TI")
##pp.check_range("TI", 500, 6000)
##pp.request("TE")
##pp.check_range("TE", 0, 7000)
pp.change_to("CA", 1)
#time.sleep(20)
##pp.request("TP")
#pp.send("SP",  1000)
#
### to get the internal temperature:
print('this is the internal temperature')
pp.request_echo("TI")
print('this is the setpoint .... maybe')
pp.request_echo("SP")
print('this is the external temperature')
pp.request_echo("TE")
#com.close()
