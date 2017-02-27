# ============================================================================
# File: test03_scan_cv.py
# ------------------------------
# 
# Notes:
#
# Layout:
#   configure and prepare
#
# Status:
#   in progress
#
# ============================================================================


import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import hp4980 # lcr meter
#from devices import ke3706 # switch



class test03_scan_cv(measurement):
    """Measurement of C-V curves for individual cells across the wafer matrix."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("CV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of C-V curves for individual cells across the wafer matrix.")
        self.logging.info("\n")
        
        self._initialise()
        self.pow_supply_address = 24
        self.volt_meter_address = 18
        self.switch_address = 21
        
        self.lim_cur = 0.0001
        self.lim_vol = 300
        self.cell_list = np.loadtxt('channelsCV.txt')
        self.volt_list = np.loadtxt('voltagesCV.txt')
        
        self.delay_vol = 10
        self.delay_ch = 0.4

        self.lcr_vol = 500 # ac voltage amplitude in mV
        self.lcr_freq = 10 # ac voltage frequency in kHz
        self.cor_open = np.loadtxt('valuesOpen.txt') # open correction for lcr meter
        self.cor_short = np.loadtxt('valuesShort.txt') # short correction for lcr meter
        self.cor_load = np.loadtxt('valuesLoad.txt') # load correction for lcr meter
        
        self.logging.info("\n")
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %.2fV" % self.lim_vol)
        self.logging.info("Power supply current limit:      %.6fA" % self.lim_cur)
        self.logging.info("LCR meter test voltage:          %.2fV" % self.test_vol)
        self.logging.info("LCR meter test frequency:        %.0fHz" % self.test_freq)
        self.logging.info("Voltage Delay:                   %.2fs" % self.delay_vol)
        self.logging.info("Channel Delay:                   %.2fs" % self.delay_ch)
        self.logging.info("\n")
        

    def execute(self):
        pass
    
    
    def finalise(self):
        self._finalise()