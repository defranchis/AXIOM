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
    """
    Handles irradiation dose steps and runs measurements.
    This function can resume a run if a `preexisting_dose` is set in the config,
    by finding the first target in the `doselist` greater than the preexisting dose.
    """
    irradiation = config["irradiation"]
    dose_steps = irradiation.get("doselist", [])
    
    # Start with the dose that is already on the sample.
    current_dose = config['sample'].get('preexisting_dose', 0)

    # Filter the dose list to find only the steps that still need to be run.
    # This allows the run to be resumed cleanly after a failure.
    targets_to_run = [dose for dose in dose_steps if dose > current_dose]

    if not targets_to_run and dose_steps:
        print(f"INFO: All target doses in {dose_steps} are less than or equal to the preexisting_dose of {current_dose} kGy.")
        print("No further irradiation will be performed.")
        return # Exit the function if there's nothing left to do.

    print(f"Starting irradiation run. Preexisting dose: {current_dose} kGy.")
    print(f"Remaining dose steps to be applied: {targets_to_run}")
    
    try:
        print(f"\n--- Running INITIAL measurement with total accumulated dose: {current_dose:.2f} kGy ---")
        run_measurement(msr_class, config, current_dose=current_dose)

        # Loop only through the remaining, filtered dose steps
        for target_dose in targets_to_run:
            print(f"\n--- Irradiating from {current_dose:.2f} kGy to {target_dose:.2f} kGy ---")
            
            # The target dose is an absolute value. 
            # obelixControl is responsible for calculating the difference to irradiate.
            subprocess.run(
                ['python', './MOCK_obelixControl.py', config_path, str(current_dose), str(target_dose)],
                check=True
            )

            # After successful irradiation, update the current dose to the new total.
            current_dose = target_dose

            print(f"\n--- Running measurement for total accumulated dose: {current_dose:.2f} kGy ---")
            # Pass the new total accumulated dose to the measurement function.
            run_measurement(msr_class, config, current_dose=current_dose)

    except subprocess.CalledProcessError as e:
        # If obelix fails, call the kill script and print the error.
        print(f"\n!!! obelixControl failed: {e} !!!")
        subprocess.run(['python', './MOCK_obelixControl.py', 'killObelix'])
    except Exception as e:
        # Catch any other unexpected errors during the loop.
        print(f"\n!!! An unexpected error occurred in the irradiation loop: {e} !!!")
        subprocess.run(['python', './MOCK_obelixControl.py', 'killObelix'])

def run_annealing_loop(config, msr_class, tm_queue = None):
    """ Runs repeated measurements during annealing steps at a configured time interval. """
    period_min = config["annealing"].get("period", 60)
    period_sec = period_min * 60
    print(f"[{datetime.datetime.now().isoformat()}] Starting annealing loop every {period_min} min.")
    try:
        for n_annealing in range(config['annealing']['n_iterations']):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Running annealing measurement step {n_annealing}...")
            try:
                if tm_queue is not None:
                    tm_queue.put(config['annealing']['measur_temp'])
                run_measurement(msr_class, config, n_annealing=n_annealing)
            except Exception as e:
                print(f"[{timestamp}] Error during measurement step {n_annealing}: {e}")
                break
            if tm_queue is not None:
                tm_queue.put(config['annealing']['anneal_temp'])
            n_annealing += 1
            print(f"[{timestamp}] Sleeping for {period_min} minutes...")
            time.sleep(period_sec)
    except KeyboardInterrupt:
        print("\nAnnealing loop interrupted by user (Ctrl+C).")

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
        #TODO: why not always run with a cmd queue, even when executing without a chiller?
        if config['temperature_management']['chiller']['enabled']:
            tm_queue = multiprocessing.Queue()  
        # Create and start the background process
        print("Starting temperature management in the background...")
        tm_process = multiprocessing.Process(
            target=temperature_worker, 
            args=(config_path, tm_queue) # Pass config and queue
        )
        tm_process.daemon = True 
        tm_process.start()
        time.sleep(2)
        input("Temperature management initialized. Press ENTER to continue")
    if "irradiation" in config:
        run_irradiation_loop(config, msr_class, config_path, tm_queue=tm_queue)
    elif "annealing" in config:
        run_annealing_loop(config, msr_class, tm_queue=tm_queue)
    else:
        run_measurement(msr_class, config, tm_queue=tm_queue)
    #TODO: ADD PROPER PARSING OF INCOMING KEYBOARD INTERRUPT, CLOSING DEVICES, RAMPING DOWN VOLTAGES ETC. IF THIS IS NOT CAUGHT IN ONE OF THE SUBPROCESSES, IT SHOULD BE CAUGHT HERE. 
    #TODO: this is to avoid the somewhat rare behaviour of rampdown not being triggered by a keyboard interrupt.  

if __name__ == "__main__":
    main()
