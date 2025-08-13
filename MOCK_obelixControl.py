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
        print("OBELIX MOCK ERROR: Dose rate cannot be zero or None.")
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
    print(f"OBELIX MOCK: Setting voltage to {voltage} kV.")
    time.sleep(0.1)  # Simulate a small hardware delay
    return voltage

def setCurrent(current):
    """Mock function to simulate setting the current."""
    print(f"OBELIX MOCK: Setting current to {current} mA.")
    time.sleep(0.1)
    return current

def turnHVOn():
    """Mock function to simulate turning on the High Voltage."""
    print("OBELIX MOCK: Turning HV ON.")
    time.sleep(0.2)  # Simulate HV ramp-up

def openShutter(shutter_number, override=''):
    """Mock function to simulate opening the shutter."""
    print(f"OBELIX MOCK: Opening shutter {shutter_number} with override='{override}'.")
    return 1  # Return a success code

def statusRead4():
    """Mock function for a status check. Always returns success."""
    return 1

def generalWarnings(port_mock):
    """Mock function for checking warnings. Does nothing."""
    pass

def biasMOS2000_ON(channel):
    """Mock function to simulate turning on biasing voltage."""
    print(f"OBELIX MOCK: Bias ON for channel {channel}.")

def biasMOS2000_OFF(channel):
    """Mock function to simulate turning off biasing voltage."""
    print(f"OBELIX MOCK: Bias OFF for channel {channel}.")

def kill_procedure():
    """A consolidated mock shutdown procedure for errors or kill commands."""
    print("\nOBELIX MOCK: SHUTDOWN SEQUENCE INITIATED.")
    print("OBELIX MOCK: Closing shutter 3.")
    print("OBELIX MOCK: Turning HV OFF.")
    # Assuming channel 3 for the mock, as it's common in the original script
    biasMOS2000_OFF(channel=3)
    print("OBELIX MOCK: System shutdown complete.")


# --- Main Execution Block (Adapted from the original script) ---

if __name__ == '__main__':

    args = sys.argv

    # Handle the 'killObelix' command, which is a special case
    if len(args) > 1 and args[-1] == 'killObelix':
        print('OBELIX MOCK: Received "killObelix" command!')
        kill_procedure()
        exit(0)

    # --- Argument and Config File Parsing ---
    if len(args) < 4:
        print("MOCK ERROR: Not enough arguments.")
        print("Usage: python obelixControl.py <config_path> <current_dose> <target_dose>")
        exit(1)

    config_path = args[1]
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            print("OBELIX MOCK: Successfully loaded config file.")
    except FileNotFoundError:
        print(f"MOCK ERROR: Config file not found at '{config_path}'")
        exit(1)
    except Exception as e:
        print(f"MOCK ERROR: Failed to load or parse YAML config: {e}")
        exit(1)

    try:
        current_dose = float(args[2])
        target_dose = float(args[3])
    except ValueError:
        print("MOCK ERROR: current_dose and target_dose must be numbers.")
        exit(1)


    if current_dose >= target_dose:
        print("OBELIX MOCK: Current dose is greater than or equal to target dose. No work to do, exiting.")
        exit(0)

    dose_to_irradiate = target_dose - current_dose
    print(f'OBELIX MOCK: Will irradiate from {current_dose} to {target_dose} kGy (a total of {dose_to_irradiate:.2f} kGy).')
    time.sleep(1)

    # --- Main Simulated Irradiation Procedure ---
    try:
        # 1. Set machine parameters from config
        setVoltage(config['irradiation']['voltage'])
        setCurrent(config['irradiation']['current'])

        # 2. Calculate total irradiation time
        dose_rate = config['irradiation']['dose_rate']
        hours, minutes, seconds = convertkGyToTime(dose_to_irradiate, dose_rate=dose_rate)
        total_irradiation_seconds = hours * 3600 + minutes * 60 + seconds

        if total_irradiation_seconds <= 0:
            print("OBELIX MOCK: Calculated irradiation time is zero or negative. Exiting.")
            exit(0)
            
        print(f"OBELIX MOCK: Calculated irradiation time: {hours}h {minutes}m {seconds}s (Total: {total_irradiation_seconds}s)")

        # 3. Simulate turning on the machine
        turnHVOn()
        if config.get('irradiation', {}).get('biasing', False):
            bias_channel = config.get('devices', {}).get('switch', {}).get('connections', {}).get('biasMOS2000', 3)
            biasMOS2000_ON(channel=bias_channel)

        openShutter(3, 'yes')  # Assume shutter 3 and override user input

        # 4. Main simulation loop
        start_time = time.time()
        remainingTimeInSeconds = total_irradiation_seconds

        while remainingTimeInSeconds > 0:
            elapsed_time = time.time() - start_time
            remainingTimeInSeconds = total_irradiation_seconds - elapsed_time

            if remainingTimeInSeconds < 0:
                remainingTimeInSeconds = 0

            # Get H:M:S for display
            h, m, s = secondsToHoursMinutesAndSeconds(remainingTimeInSeconds)

            # Print status update on a single line for a clean look
            print(f'\rOBELIX MOCK: Irradiating... Time remaining: {h:02d}h {m:02d}m {s:02d}s', end='')

            statusRead4()      # Simulate status check
            generalWarnings(None)  # Simulate warnings check

            time.sleep(1)      # Wait for 1 second to simulate real time

        print("\nOBELIX MOCK: Irradiation complete!")

        # 5. Simulate normal shutdown
        if config.get('irradiation', {}).get('biasing', False):
             bias_channel = config.get('devices', {}).get('switch', {}).get('connections', {}).get('biasMOS2000', 3)
             biasMOS2000_OFF(channel=bias_channel)
        
        print("OBELIX MOCK: Simulating closing shutter and turning off HV.")

    except (KeyboardInterrupt, Exception) as e:
        print(f'\nOBELIX MOCK: EXCEPTION RAISED! ({type(e).__name__})')
        kill_procedure()
        exit(1) # Exit with an error code so subprocess.run can catch it

    print("OBELIX MOCK: Script finished successfully.")
    exit(0)