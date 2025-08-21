import sys
import time
import datetime
import yaml

# --- Mock Functions ---
# These functions replace the original hardware-controlling functions with simple simulations.

def convertkGyToTime(nkGy, dose_rate):
    """
    Calculates irradiation time from dose and dose rate. 
    This logic is identical to the original script.
    """
    if dose_rate is None or dose_rate == 0:
        print("OBELIX MOCK ERROR: Dose rate cannot be zero or None.", flush=True)
        return 0, 0, 0
    nSeconds = int(3600. / dose_rate * nkGy)
    hms = str(datetime.timedelta(seconds=nSeconds))
    hms_list = [int(i) for i in hms.split(':')]
    return hms_list[0], hms_list[1], hms_list[2]

def secondsToHoursMinutesAndSeconds(seconds):
    """
    Converts a total number of seconds into hours, minutes, and seconds.
    This logic is identical to the original script.
    """
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return [hours, minutes, remaining_seconds]

def setVoltage(voltage):
    """Mock function to simulate setting the voltage."""
    print(f"OBELIX MOCK: Setting voltage to {voltage} kV.", flush=True)
    time.sleep(0.1)  # Simulate a small hardware delay
    return voltage

def setCurrent(current):
    """Mock function to simulate setting the current."""
    print(f"OBELIX MOCK: Setting current to {current} mA.", flush=True)
    time.sleep(0.1)
    return current

def turnHVOn():
    """Mock function to simulate turning on the High Voltage."""
    print("OBELIX MOCK: Turning HV ON.", flush=True)
    time.sleep(0.2)  # Simulate HV ramp-up

def openShutter(shutter_number, override=''):
    """Mock function to simulate opening the shutter."""
    print(f"OBELIX MOCK: Opening shutter {shutter_number} with override='{override}'.", flush=True)
    return 1  # Return a success code

def statusRead4():
    """Mock function for a status check. Always returns success."""
    return 1

def generalWarnings(port_mock):
    """Mock function for checking warnings. Does nothing."""
    pass

def biasMOS2000_ON(channel):
    """Mock function to simulate turning on biasing voltage."""
    print(f"OBELIX MOCK: Bias ON for channel {channel}.", flush=True)

def biasMOS2000_OFF(channel):
    """Mock function to simulate turning off biasing voltage."""
    print(f"OBELIX MOCK: Bias OFF for channel {channel}.", flush=True)

def kill_procedure():
    """A consolidated mock shutdown procedure for errors or kill commands."""
    print("\nOBELIX MOCK: SHUTDOWN SEQUENCE INITIATED.", flush=True)
    print("OBELIX MOCK: Closing shutter 3.", flush=True)
    print("OBELIX MOCK: Turning HV OFF.", flush=True)
    # Assuming channel 3 for the mock, as it's common in the original script
    biasMOS2000_OFF(channel=3)
    print("OBELIX MOCK: System shutdown complete.", flush=True)


# --- Helper: compute accumulated dose (same logic as the real script) ---
def compute_accumulated_dose(remaining_seconds, total_seconds, current_dose_kGy, dose_rate_kGy_per_hr):
    """
    remaining_seconds: seconds left on timer (float or int)
    total_seconds: total irradiation seconds planned (int)
    current_dose_kGy: starting dose before this irradiation (float)
    dose_rate_kGy_per_hr: kGy per hour (float)
    returns (accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds)
    """
    try:
        total_seconds = int(total_seconds)
        remaining_seconds = int(max(0, remaining_seconds))
        elapsed = max(0, int(total_seconds - remaining_seconds))
        dose_delivered = (elapsed * float(dose_rate_kGy_per_hr)) / 3600.0
        accumulated = float(current_dose_kGy) + dose_delivered
        return accumulated, dose_delivered, elapsed
    except Exception:
        # In case of unexpected inputs, return sensible defaults
        return float(current_dose_kGy), 0.0, 0


# --- Main Execution Block (Adapted from the original script) ---

