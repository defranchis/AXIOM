import argparse
import measurements
import subprocess
import time
import queue
import datetime
from utils.config_validator import validate_config_structure 
import multiprocessing
from temperature_management import ThermalManager as TM 

def run_measurement(msr_class, config, current_dose=None, n_annealing = None, tm_queue= None):
    """Encapsulates the repeated measurement steps."""
    msr = msr_class(config=config, current_dose=current_dose, n_annealing=n_annealing)
    msr.initialise()
    msr.execute()
    msr.finalise()


def run_irradiation_loop(config, msr_class, config_path, tm_queue = None):
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


def run_annealing_loop(config, msr_class, tm_queue = None):
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



# def run_temperature_management(config_path):
#     """This function will be the target for our new process."""
#     try:
#         subprocess.run(
#             ['python', './temperature_management/ThermalManager.py', '--config', config_path], 
#             check=True
#         )
#     except Exception as e:
#         print(f'Exception during temperature management execution: {e}')


def temperature_worker(config_path, command_queue):
    """
    This function runs in the background process. It initializes and runs the manager.
    need to pass config_path since the tm can also run standalone. 
    """
    manager = TM.ThermalManager(config_path = config_path, command_queue=command_queue)
    manager.run()

def main():
    parser = argparse.ArgumentParser(description="Validate YAML configuration file.")
    parser.add_argument("config_path", help="Path to the YAML config file")
    args = parser.parse_args()
    config_path = args.config_path
    config = validate_config_structure(config_path)
    msr_class = getattr(measurements, config['measurement_type'])

    tm_queue = None # preinit to ensure correct parsing when running without chiller, when tm_process has tm_queue = None, 

    if "temperature_management" in config:
        #TODO: why not always run with a cmd queue, even when executing without a chiller? (maybe to enable standalone execution logic? )
        if config['temperature_management']['chiller']['enabled']:
            tm_queue = multiprocessing.Queue()  

        # 2. Create and start the background process
        print("Starting temperature management in the background...")
        tm_process = multiprocessing.Process(
            target=temperature_worker, 
            args=(config_path, tm_queue) # Pass config and queue
        )
        tm_process.daemon = True 
        tm_process.start()
        time.sleep(2)

    if "irradiation" in config:
        run_irradiation_loop(config, msr_class, config_path, tm_queue=tm_queue)
    elif "annealing" in config:
        run_annealing_loop(config, msr_class, tm_queue=tm_queue)
    else:
        run_measurement(msr_class, config, tm_queue=tm_queue)

    #TODO: ADD PROPER PARSING OF INCOMING KEYBOARD INTERRUPT, CLOSING DEVICES, RAMPING DOWN VOLTAGES ETC. IF THIS IS NOT CAUGHT IN ONE OF THE SUBPROCESSES, IT SHOULD BE CAUGHT HERE. 

if __name__ == "__main__":
    main()