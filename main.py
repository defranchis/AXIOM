import measurements
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
		parser.error("You have to give an identifier")
	id = args[0]

	test_list = []	
	if len(args) > 1:
		test_list = args[1:]

	for test_name in test_list:
		
		try:
			test = getattr(measurements, test_name)
		except AttributeError:
			print('Unknown Test.')
			return 1

		msr = test(ide = id)
		msr.initialise()
		msr.execute()
		msr.finalise()



if __name__ == "__main__":
    main()

 