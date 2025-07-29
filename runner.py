import measurements
from optparse import OptionParser
import yaml
import subprocess



def format_name(sample_type, sample_id, dose = None):
    return( '{t}_{n}_{d}kGy'.format(t=sample_type, n=sample_id, d=dose) )

def main():


    # TODO: remove option parser and just get an argument form the CLI since supplying the config file is mandatory.
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_path", help="Path to YAML config file")
    (options, args) = parser.parse_args()

    if not options.config_path:
        parser.error("The --config option must be specified.")

    config_path = options.config_path
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    test = getattr(measurements, config['test_name'])

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

                msr = test(ide=format_name(config['sample_type'], config['sample_id'], current_dose), config_path=config_path)
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
        msr = test(ide=format_name(config['sample_type'], config['sample_id']), config_path=config_path)
        msr.initialise()
        msr.execute()
        msr.finalise()




if __name__=="__main__":
    main()
