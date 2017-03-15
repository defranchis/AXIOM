from devices import *
from measurements import *
from optparse import OptionParser


def main():
	usage = "usage: prog [options] id test[(parameter=value parameter2=value)]"

	parser = OptionParser(usage=usage, version="prog 0.01")
	parser.add_option("-l", "--list-tests", action="store_true", dest="list_tests", default=False,  help="List all avaliable tests")

	(options, args) = parser.parse_args()
	
	if options.list_tests:
		tests = TPX_tests("null", logdir="logs/null/")
		tests.list()
		return 0

	if len(args) < 1:
		parser.error("You have to given an identifier")
	id = args[0]

	test_list = []	
	if len(args) > 1:
		test_list = args[1:]

	for test in test_list:
		if test == 'test00_debugging':
			msr = test00_debugging(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		elif test == 'test02_scan_iv':
			msr = test02_scan_iv(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		elif test == 'test03_scan_cv':
			msr = test03_scan_cv(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		elif test == 'test04_single_iv':
			msr = test04_single_iv(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		elif test == 'test05_single_cv':
			msr = test05_single_cv(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		elif test == 'test06_longterm_iv':
			msr = test06_longterm_iv(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		elif test == 'test07_longterm_cv':
			msr = test07_longterm_cv(ide=id)
			msr.initialise()
			msr.execute()
			msr.finalise()

		else:
			print 'Unknown Test.'

if __name__ == "__main__":
    main()

 