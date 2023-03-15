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

# # davids:
# O = 1.4
# P = -6.
# I = -0.08
# D = -2

# matteos:
O = 1.0
P = -5.
I = 0
D = -3

target_voltage = 8 # use constant voltage and regulate via current
max_voltage = 12
max_current = 4

output_dir = "Test2"

log = logging.setup_logger(__file__, 3)

info = protocol("Test", 
	metadata={
	"O": O,
	"P": P,
	"I": I,
	"D": D,
	"target_temperature":targetT,
	"target_voltage":target_voltage,
	"max_current":max_current,
	"max_voltage":max_voltage

}, 
override=True)

# load devices
temp = TSIC306TO92("COM7")



tsx = tsx3510P(6)
tsx.set_voltage(target_voltage)
tsx.set_current(0)


tsx.set_output_on()

temp.create_figure()

pid = PID(P, I, D)
pid.SetPoint = targetT
pid.setSampleTime(1)

try:
	i=0
	while 1:
		i += 1
		info.update_pid_config(pid)
		#read temperature data
		temperature = temp.read_temperature()

		temp.update_figure(temperature, targetT)	

		pid.update(temperature)

		metadata = info.get_metadata()

		max_voltage = metadata["max_voltage"]
		max_current = metadata["max_current"]
		offset_current = metadata["O"]

		target_current = pid.output + offset_current
		target_current_cap = max(min( target_current, max_current), 0.01)

		log.info(f"Target: {targetT} C | Temperature: {temperature} C | Target current: {target_current} | Actual current: {target_current_cap}")

		# save information every 10 seconds
		if i%20 == 0:
			info.write({
				"time": dt.datetime.now().strftime('%H:%M:%S'),
				"temperature": temperature,
				"target_current": target_current_cap,
				"voltage": tsx.read_voltage(),
				"current": tsx.read_current(),
			})

		# Set PWM expansion channel 0 to the target setting
		tsx.set_current(target_current_cap)
		time.sleep(1.0)

except:
	tsx.set_output_off()

# print(temp.read_temperature())


