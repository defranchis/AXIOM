import measurements
from optparse import OptionParser
import yaml
import subprocess
from config_validator import validate_config_structure


def format_name(sample_type, sample_id, dose = None):
    return( '{t}_{n}_{d}kGy'.format(t=sample_type, n=sample_id, d=dose) )

def main():


    # TODO: remove option parser and just get an argument form the CLI since supplying the config file is mandatory.
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_path", help="Path to YAML config file")
    (options, args) = parser.parse_args()

    if not options.config_path:
        parser.error("The --config option must be specified.")


    #TODO: consolidate the config loading and validation logic.
    config_path = options.config_path
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        print(yaml.dump(config, default_flow_style=False))

    is_valid, warnings = validate_config_structure(config_path)

    if not is_valid:
        print("Configuration file has errors:")
        for warning in warnings:
            print(f"- {warning}")
            a = input('config has errors, would you like to continue? (y/n): ')
        if a.lower() != 'y':
            print("Exiting due to configuration errors.")
            return
    else:
        print("Configuration is valid, proceeding with measurement.")


    test = getattr(measurements, config['measurement_type'])


    #TODO: improve loop logic to avoid code duplication. DRY principle.
    # if irradiation is present in config, run for loop with irradiation steps + measurement. 
    if "irradiation" in config:
        irradiation = config["irradiation"]
        dose_steps = irradiation.get("doselist", [])
        
        try:
            current_dose = 0
            for target_dose in dose_steps:
                
                subprocess.run([
                    'python',
                    './obelixControl.py',
                    config_path,
                    str(current_dose),
                    str(target_dose)
                ], check=True)
                current_dose = target_dose 

                msr = test(ide=format_name(config['sample']['type'], config['sample']['id'], current_dose), config_path=config_path, current_dose=current_dose)
                msr.initialise()
                msr.execute()
                msr.finalise()
        except subprocess.CalledProcessError as e:
                subprocess.run(['python', '.\obelixControl.py', 'killObelix'])
                print(f"An error occurred while running obelixControl.py: {e}")
        except Exception as e:
            subprocess.run(['python', '.\obelixControl.py', 'killObelix'])
            print(f"An unexpected error occurred: {e}")

    # if irradiation is not present, run measurement only.
    else:
        msr = test(ide=format_name(config['sample']['type'], config['sample']['id']), config_path=config_path)
        msr.initialise()
        msr.execute()
        msr.finalise()




if __name__=="__main__":
    main()
