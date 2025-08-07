import yaml
import time
import argparse
import logging
from pathlib import Path
from collections import deque
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from sympy import Symbol, solve
import sys
from pathlib import Path
import queue # Import the queue module for the 'Empty' exception

# This enables running the temperature monitor as a standalone script, as well as integrating it in the runner. 
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# all module / path dependent imports need to happen after the path adjustment. 
import devices

def R2T_PTX_ITS90(R: float, R0: float) -> float:
    """
    Converts resistance to temperature for a PTX sensor using the ITS-90 standard.
    Filters out complex roots and returns the first real root.
    """
    t = Symbol('t')
    A = 3.9083E-3
    B = -5.7750E-7
    C = -4.183E-12 if R > R0 else 0.0
    try:
        solution = solve(R - R0 * (1 + A * t + B * t**2 + C * (t - 100) * t**3), t)
        real_solutions = [s.evalf() for s in solution if s.is_real]
        if not real_solutions:
            raise ValueError(f"No real solution for R={R}, R0={R0}")
        return float(real_solutions[0])
    except Exception as e:
        logging.error(f"error in R2T_PTX conversion: {e}")
        return float('nan')

class ThermalManager:

    def __init__(self, config_path: str, command_queue=None):
        """Initializes the monitor, devices, logging, and plots based on a config file."""
        with open(config_path, 'r') as file:
            self.config_path = config_path 
            self.config = yaml.safe_load(file)
        
        self.command_queue = command_queue 
        self._setup_logging()
        self.is_running = True
        self.devices = {}
        self.plot_data = {}
        self.plot_lines = {}
        self.plot_axes = {}
        
        self._setup_devices()
        self._setup_plot()

    def _setup_logging(self):
        """Configures file-based logging."""
        log_dir = Path(self.config['temperature_management']['logging']['directory'])
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file_path = log_dir / f'temperature_log_{timestamp}.dat'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file_path),
                logging.StreamHandler()
            ]
        )
        logging.info("Thermal Monitor Started")
        logging.info(f"Configuration loaded from: {self.config_path}")

    def _setup_devices(self):
        """Initializes hardware devices based on the config file."""
        # --- Multimeter Setup ---
        try:
            multi_conf = self.config['devices']['multimeter']
            multimeter_class = getattr(devices, multi_conf['model'])
            self.devices['multimeter'] = multimeter_class(multi_conf['address'])
            self.devices['multimeter'].reset()
            self.devices['multimeter'].set_sense('resistance')
            self.devices['multimeter'].set_terminal('rear')
            self.devices['multimeter'].set_nplc(10)
        except Exception as e:
            logging.error(f"Failed to initialize multimeter: {e}")
            self.devices['multimeter'] = None
            
        # --- Chiller Setup ---
        if self.config['temperature_management']['chiller']['enabled']:
            try:
                chiller_conf = self.config['temperature_management']['chiller']
                chiller_class = getattr(devices, chiller_conf['model'])
                self.devices['chiller'] = chiller_class(chiller_conf['port'])
                self.temperature_setpoint = chiller_conf['default_temperature']
                self.devices['chiller'].set_point(self.temperature_setpoint)
                
            except Exception as e:
                logging.error(f"Failed to initialize chiller: {e}")
                self.devices['chiller'] = None
        else:
            logging.info("Chiller is disabled in the configuration.")

    def _setup_plot(self):
        """Creates the matplotlib figure and axes for real-time plotting."""
        plt.style.use('ggplot')
        num_plots = 1 + (3 if self.config['temperature_management']['chiller']['enabled'] and self.devices.get('chiller') else 0)
        
        self.fig, all_axes = plt.subplots(num_plots, 1, figsize=(8, 2 * num_plots), sharex=True)
        all_axes = np.atleast_1d(all_axes) # Ensure it's iterable even with 1 plot
        
        plot_map = self._get_plot_map()
        
        for ax, (name, details) in zip(all_axes, plot_map.items()):
            self.plot_axes[name] = ax
            window_size = 600
            self.plot_data[name] = {'time': deque(maxlen=window_size), 'temp': deque(maxlen=window_size)}
            self.plot_lines[name] = ax.plot([], [], color=details['color'], label=details['label'])[0]
            ax.set_ylabel("Temp (°C)")
            ax.set_ylim([-35, 35])
            ax.legend(loc='upper left')
            ax.grid(True)

        all_axes[-1].set_xlabel("Time (s)")
        self.fig.tight_layout()
        plt.ion()
        plt.show()

    def _get_plot_map(self):
        """Returns a dictionary defining which sensors to plot."""
        plot_map = {}
        if self.devices.get('multimeter'):
            plot_map['pt1000'] = {'color': 'blue', 'label': 'PT1000'}
        if self.config['temperature_management']['chiller']['enabled'] and self.devices.get('chiller'):
            plot_map.update({
                'internal': {'color': 'green', 'label': 'Chiller Internal'},
                'external': {'color': 'orange', 'label': 'Chiller External'},
                'setpoint': {'color': 'red', 'label': 'Chiller Setpoint'}
            })
        return plot_map

    def _read_sensors(self) -> dict:
        """Reads data from all active sensors and returns a dictionary of values."""
        readings = {}
        if self.devices.get('multimeter'):
            try:
                r0 = float(self.config['devices']['multimeter']['sensor_r0']           )
                mm_reply = self.devices['multimeter'].read_resistance()
                if 'OOHM' in mm_reply: 
                    logging.warning(f"multimeter in overflow, reply: {mm_reply}")
                resistance = float(mm_reply.split(',')[0].replace('NOHM',''))
                readings['pt1000'] = R2T_PTX_ITS90(resistance, r0)
            except Exception as e:
                logging.warning(f"Could not read multimeter: {e}")
                readings['pt1000'] = float('nan')
        
        if self.config['temperature_management']['chiller']['enabled'] and self.devices.get('chiller'):
            chiller = self.devices['chiller']
            readings['internal'] = chiller.read_internal_temperature()
            readings['external'] = chiller.read_external_temperature()
            readings['setpoint'] = chiller.read_setpoint()
            
        return readings

    def _update_plot(self, current_time: float, readings: dict):
        """Updates the plot with new data."""
        for name, temp in readings.items():
            if name in self.plot_data:
                self.plot_data[name]['time'].append(current_time)
                self.plot_data[name]['temp'].append(temp)
                
                # Update line data
                self.plot_lines[name].set_data(self.plot_data[name]['time'], self.plot_data[name]['temp'])
                
                # Update label with current value
                self.plot_lines[name].set_label(f"{self._get_plot_map()[name]['label']}: {temp:.2f} °C")
                self.plot_axes[name].legend(loc='upper left')
                
                # Rescale axes
                self.plot_axes[name].relim()
                self.plot_axes[name].autoscale_view()
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def run(self):
        """Main application loop for monitoring, logging, and plotting."""
        initial_time = time.time()
        last_log_time = last_cmd_time = initial_time
        
        header = "\t".join(["Timestamp"] + list(self._get_plot_map().keys()))
        logging.info(header)

        try:
            while self.is_running:
                current_time = time.time() - initial_time
                
                # Read data from sensors
                readings = self._read_sensors()
                
                # Log data periodically
                if (time.time() - last_log_time) >= self.config['temperature_management']['logging']['log_interval_sec']:
                    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t" + "\t".join(f"{readings.get(k, 'NaN'):.2f}" for k in self._get_plot_map())
                    logging.info(log_entry)
                    last_log_time = time.time()
                
                # Update the real-time plot
                self._update_plot(current_time, readings)
                plt.pause(self.config['temperature_management']['plotting']['update_interval_sec'])

                # parsing potential temperature updates from the runner, only if a command queue was initialized. 
                if self.command_queue != None and (time.time() - last_cmd_time) >= self.config['temperature_management']['chiller']['update_frequency']:
                    try:
                        last_cmd_time = time.time()
                        new_command = self.command_queue.get_nowait() #always use non blocking
                        self.temperature_setpoint = new_command
                        self.devices['chiller'].set_point(self.temperature_setpoint) #this ensures that we only send setpoints when we receive cmds
                        print(f"ThermalManager received command: {new_command}")

                        if new_command is None: # A way to signal shutdown
                            self.is_running = False
                            continue
                    except queue.Empty: #empty queue = no new commands sent
                        pass 
                
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt detected. Shutting down.")
        finally:
            self.close()


    def close(self):
        """Gracefully closes all hardware connections."""
        self.is_running = False
        for device in self.devices.values():
            if device:
                device.close()
        plt.ioff()
        logging.info("All connections closed. Application terminated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Temperature Monitoring Tool.")
    parser.add_argument(
        '--config',
        type=str,
        required=True,
        help="Path to the configuration YAML file."
    )
    args = parser.parse_args()
    
    monitor = ThermalManager(config_path=args.config, command_queue= None)
    monitor.run()