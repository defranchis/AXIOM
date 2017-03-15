# ============================================================================
# File: test06_longterm_iv.py
# ------------------------------
# 
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       while measurement time is not reached:
#           measure voltage, time, current, total current
#   finish
#
# Status:
#   works well
#
# ============================================================================

import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import ke2001 # volt meter


class test06_longterm_iv(measurement):
    """Multiple measurements of IV over a longer period."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("IV Longterm")
        self.logging.info("------------------------------------------")
        self.logging.info("Multiple measurements of IV over a longer period.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.volt_meter_address = 16    # gpib address of the multimeter
        
        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 500              # compliance in [V]
        self.volt_list = [150]          # list of bias voltage in [V]
        
        self.delay_msr = 1              # delay between two consecutive measurements in [s]
        self.duration_msr = 100         # total measurement time in [s]
        
        

    def execute(self):
        
        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.reset()
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_voltage(0)
        pow_supply.set_terminal('rear')
        pow_supply.set_output_on()

        ## Set up volt meter
        volt_meter = ke2001(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.setup_ammeter(nplc=10, dig=9)

        ## Print info
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %.2f V" % self.lim_vol)
        self.logging.info("Power supply current limit:      %.6f A" % self.lim_cur)
        self.logging.info("Volt meter voltage limit:        %.2f V" % self.lim_vol)
        self.logging.info("Volt meter current limit:        %.6f A" % self.lim_cur)
        self.logging.info("Measurement Delay:               %.2f s" % self.delay_msr)
        self.logging.info("Measurement Time:                %.0f s" % self.duration_msr)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tTime [s]\tCurrent [A]\tTotal current [A]")
        self.logging.info("\t----------------------------------------------------------------")
        
        ## Prepare
        out = []
        t = 0
        err = 3*10**(-10)

        ## Loop over voltages
        for v in self.volt_list:
            pow_supply.ramp_voltage(v)
            time.sleep(self.delay_msr)

            vol = pow_supply.read_voltage()
            cur_tot = pow_supply.read_current()
            
            t0 = time.time()
            while t < self.duration_msr:
                t = time.time() - t0
                
                vol = pow_supply.read_voltage()
                cur_tot = pow_supply.read_current()

                tmp = []
                for i in range(5):
                    tmp.append(volt_meter.read_current())
                cur = np.mean(np.array(tmp))
                

                out.append([vol, t, cur, cur_tot])
                time.sleep(self.delay_msr)

                self.logging.info("\t%.2E \t%.2E \t%.4E \t%.4E" % (vol, t, cur, cur_tot))
            
        ## Close connections
        pow_supply.ramp_voltage(0)
        volt_meter.reset()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\t")
        self.save_list(out, "iv_long.dat", fmt="%.5E", header=' volt [V]\ttime [s]\tcurrent[A]\ttotal current[A]')
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 2], err, 'Time [s]', 'Leakage Current [A]', 
                         'Longterm IV ' + self.id, fn="iv_long_%s.png" % self.id)
        self.logging.info("\t")

    
    def finalise(self):
        self._finalise()



