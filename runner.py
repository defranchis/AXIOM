import measurements
import argparse
import subprocess
from utils.config_validator import validate_config_structure 
import time
import datetime

def run_measurement(msr_class, config, current_dose=None, n_annealing = None):
    """Encapsulates the repeated measurement steps."""
    msr = msr_class(config=config, current_dose=current_dose, n_annealing=n_annealing)
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


def run_annealing_loop(config, msr_class):
    """
    Runs repeated measurements during annealing steps at a configured time interval.
    
    Assumes the annealing period is given in minutes.
    """
    period_min = config["annealing"].get("period", 60)
    period_sec = period_min * 60
    n_annealing = 0

    print(f"[{datetime.datetime.now().isoformat()}] Starting annealing loop every {period_min} min.")

    try:
        while True:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Running annealing measurement step {n_annealing}...")

            try:
                run_measurement(msr_class, config, n_annealing=n_annealing)
            except Exception as e:
                print(f"[{timestamp}] Error during measurement step {n_annealing}: {e}")
                break

            n_annealing += 1
            print(f"[{timestamp}] Sleeping for {period_min} minutes...")
            time.sleep(period_sec)

    except KeyboardInterrupt:
        print("\nAnnealing loop interrupted by user (Ctrl+C).")



def main():
    parser = argparse.ArgumentParser(description="Validate YAML configuration file.")
    parser.add_argument("config_path", help="Path to the YAML config file")
    args = parser.parse_args()

    config = validate_config_structure(args.config_path)
    msr_class = getattr(measurements, config['measurement_type'])

    if "irradiation" in config:
        run_irradiation_loop(config, msr_class, args.config_path)
    elif "annealing" in config:
        run_annealing_loop(config, msr_class)
    else:
        run_measurement(msr_class, config)

if __name__ == "__main__":
    main()
