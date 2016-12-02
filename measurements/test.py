# ============================================================================
# File: test.py
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
from devices import ke2450 # volt meter
from devices import hp4980 # lcr meter


class test(measurement):
    """A test on communication and functionality."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("Test")
        self.logging.info("------------------------------------------")
        self.logging.info("A test on communication and functionality.")
        self.logging.info("\n")
        
        self._initialise()
        self.pow_supply_address = 24
        self.volt_meter_address = 17
        self.lcr_meter_address = 18
        self.switch_address = 21
        
        self.lim_cur = 0.0001
        self.lim_vol = 100
        self.cell_list = [1, 2, 3]
        self.volt_list = [1, 5, 10]
        
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
        pow_supply.set_voltage(0)
        pow_supply.set_output_on()

        ## Set up volt meter
        volt_meter = ke2450(self.volt_meter_address)
        volt_meter.set_source('voltage')
        volt_meter.set_sense('current')
        volt_meter.set_voltage_limit(self.lim_vol)
        volt_meter.set_current_limit(self.lim_cur)
        volt_meter.set_voltage(0)
        volt_meter.set_output_on()

        for v in self.volt_list:
            pow_supply.set_voltage(v)
            vol = pow_supply.read_voltage()
            cur = pow_supply.read_voltage()
        
            time.sleep(0.5)
            self.logging.info("vol %d, cur %d" % (vol, cur))

        ## Close connections
        volt_meter.set_output_off()
        volt_meter.reset()
        pow_supply.set_output_off()
        pow_supply.reset()
    
    
    def finalise(self):
        self._finalise()