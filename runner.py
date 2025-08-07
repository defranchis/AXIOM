import argparse
import measurements
import subprocess
import time
import datetime
from utils.config_validator import validate_config_structure 

# Add this import at the top of your file
import multiprocessing

from temperature_management import ThermalManager as TM

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
    """ Runs repeated measurements during annealing steps at a configured time interval. """
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



def run_temperature_management(config_path):
    """This function will be the target for our new process."""
    try:
        # Use subprocess.run here as before, it's now inside the parallel process
        subprocess.run(
            ['python', './temperature_management/ThermalManager.py', '--config', config_path], 
            check=True
        )
    except Exception as e:
        print(f'Exception during temperature management execution: {e}')

def main():
    parser = argparse.ArgumentParser(description="Validate YAML configuration file.")
    parser.add_argument("config_path", help="Path to the YAML config file")
    args = parser.parse_args()

    config = validate_config_structure(args.config_path)
    msr_class = getattr(measurements, config['measurement_type'])

    # --- MODIFIED SECTION ---
    print("Starting temperature management in the background...")
    # Create a Process object targeting our function
    tm_process = multiprocessing.Process(
        target=run_temperature_management, 
        args=(args.config_path,)
    )
    # Set as a daemon process to exit when the main script exits
    tm_process.daemon = True 
    tm_process.start() # Start the process
    # --- END MODIFIED SECTION ---

    # Your main script continues immediately to this part
    if "irradiation" in config:
        run_irradiation_loop(config, msr_class, args.config_path)
    elif "annealing" in config:
        run_annealing_loop(config, msr_class)
    else:
        run_measurement(msr_class, config)

    print("Main measurement task finished.")
    # No need to explicitly stop the daemon process, it will be terminated.

if __name__ == "__main__":
    main()