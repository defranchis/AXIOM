# Overview

Python framework for HGC sensor testing. Software is based on SPIDR python framework for Timepix3. 


# Install
Just download the folder.

# Requirements

matplotlib

numpy

pyvisa (if gpib communciation is used)

pyserial (if serial communication is used)

VISA drivers (if gpib communciation is used)

FTDI drivers (if serial communciation is used)


# Instructions
Use 'main.py' to execute measurements. Syntax is 'python main.py [test] [identifier]'.


Examples
-- python main.py test04_single_iv Cell52

-- python main.py test03_scan_cv Sensor1002

Notes
-- Folder devices holds all communication drivers

-- Folder measurements holds all measurement scripts

-- Folder analysis holds the visualisation


# To Do

Add GUI

