import pdb
import sys
import time
import datetime as dt

sys.path.append("C:\\Users\\pcdttp04\\AXIOM")
sys.path.append("C:\\Users\\pcdttp04\\AXIOM\\devices")
sys.path.append("C:\\Users\\pcdttp04\\AXIOM\\utils")

from devices.tsic306to92 import TSIC306TO92
from devices.tsx3510P import tsx3510P

from utils import logging
from utils.pid import PID
from utils.io_tools import protocol

# settings
targetT = -20
P = -0.1
I = 0
D = 0

target_voltage = 8 # use constant voltage and regulate via current

output_dir = "Test"

log = logging.setup_logger(__file__, 3)

info = protocol("Test", 
	metadata={
	"P": P,
	"I": I,
	"D": D,
	"target_temperature":targetT,
	"target_voltage":target_voltage
}, 
override=True)

# load devices
temp = TSIC306TO92("COM7")

tsx = tsx3510P(6)
tsx.set_voltage(target_voltage)
tsx.set_current(0)

temp.create_figure()

pid = PID(P, I, D)
pid.SetPoint = targetT
pid.setSampleTime(1)

i=0
while 1:
	i += 1
	info.update_pid_config(pid)
	#read temperature data
	temperature = temp.read_temperature()

	temp.update_figure(temperature)	

	pid.update(temperature)
	target_power = pid.output

	log.info(f"Target: {targetT} C | Current: {temperature} C | PWM: {target_power}")

	target_power = max(min( int(target_power), 4 ), 0)

	# save information every 10 seconds
	if i%20 == 0:
		info.write({
			"time": dt.datetime.now().strftime('%H:%M:%S'),
			"temperature": temperature,
			"target_current": target_power,
			"voltage": tsx.read_voltage(),
			"current": tsx.read_current(),
		})

	# Set PWM expansion channel 0 to the target setting
	tsx.set_current(target_power)
	time.sleep(0.5)

# print(temp.read_temperature())


