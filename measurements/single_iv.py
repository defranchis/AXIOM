# ============================================================================
# File: singe_iv.py
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
#from devices import ke2450 # volt meter


class iv_scan(measurement):
    """Measurement of I-V curve for a single cell on the wafer."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("IV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of IV for a single cell.")
        self.logging.info("\n")
        
        self._initialise()
        self.pow_supply_address = 24
        self.volt_meter_address = 16
        
        self.lim_cur = 0.0001
        self.lim_vol = 100
        self.volt_list = np.loadtxt('voltagesIV.txt')
        
        self.logging.info("\n")
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %.2fV" % self.lim_vol)
        self.logging.info("Power Supply current limit:      %.6fA" % self.lim_cur)
        self.logging.info("Volt Meter voltage limit:        %.2fV" % self.lim_vol)
        self.logging.info("Volt Meter current limit:        %.6fA" % self.lim_cur)
        self.logging.info("\n")
        
        

    def execute(self):
        
        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_voltage_limit(self.lim_vol)
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_output_on()

        ## Set up volt meter
        # Set up volt meter

        for v in self.volt_list:
            pow_supply.set_voltage(v)
            vol = pow_supply.read_voltage()
            cur = pow_supply.read_voltage()
        
            self.logging.info("vol %d, cur %d" % (vol, cur))

        ## Close connections
        pow_supply.set_output_off()
        pow_supply.reset()
    
    
    def finalise(self):
        self._finalise()