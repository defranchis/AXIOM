import time
import random

class chiller_cc_505:
    """
    Dummy class for the Huber CC-505 chiller to simulate its behavior
    for testing the ThermalManager without the actual hardware.
    It perfectly mirrors the public methods and behavior of the real class.
    """

    def __init__(self, port: str = 'COM5'):
        """Initializes the simulated chiller's state."""
        print(f"✅ DummyChiller: Initialized on fake port '{port}'.")
        self.port = port
        
        # --- Internal State Simulation ---
        self._is_on = False
        self._start_time = None
        self._setpoint = 20.0  # Default setpoint in °C
        self._internal_temp = 22.0 # Start at a typical ambient temperature
        self._ambient_temp = 22.0 # The temperature the chiller drifts towards when off
        
        # --- Simulation Parameters ---
        self._cooling_factor = 0.1 # Determines how fast the temp changes towards setpoint
        self._noise_amplitude = 0.05 # Creates realistic small fluctuations

    def turn_on_off(self, mode: str, min_runtime: int = 300):
        """Simulates turning the chiller on or off, respecting min_runtime."""
        if mode.lower() == 'on':
            if not self._is_on:
                print("💡 DummyChiller: Turning ON.")
                self._is_on = True
                self._start_time = time.time()
            return None # No error
            
        elif mode.lower() == 'off':
            if self._start_time and (time.time() - self._start_time) < min_runtime:
                remaining = min_runtime - (time.time() - self._start_time)
                msg = f'The minimum run-time of the chiller is not yet lapsed! Wait {remaining:.1f}s.'
                print(f"⚠️ DummyChiller: {msg}")
                return msg # Mimic error message
            
            if self._is_on:
                print("💡 DummyChiller: Turning OFF.")
                self._is_on = False
                self._start_time = None
            return None # No error
            
        else:
            print(f'❌ DummyChiller: Invalid mode "{mode}". Use "on" or "off".')

    def set_point(self, setpoint_temperature: int):
        """Sets a new simulated temperature setpoint."""
        # The real class expects temp*100, but the ThermalManager provides the direct temp.
        # We just store the direct temperature.
        self._setpoint = float(setpoint_temperature)
        print(f"🎯 DummyChiller: New setpoint received -> {self._setpoint}°C")

    def _simulate_temperature_change(self):
        """Private method to update internal temperatures based on state."""
        noise = random.uniform(-self._noise_amplitude, self._noise_amplitude)

        if self._is_on:
            # If on, move temperature towards the setpoint (simple first-order dynamics)
            diff = self._setpoint - self._internal_temp
            self._internal_temp += diff * self._cooling_factor + noise
        else:
            # If off, drift slowly towards ambient temperature
            diff = self._ambient_temp - self._internal_temp
            self._internal_temp += diff * (self. _cooling_factor / 2) + noise

    def read_setpoint(self):
        """Returns the current simulated setpoint."""
        return self._setpoint

    def read_internal_temperature(self):
        """Reads the simulated internal temperature, updating it in the process."""
        self._simulate_temperature_change()
        return self._internal_temp

    def read_external_temperature(self):
        """Reads a simulated external temperature, which just follows the internal one."""
        # For simplicity, external temp is just internal temp with a slight offset.
        return self._internal_temp - 0.2 + (random.uniform(-0.1, 0.1))

    def check_status(self):
        """Returns the simulated status: 1 for ON, 0 for OFF."""
        return 1 if self._is_on else 0

    def close(self):
        """Simulates closing the connection."""
        print(f"✅ DummyChiller: Closing connection on fake port '{self.port}'.")
        self._is_on = False