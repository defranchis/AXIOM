import os
import measurements
from optparse import OptionParser


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


def list_tests():
	test_names = []
	for attr in dir(measurements):
		obj = getattr(measurements, attr)
		if callable(obj) and hasattr(obj, 'initialise') and hasattr(obj, 'execute') and hasattr(obj, 'finalise'):
			test_names.append(attr)
	print("Available measurements:")
	for name in test_names:
		print(f"  {name}")
	return

def main():
	# This sets up the CLI commands, receives potential parameters and sets config paths, if provided. 
	usage = "usage: prog [options] id test[(parameter=value parameter2=value)]"
	parser = OptionParser(usage=usage, version="prog 0.01")
	parser.add_option("-l", "--list-tests", action="store_true", dest="list_tests", default=False,  help="list all avaliable measurements")
	parser.add_option("-c", "--config", dest="config_file", default=None, help="Path to the YAML configuration file")

	(options, args) = parser.parse_args()
	if len(args) < 1 and not options.list_tests:
		parser.error("You have to give an identifier. Try '-h' to get more info.")

	if options.list_tests:
		list_tests()
		return 0

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
		except AttributeError:
			print('Unknown Test: ', test_name)
			list_tests()

			return 1
		
		msr = test(ide = id, config_path=config_path)
		print(msr)
		msr.initialise()
		msr.execute()
		msr.finalise()

if __name__=="__main__":
	main()
