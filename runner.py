import measurements
from optparse import OptionParser
import shutil
import os
import yaml



def main():
    # This sets up the CLI commands, receives potential parameters and sets config paths, if provided. 
    usage = "usage: prog [options] id test[(parameter=value parameter2=value)]"
    parser = OptionParser(usage=usage, version="prog 0.01")
    parser.add_option("-c", "--config", dest="config_file", default=None, help="Path to the YAML configuration file")
    
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("You have to give an identifier. Try '-h' to get more info.")

    config_path = options.config_file

    config = None
    if config_path:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        local_config_path = os.path.join(os.getcwd(), os.path.basename(config_path))
        shutil.copyfile(config_path, local_config_path)

    # Iterate through the provided tests and execute them.
    # The following lines assume 'test_name' and 'id' are defined from args; you may need to parse them from args.
    # For demonstration, let's assume:
    # id = args[0]
    # test_name = args[1]
    if len(args) < 2:
        parser.error("You have to provide both an identifier and a test name.")

    id = args[0]
    test_name = args[1]

    test = getattr(measurements, test_name)

    msr = test(ide=id, config_path=config_path)
    msr.initialise()
    msr.execute()
    msr.finalise()

if __name__=="__main__":
    main()