if __name__ == '__main__':

    args = sys.argv

    # Handle the 'killObelix' command, which is a special case
    if len(args) > 1 and args[-1] == 'killObelix':
        print('OBELIX MOCK: Received "killObelix" command!', flush=True)
        kill_procedure()
        exit(0)

    # --- Argument and Config File Parsing ---
    if len(args) < 4:
        print("MOCK ERROR: Not enough arguments.", flush=True)
        print("Usage: python obelixControl.py <config_path> <current_dose> <target_dose>", flush=True)
        exit(1)

    config_path = args[1]
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            print("OBELIX MOCK: Successfully loaded config file.", flush=True)
    except FileNotFoundError:
        print(f"MOCK ERROR: Config file not found at '{config_path}'", flush=True)
        exit(1)
    except Exception as e:
        print(f"MOCK ERROR: Failed to load or parse YAML config: {e}", flush=True)
        exit(1)

    try:
        current_dose = float(args[2])
        target_dose = float(args[3])
    except ValueError:
        print("MOCK ERROR: current_dose and target_dose must be numbers.", flush=True)
        exit(1)


    if current_dose >= target_dose:
        print("OBELIX MOCK: Current dose is greater than or equal to target dose. No work to do, exiting.", flush=True)
        exit(0)

    dose_to_irradiate = target_dose - current_dose
    print(f'OBELIX MOCK: Will irradiate from {current_dose} to {target_dose} kGy (a total of {dose_to_irradiate:.6f} kGy).', flush=True)
    time.sleep(1)

    # --- Main Simulated Irradiation Procedure ---
    try:
        # 1. Set machine parameters from config
        setVoltage(config['irradiation']['voltage'])
        setCurrent(config['irradiation']['current'])

        # 2. Calculate total irradiation time
        dose_rate = config['irradiation'].get('dose_rate', None)
        hours, minutes, seconds = convertkGyToTime(dose_to_irradiate, dose_rate=dose_rate)
        total_irradiation_seconds = int(hours * 3600 + minutes * 60 + seconds)

        if total_irradiation_seconds <= 0:
            print("OBELIX MOCK: Calculated irradiation time is zero or negative. Exiting.", flush=True)
            exit(0)
            
        print(f"OBELIX MOCK: Calculated irradiation time: {hours}h {minutes}m {seconds}s (Total: {total_irradiation_seconds}s)", flush=True)

        # 3. Simulate turning on the machine
        turnHVOn()
        if config.get('irradiation', {}).get('biasing', False):
            bias_channel = config.get('devices', {}).get('switch', {}).get('connections', {}).get('biasMOS2000', 3)
            biasMOS2000_ON(channel=bias_channel)

        openShutter(3, 'yes')  # Assume shutter 3 and override user input

        # 4. Main simulation loop with in-place console updates and flushing
        start_time = time.time()
        remainingTimeInSeconds = total_irradiation_seconds

        # Single-line display formatting:
        # We'll overwrite the same line each second. Use '\r' + ANSI clear line '\x1b[K' to ensure cleanup.
        # After the loop completes we print final results on separate lines.
        while remainingTimeInSeconds > 0:
            elapsed_time = time.time() - start_time
            remainingTimeInSeconds = total_irradiation_seconds - elapsed_time
            if remainingTimeInSeconds < 0:
                remainingTimeInSeconds = 0

            # Compute accumulated dose using helper
            accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(
                remaining_seconds=remainingTimeInSeconds,
                total_seconds=total_irradiation_seconds,
                current_dose_kGy=current_dose,
                dose_rate_kGy_per_hr=dose_rate
            )

            # Get H:M:S for display
            h, m, s = secondsToHoursMinutesAndSeconds(remainingTimeInSeconds)

            # Build a single status line: time remaining + dose delivered + accumulated dose
            status_line = (
                f"OBELIX MOCK: Time remaining: {h:02d}h {m:02d}m {s:02d}s | "
                f"Delivered (this run): {dose_delivered_kGy:.6f} kGy | "
                f"Accumulated: {accumulated_total_kGy:.6f} kGy"
            )

            # Overwrite the previous line and flush immediately
            # '\r' returns to start, '\x1b[K' clears the line (ANSI). Works on modern terminals.
            print('\r\x1b[K' + status_line, end='', flush=True)

            statusRead4()      # Simulate status check
            generalWarnings(None)  # Simulate warnings check

            time.sleep(1)      # Wait for 1 second to simulate real time

        # Normal end of loop: print final results on a clean new line
        print()  # move to next line
        print("OBELIX MOCK: Irradiation complete!", flush=True)

        # 5. Final accumulated dose report (normal completion)
        accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(
            remaining_seconds=0,
            total_seconds=total_irradiation_seconds,
            current_dose_kGy=current_dose,
            dose_rate_kGy_per_hr=dose_rate
        )
        print(f'OBELIX MOCK: Final dose delivered this run: {dose_delivered_kGy:.6f} kGy', flush=True)
        print(f'OBELIX MOCK: Final total accumulated dose: {accumulated_total_kGy:.6f} kGy', flush=True)

        # 6. Simulate normal shutdown
        if config.get('irradiation', {}).get('biasing', False):
             bias_channel = config.get('devices', {}).get('switch', {}).get('connections', {}).get('biasMOS2000', 3)
             biasMOS2000_OFF(channel=bias_channel)
        
        print("OBELIX MOCK: Simulating closing shutter and turning off HV.", flush=True)

    except (KeyboardInterrupt, Exception) as e:
        # Attempt to determine elapsed/remaining time and compute accumulated dose before shutdown
        try:
            # try to compute remaining value if loop got interrupted
            try:
                # if start_time exists, compute elapsed from it
                elapsed_time = time.time() - start_time if 'start_time' in globals() else 0
                remaining = max(0, total_irradiation_seconds - elapsed_time) if 'total_irradiation_seconds' in globals() else None
            except Exception:
                remaining = None

            if remaining is None:
                print(f'\nOBELIX MOCK: EXCEPTION RAISED! ({type(e).__name__})', flush=True)
                print('OBELIX MOCK: Could not determine remaining time; printing baseline current dose only.', flush=True)
                print(f'OBELIX MOCK: Current dose before run: {current_dose:.6f} kGy', flush=True)
            else:
                accumulated_total_kGy, dose_delivered_kGy, elapsed_seconds = compute_accumulated_dose(
                    remaining_seconds=remaining,
                    total_seconds=total_irradiation_seconds,
                    current_dose_kGy=current_dose,
                    dose_rate_kGy_per_hr=dose_rate
                )
                print(f'\nOBELIX MOCK: EXCEPTION RAISED! ({type(e).__name__})', flush=True)
                print('OBELIX MOCK: Irradiation stopped unexpectedly.', flush=True)
                print(f'OBELIX MOCK: Dose delivered before stop: {dose_delivered_kGy:.6f} kGy', flush=True)
                print(f'OBELIX MOCK: Total accumulated dose = {accumulated_total_kGy:.6f} kGy', flush=True)

        except Exception as e2:
            # If any reporting fails, at least print baseline
            print(f'\nOBELIX MOCK: Error while reporting accumulated dose: {e2}', flush=True)
            print(f'OBELIX MOCK: Current dose before run: {current_dose:.6f} kGy', flush=True)

        # run consolidated shutdown procedure and exit with error code
        kill_procedure()
        exit(1) # Exit with an error code so subprocess.run can catch it

    print("OBELIX MOCK: Script finished successfully.", flush=True)
    exit(0)
