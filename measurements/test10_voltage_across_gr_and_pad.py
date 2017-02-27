# ============================================================================
# File: test10_voltage_across_gr_and_pad.py
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
from devices import ke2410 # power supply 1
from devices import ke2450 # power supply 2


class test10_voltage_across_gr_and_pad(measurement):
    """Measurement of I-V curve for a single cell on the wafer."""
    
    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Voltage across GR and Pad")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement behaviour if there is a voltage difference between Pad and GR.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply1_address = 24
        self.pow_supply2_address = 18
        
        self.lim_cur = 0.0005
        self.lim_vol = 100
        self.volt_list1 = [1, 5, 10, 25, 50]
        self.volt_list2 = [1, 2, 3, 5]
        
        self.delay_vol = 2
        
        

    def execute(self):
        
        ## Set up power supply
        pow_supply1 = ke2410(self.pow_supply1_address)
        pow_supply1.reset()
        pow_supply1.set_source('voltage')
        pow_supply1.set_sense('current')
        pow_supply1.set_current_limit(self.lim_cur)
        pow_supply1.set_voltage(0)
        pow_supply1.set_terminal('rear')
        pow_supply1.set_output_on()

        ## Set up volt meter
        pow_supply2 = ke2450(self.pow_supply2_address)
        pow_supply2.reset()
        pow_supply2.set_source('current')
        pow_supply2.set_sense('voltage')
        #pow_supply2.set_current_limit(2)
        pow_supply2.set_voltage(0)
        pow_supply2.set_output_on()

        ## Print Info
        self.logging.info("Settings:")
        self.logging.info("Power supply 1 voltage limit:      %8.2E V" % self.lim_vol)
        self.logging.info("Power supply 1 current limit:      %8.2E A" % self.lim_cur)
        self.logging.info("Power supply 2 voltage limit:      %8.2E V" % self.lim_vol)
        self.logging.info("Power supply 2 current limit:      %8.2E A" % self.lim_cur)
        self.logging.info("Voltage Delay:                     %8.2E s" % self.delay_vol)
        self.logging.info("\t")

        self.logging.info("\tVoltage 1 [V]\tVoltage 2 [V]\tTotal current [A]")
        self.logging.info("\t--------------------------------------------------")

        ## Prepare
        out = []

        ## Loop over voltages
        for v in self.bias_list:
            pow_supply1.ramp_voltage(v)
            for v2 in self.volt_list:
                pow_supply2.ramp_voltage(v)
                time.sleep(self.delay_vol)

            #    vol1 = pow_supply1.read_voltage()
            #    vol2 = pow_supply1.read_voltage()
            #    cur = pow_supply2.read_current()
            #    cur_tot = pow_supply1.read_current()
    
            #    out.append([vol, cur, cur_tot])
            #    self.logging.info("\t%.2E \t%.2E \t%.2E" % (vol, cur, cur_tot))

            time.sleep(self.delay_vol)
            time.sleep(0.001)

            vol1 = pow_supply1.read_voltage()
            cur_tot = pow_supply1.read_current()
            
            tmp = []
            for i in range(5):
                tmp.append(pow_supply2.read_voltage())
            vol2 = np.mean(np.array(tmp))
            
            time.sleep(0.001)

            out.append([vol, cur, cur_tot])
            self.logging.info("\t%.2E \t%.3E \t%.2E" % (vol, cur, cur_tot))


        ## Close connections
        pow_supply.ramp_voltage(0)
        volt_meter.set_output_off()
        volt_meter.reset()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header=' volt [V]\tcurrent[A]\ttotal current[A]\t')
        self.print_graph(np.array(out)[:, 0], np.array(out)[:, 1], 'Bias Voltage [V]', 'Leakage Current [A]', fn="iv.png")
        self.logging.info("\n")

    
    
    def finalise(self):
        self._finalise()

