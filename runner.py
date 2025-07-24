import measurements
from optparse import OptionParser
import shutil
import os
import yaml



def main():

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_path", help="Path to YAML config file")
    (options, args) = parser.parse_args()

    if not options.config_path:
        parser.error("The --config option must be specified.")

    config_path = options.config_path

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    test = getattr(measurements, config['test_name'])

    msr = test(ide=id, config_path=config_path)
    msr.initialise()
    msr.execute()
    msr.finalise()

if __name__=="__main__":
    main()
