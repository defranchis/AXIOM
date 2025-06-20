import os
import measurements
from optparse import OptionParser
# #import measurements.allmeasurements as allmsr
# from measurements.testMD_dummyIVWithSwitch import *
# from measurements.testMD_fullSensorMeasurements import *
# from measurements.testMD_CRV import *
# #from measurements.testMD_fullStrip import *
# # from measurements.testEF_fullDiode import *
# #from measurements.testMD_DiodeStrip import *
# from measurements.testMD_DiodeGR import *


#import testMD_dummyIVWithSwitch

# ------------------------------------------------------------------------------
# main()
#
# Entry point for running measurement scripts in the ARRAY wafer probing system.
# Parses command-line arguments to:
# - List available measurement scripts from the 'measurements' folder
# - Run a specified measurement on a device identified by a user-defined ID
# - Optionally load a YAML configuration file
#
# Executes the selected measurement by calling its initialise(), execute(), 
# and finalise() methods. Results are stored in the 'logs' directory under the 
# provided identifier.
# ------------------------------------------------------------------------------



def main():

	# This sets up the CLI commands, receives potential parameters and sets config paths, if provided. 
	usage = "usage: prog [options] id test[(parameter=value parameter2=value)]"
	parser = OptionParser(usage=usage, version="prog 0.01")
	parser.add_option("-l", "--list-tests", action="store_true", dest="list_tests", default=False,  help="list all avaliable measurements")
	parser.add_option("-c", "--config", dest="config_file", default=None, help="Path to the YAML configuration file")

	(options, args) = parser.parse_args()
	if len(args) < 1 and not options.list_tests:
		parser.error("You have to give an identifier. Try '-h' to get more info.")

	# if options.list_tests:
	# 	list_of_tests = []
	# 	list_of_valid_prefix = ['test', 'msr', 'measurement', 'exp', 'experiment']

	# 	for test_name in os.listdir('measurements'):
	# 		for prefix in list_of_valid_prefix:
	# 			if len(prefix) < len(test_name):
	# 				if test_name[len(prefix)].isdigit():
	# 					list_of_tests.append(test_name)

	# 	print("{a:40s} | {b}" .format(a="Test Name", b="Description") )
	# 	#print("-" * 80)
	# 	for test_name in sorted(list_of_tests):
	# 	    #test = getattr(measurements, test_name)
	# 		test = test_name
	# 		#print("%-40s | %s" % (test_name, test.__doc__)
	# 		print("{a:40s}".format(a=test_name ) )

	# 	return 0

	# if options.list_tests:
	# 	list_of_tests = []
	# 	list_of_valid_prefix = ['test', 'msr', 'measurement', 'exp', 'experiment']

	# 	for test_name in dir(measurements):
	# 		for prefix in list_of_valid_prefix:
	# 			if len(prefix) < len(test_name):
	# 				if test_name[len(prefix)].isdigit():
	# 					list_of_tests.append(test_name)

	# 	print("{a:40s} | {b}" .format(a="Test Name", b="Description") )
	# 	print ("-" * 80)
	# 	for test_name in sorted(list_of_tests):
	# 		test = getattr(measurements, test_name)
	# 		print("{a:40s}".format(a=test_name ) )

	# 	return 0


	# The argument at [0] is now the identifier that is specified for this test session. 
	id = args[0]

	test_list = []
	if len(args) > 1:
		test_list = args[1:] 

	config_path = options.config_file

	for test_name in test_list:
		print('this is testname', test_name)
		try:
			test = getattr(measurements, test_name)
			# test = testMD_fullSensorMeasurements
			# test = measurements.testMD_fullStrip
		except AttributeError:
			print('Unknown Test.')
			return 1
		

		msr = test(ide = id, config_path=config_path)
		#msr = test(ide = id)
		print(msr)
		msr.initialise()
		msr.execute()
		msr.finalise()

if __name__=="__main__":
	main()
