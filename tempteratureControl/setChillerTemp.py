import serial, sys, time
from chiller_from_Matthias import Chiller_CC_505

chiller = Chiller_CC_505(port='COM6')
chiller.set_point(float(sys.argv[1]))
time.sleep(1)
print(chiller.read_setpoint())