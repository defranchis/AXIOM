from xraymachine import XrayMachine
import time

### USER INPUTS ###

irradiation_step = 22 # in seconds!

kV = 40
mA = 3

n_shutter = 3 # shutter number. 1 for AsteiX, 3 of ObeliX

#############

xray = XrayMachine(port="COM3")

# used later to check how much when the irradiation is over
def get_timer(tn = None):
    try:
        time_left = xray.getTimer(tn=tn)
    except:
        print("Timer exception")
        time_left = 0

    return time_left

xray.timerOn(tn=3)          # ensure timer is on
xray.hvEnable(False)    # ensure power is off
xray.setHighVoltage(kV) # set tube voltage
xray.setCurrent(mA)     # set tube current
xray.hvEnable(True)     # turn power on
xray.waitForWarmUp()    # Wait until tube is ready to work

xray.setTimer(time=irradiation_step, tn = 3) # set xray machine timer

xray.openShutter(n_shutter) # START THE IRRADIATION!

# wait for timer to end
time_left = get_timer(tn=3)
print(f" remaining time: {time_left}")
# exit(-1)

try:
    while time_left > 0:
        time_left = get_timer(tn=3)
        print(f" remaining time: {time_left}")
        time.sleep(1)
except Exception as e:
    print(f"exception during iteration: {e}")
    pass

# be sure that the shutter is closed
xray.closeShutter(n_shutter) 
time.sleep(1)

# xray.port.flush()
remain = xray.port.read_all()
#print("remain: ", remain)s
xray.disconnect()
