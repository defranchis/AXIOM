import measurements
import argparse
import subprocess
from config_validator import validate_config_structure


def format_name(sample_type, sample_id, dose = None):
    return( '{t}_{n}_{d}kGy'.format(t=sample_type, n=sample_id, d=dose) )

def main():

    parser = argparse.ArgumentParser(description="Validate YAML configuration file.")
    parser.add_argument("config_path", help="Path to the YAML config file")
    args = parser.parse_args()
    config = validate_config_structure(args.config_path)

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
                    args.config_path,
                    str(current_dose),
                    str(target_dose)
                ], check=True)
                current_dose = target_dose 

                msr = test(ide=format_name(config['sample']['type'], config['sample']['id'], current_dose), config_path=args.config_path, current_dose=current_dose)
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
