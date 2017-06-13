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
from devices import ke6487 # volt meter
from devices import switchcard # switch


class test08_interpad_res(measurement):
    """Multiple measurements of IV over a longer period."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("IV Longterm")
        self.logging.info("------------------------------------------")
        self.logging.info("Multiple measurements of IV over a longer period.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.volt_meter_address = 23    # gpib address of the multimeter
        self.switch_address = 'COM3'    # serial port of switch card
        
        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 500              # compliance in [V]
        
        self.volt_list = [0,-10,-20]

        self.delay_vol = 5              # delay between setting voltage and executing measurement in [s]
        
        

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
        volt_meter = ke6487(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.setup_ammeter()
        volt_meter.set_nplc(2)

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()

        ## Print Info
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power Supply current limit:      %8.2E A" % lim_cur)
        self.logging.info("Voltage Delay:                   %8.2f s" % self.delay_vol)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tCurrent Mean[A]\tCurrent Error[A]\tTotal current [A]")
        self.logging.info("\t-----------------------------------------------------------------------")

        ## Prepare
        out = []
        hd = ' Single IV\n' \
           + ' Measurement Settings:\n' \
           + ' Power supply voltage limit:      %8.2E V\n' % lim_vol \
           + ' Power supply current limit:      %8.2E A\n' % lim_cur \
           + ' Voltage Delay:                   %8.2f s\n\n' % self.delay_vol \
           + ' Volt [V]\tCurrent Mean [A]\tCurrent Error [A]\tTotal Current[A]\t'

        ## Loop over voltages
        try:
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)
                time.sleep(0.001)
        
                cur_tot = pow_supply.read_current()
                vol = pow_supply.read_voltage()
                
                tmp = []
                for i in range(5):
                    tmp.append(volt_meter.read_current())
                cur = np.mean(np.array(tmp))
                err = np.std(np.array(tmp))
                
                time.sleep(0.001)
        
                out.append([vol, cur, err, cur_tot])
                self.logging.info("\t%.2E \t%.3E \t%.3E \t%.2E" % (vol, cur, err, cur_tot))
  
        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

        ## Close connections
        pow_supply.ramp_voltage(0)
        volt_meter.reset()
        time.sleep(15)
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header=hd)
        self.print_graph(np.array(out)[:, 0], np.array(out)[:, 1], np.array(out)[:, 2], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_%s.png" % self.id)
        self.print_graph(np.array([val for val in out if (val[0] < 251 and val[0]>-0.1)])[:, 0], \
                         np.array([val for val in out if (val[0] < 251 and val[0]>-0.1)])[:, 1], \
                         np.array([val for val in out if (val[0] < 251 and val[0]>-0.1)])[:, 2], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_zoom_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 0], np.array(out)[:, 3], np.array(out)[:, 3]*0.0001, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_%s.png" % self.id)
        self.logging.info("\n")


    def finalise(self):
        self._finalise()


