# Overview
Python framework for ARRAY wafer probing system. Software is loosely based on SPIDR python framework for Timepix3.


# Install
Just download the folder.

# Requirements
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
Use 'main.py' to execute measurements. Syntax is 'python main.py [identifier] [test]'.

Examples

* python main.py test test00_debugging
* python main.py sensor1008 test03_scan_cv


Notes

* Folder devices holds all communication drivers
* Folder measurements holds all measurement scripts


# To Do

- [ ] Add GUI
- [ ] Add ethernet device
- [ ] Add USB device
