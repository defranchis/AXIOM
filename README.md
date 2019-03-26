# Overview
Python framework for ARRAY wafer probing system. It consists of a text-based 
user interface and a set of standard measurements for IV and CV measurements.
Drivers for a few common measurement instruments are provided. 
The framework is loosely based on SPIDR python framework for Timepix3.


# Install
Just download the folder.


# Dependencies
General
* matplotlib
* numpy

For serial communication with ARRAY
* pyserial
* FTDI drivers (https://www.ftdichip.com/FTDrivers.htm)

If GPIB communication is to be used
* pyvisa
* VISA drivers


# Instructions
Use 'main.py' to execute measurements. Syntax is 'python main.py [identifier] [measurement]'.

* [identifier] - Name of the folder in 'logs' where results should be stored.
* [measurement] - Measurement script to be executed.

Examples

* python main.py test test00_debugging
* python main.py sensor1008 test03_scan_cv


Notes

* Folder devices holds all communication drivers
* Folder measurements holds all measurement scripts
* The main switch card library is in devices/switchcard.py


# Development

To add additional measurements, add or modify a file in the 'measurements'.
In case of a new class, make sure to register it in 'measurements/\_\_init__.py'.

Some things to look out for:
* Before changing the settings in any external instruments (e.g. bias voltage), all channels should shorted to GND. This is a safety procedure as some instruments tend to protect their input via a high impedance shunt to ground. In case of large leakage currents, this could harm the switch card. When switching channels on the switch card, this is done internally. 


# To Do

- [ ] Add GUI
- [ ] Add ethernet device
- [ ] Add USB device
