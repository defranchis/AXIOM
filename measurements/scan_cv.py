import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import hp4284A # lcr meter
#from devices import ke3706 # switch


class scan_cv(measurement):
    """Measurement of C-V curves for individual cells across the wafer matrix."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("CV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of C-V curves for individual cells across the wafer matrix.")
        self.logging.info("\n")
        
        self._initialise()
        self._initialise()
        self.pow_supply_address = 24
        self.lcr_meter_address = 16
        self.switch_address = 10
        
        self.lim_cur = 0.0001
        self.lim_vol = 300
        self.cell_list = [0, 1, 2, 3]
        self.volt_list = [20, 50, 100, 200]

        self.lcr_vol = 500 # ac voltage amplitude in mV
        self.lcr_freq = 10 # ac voltage frequency in kHz
        self.cor_open = np.loadtxt('valuesOpen.txt') # open correction for lcr meter
        self.cor_short = np.loadtxt('valuesShort.txt') # short correction for lcr meter
        self.cor_load = np.loadtxt('valuesLoad.txt')
        
        self.logging.info("\n")
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %.2fV" % self.lim_vol)
        self.logging.info("Power Supply current limit:      %.6fA" % self.lim_cur)
        self.logging.info("LCR measurement voltage:         %.2fV" % self.lcr_vol)
        self.logging.info("LCR measurement frequency:       %.6fA" % self.lcr_freq)
        self.logging.info("\n")
        

    def execute(self):
        pass
    
    
    def finalise(self):
        self._finalise()