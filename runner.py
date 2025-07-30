import measurements
import argparse
import subprocess
from config_validator import validate_config_structure

def run_measurement(msr_class, config, current_dose=None):
    """Encapsulates the repeated measurement steps."""
    msr = msr_class(config=config, current_dose=current_dose)
    msr.initialise()
    msr.execute()
    msr.finalise()

def run_irradiation_loop(config, msr_class, config_path):
    """Handles irradiation dose steps and runs measurements."""
    irradiation = config["irradiation"]
    dose_steps = irradiation.get("doselist", [])
    current_dose = 0

    try:
        for target_dose in dose_steps:
            subprocess.run(
                ['python', './obelixControl.py', config_path, str(current_dose), str(target_dose)],
                check=True
            )
            current_dose = target_dose
            run_measurement(msr_class, config, current_dose=current_dose)

    except subprocess.CalledProcessError as e:
        subprocess.run(['python', './obelixControl.py', 'killObelix'])
        print(f"obelixControl failed: {e}")
    except Exception as e:
        subprocess.run(['python', './obelixControl.py', 'killObelix'])
        print(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Validate YAML configuration file.")
    parser.add_argument("config_path", help="Path to the YAML config file")
    args = parser.parse_args()

    config = validate_config_structure(args.config_path)
    msr_class = getattr(measurements, config['measurement_type'])

    if "irradiation" in config:
        run_irradiation_loop(config, msr_class, args.config_path)
    else:
        run_measurement(msr_class, config)

if __name__ == "__main__":
    main()
