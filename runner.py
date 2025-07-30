import measurements
import argparse
import subprocess
from config_validator import validate_config_structure

def main():

    parser = argparse.ArgumentParser(description="Validate YAML configuration file.")
    parser.add_argument("config_path", help="Path to the YAML config file")
    args = parser.parse_args()
    config = validate_config_structure(args.config_path)

    msr_class = getattr(measurements, config['measurement_type'])


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
                    args.config_path,  # need to pass path since we cannot provide the entire config as a dict when calling as subprocess
                    str(current_dose),
                    str(target_dose)
                ], check=True)

                current_dose = target_dose 
                msr = msr_class(config=config, current_dose=current_dose)
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
        msr = msr_class(config=config)
        msr.initialise()
        msr.execute()
        msr.finalise()




if __name__=="__main__":
    main()
