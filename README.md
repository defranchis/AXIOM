# Overview
Python framework for HGC sensor testing. Software is based on SPIDR python framework for Timepix3. 


# Install
Just download the folder.

# Requirements

* matplotlib
* numpy
* pyvisa (if gpib communciation is used)
* pyserial (if serial communication is used)
* VISA drivers (if gpib communciation is used)
* FTDI drivers (if serial communciation is used)


# Instructions
Use 'main.py' to execute measurements. Syntax is 'python main.py [identifier] [test]'.

Examples

* python main.py test test00_debugging
* python main.py cell52 test04_single_iv
* python main.py sensor1008  test03_scan_cv


Notes

* Folder devices holds all communication drivers
* Folder measurements holds all measurement scripts
* Folder analysis holds the visualisation


# To Do

- [ ] Automatic recognition of tests
- [ ] Add GUI

