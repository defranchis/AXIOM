# Silicon Dioxide Measurement Framework

## Overview

This repository contains a Python-based software framework for characterizing the electrical properties of silicon dioxide in silicon sensors, specifically for the CMS High Granularity Calorimeter (HGCAL) project. The system automates **Current-Voltage (IV)** and **Capacitance-Voltage (CV)** measurements to study leakage currents, breakdown behavior, doping concentrations, and depletion voltages.

The primary goal is to understand how these properties change due to **radiation damage** and subsequent **annealing**, which is crucial for calibrating the HGCAL sensors. The framework is designed for flexibility, allowing for standalone measurements or integrated campaigns with auxiliary hardware like the **Obelix X-ray irradiator** and a **chiller** for temperature control.

The architecture is loosely based on the AXIOM/ARRAY repositories, ensuring some backward compatibility, but has been significantly refactored to be more modular, robust, and maintainable.

-----

## Key Features

This framework was redesigned from the ground up to be stable and easy to extend. Key features include:

  * **Centralized Configuration**: All aspects of an experiment—from hardware addresses to measurement parameters and dose lists—are defined in a single, human-readable YAML file.
  * **Dynamic Device Initialization**: Devices specified in the config (e.g., `sourcemeter_1`, `lcrmeter`) are automatically initialized and made available to the measurement class. This allows for easy hardware swapping by simply changing the model and address in the config, as long as the device classes share a common interface.
  * **Automated Measurement Sequences**:
      * **Irradiation Loops**: The runner can execute a full irradiation campaign, applying doses from a `doselist` and running measurements after each step. It can also cleanly resume an interrupted campaign by checking the `preexisting_dose`.
      * **Annealing Loops**: The system can perform long-term annealing studies by running measurements at set time intervals while managing the sample temperature.
  * **Intelligent Measurement Control**:
      * **Dynamic Voltage Ranges**: For irradiation studies, the system can automatically adjust the voltage sweep range for the current radiation dose. It does this by linearly interpolating from a set of empirical data points, ensuring efficient and relevant measurements as the sample's properties change.
      * **Adaptive Plateau Detection**: During CV scans, the system actively searches for the capacitance plateau. Once detected, it can terminate the scan early based on the `plateau_extention` parameter, significantly speeding up measurements without losing critical data.
  * **Robust and Safe Operation**:
      * The runner includes robust exception handling to ensure that critical hardware, like the X-ray irradiator, is safely shut down in case of an error.
      * To prevent accidental re-irradiation, the system can check for existing log files if a run is started with `preexisting_dose: 0`.
  * **Integrated Thermal Management**: Temperature control is handled by a separate, parallel process (`multiprocessing.Process`) that communicates with the main runner. This ensures the sample temperature is consistently managed without blocking measurement execution.

-----

## System Architecture

The software is built on a simple, three-layer architecture designed for modularity.

1.  **Runner (`runner.py`)**: The single entry point for all operations. It parses the user-provided configuration file, initializes the appropriate measurement class, and orchestrates the high-level experimental flow (e.g., an irradiation loop, an annealing loop, or a single measurement).

2.  **Configuration File (`.yaml`)**: Defines the entire experiment. This includes the sample ID, the list of hardware `devices` and their connection details, `measurements` parameters (like voltage ranges and the `testset` to execute), `irradiation` dose steps, and `temperature_management` settings.

3.  **Measurement Classes (e.g., `gcdmos.py`)**: Contains the high-level logic for measuring a specific type of sample. It interprets the measurement parameters from the config, controls the hardware via the device classes, and executes the scan sequences (e.g., `doCVScan`, `doIVScan`).

4.  **Device Classes**: These are the low-level drivers that communicate directly with the hardware instruments (e.g., Keithley sourcemeters, Agilent LCR meters). They provide a consistent programming interface, allowing measurement classes to function without knowing the specific model of the instrument being used.

-----

## Usage

All interaction with the setup is handled via the main runner. An experiment is launched by invoking `runner.py` from the command line and providing the path to a configuration file.

```bash
python runner.py /path/to/your/config.yaml
```

Example configuration files can be found in the `config/` directory.

-----

## Configuration

The YAML configuration file is the heart of the experiment. Its main sections are:

  * **`devices`**: Define all hardware to be used. The name given to each device (e.g., `sourcemeter_1`) is how it will be accessed in the measurement class (`self.sourcemeter_1`). If a device is listed here, the runner will attempt to initialize it. If you are not using a device (like the `switch`), comment it out to prevent initialization errors.
  * **`measurements`**: Specify the parameters for the scans.
      * `testset`: A list determining which measurements are executed (e.g., `[moshalf, mos2000, gcd]`).
      * `dynamic_voltage_range`: Enable and configure the automatic adjustment of voltage ranges based on dose.
      * `CV` / `IV`: Set the static voltage ranges, sample sizes, delays, and other specific parameters for each measurement type.
  * **`irradiation`**: Configure the irradiation campaign.
      * `doselist`: A list of target cumulative doses in kGy.
      * `dose_rate`, `voltage`, `current`: Parameters for the X-ray source.
  * **`temperature_management`**: Enable and configure the chiller and temperature logging.

-----

## Extending the System

The modular design makes the framework easy to extend.

### Adding a New Configuration Parameter

1.  Add the new parameter to your YAML configuration file in the appropriate section.
2.  Access it within your measurement class via the `self.config` dictionary (e.g., `self.config['measurements']['CV']['my_new_parameter']`).
3.  **(Optional but Recommended)**: If the parameter is a permanent addition, add it to the corresponding validation schema in the `config/schemas/` directory. This ensures the config validator will check for its presence and correct type.

### Adding a New Device

1.  Create a new device class that implements the necessary communication functions (e.g., `set_voltage`, `read_current`).
2.  Ensure the functions you intend to use have the same name and behavior as in other device classes of the same type (e.g., all sourcemeter classes should have a `ramp_voltage()` method).
3.  Update the `model` in your config file to the name of your new device class. The dynamic initialization will handle the rest.