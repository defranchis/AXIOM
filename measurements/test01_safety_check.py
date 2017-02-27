# ============================================================================
# File: test01_safety_check.py
# ------------------------------
# 
# Notes:
#
# Layout:
#   configure and prepare
#   measure leakage current of all cells at 10V
#   warn if any is too high
#
# Status:
#   under construction
#
# ============================================================================

import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import ke2001 # volt meter


class test01_safety_check(measurement):
    """Performs a scan at 10V to check for high currents after alignment."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("Safety Check")
        self.logging.info("------------------------------------------")
        self.logging.info("Performs a scan at 10V to check for high currents after alignment.")
        self.logging.info("\n")
        
        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.volt_meter_address = 18    # gpib address of the multi meter
        
        self.lim_cur = 0.0001           # compliance in [A]
        self.lim_vol = 100              # compliance in [V]

        self.cell_list = [1]            # list of cells
        
        self.delay_vol = 2              # delay between setting voltage and executing measurement in [s]
        self.delay_cell = 0.4           # delay between switching cell and executing measurement in [s]
        
        self.logging.info("\n")
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %.2f V" % self.lim_vol)
        self.logging.info("Power supply current limit:      %.6f A" % self.lim_cur)
        self.logging.info("Volt meter voltage limit:        %.2f V" % self.lim_vol)
        self.logging.info("Volt meter current limit:        %.6f A" % self.lim_cur)
        self.logging.info("Voltage Delay:                   %.2f s" % self.delay_vol)
        self.logging.info("\n")
        
        

    def execute(self):
        
        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.reset()
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_voltage(0)
        pow_supply.set_output_on()

        ## Set up volt meter
        volt_meter = ke2001(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.setup_ammeter(nplc=10, dig=9)

        ## Set up lcr meter

        ## Set up switch
        # Set up switch

        v = 10
        pow_supply.ramp_voltage(v)
        time.sleep(delay_vol)

        cur_tot = pow_supply.read_current() 
        
        total_current_notice = 1.0 * 10**(-7)
        total_current_warning = 5.0 * 10**(-7)

        if cur_tot < total_current_notice:
            self.logging.info("Total current: %e" % cur_tot)
        elif cur > single_channel_notice and cur < single_channel_warning:
             self.logging.warning("Total current: %e" % cur_tot)
        else:
            self.logging.critical("Total current: %e" % cur_tot)


        for c in self.cell_list:
            # Check all channels close
            # Open channel c
            time.sleep(delay_ch)

            cur = volt_meter.read_current()

            single_channel_notice = 1.0 * 10**(-9)
            single_channel_warning = 5.0 * 10**(-9)
            if cur < single_channel_notice:
                self.logging.info("cell nr.:%d, vol %d, cur %e" % (c, v, cur))
            elif cur > single_channel_notice and cur < single_channel_warning:
                self.logging.warning("cell nr.:%d, vol %d, cur %e" % (c, v, cur))
            else:
                self.logging.critical("cell nr.:%d, vol %d, cur %e" % (c, v, cur))

            # Close all channels
            time.sleep(0.01)
                

        ## Close connections
        pow_supply.set_output_off()
        pow_supply.reset()
        volt_meter.set_output_off()
        volt_meter.reset()
    

    def finalise(self):
        self._finalise()


