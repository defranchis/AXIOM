# ============================================================================
# File: test07_longterm_cv.py
# ------------------------------
# 
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       while measurement time is not reached:
#           measure voltage, time, z, phi
#           calculate cp, cs
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
from devices import hp4980 # lcr meter
from utils import lcr_series_equ, lcr_parallel_equ


class test09_interpad_cap(measurement):
    """Multiple measurements of IV over a longer period."""
    
    def initialise(self):
        self.logging.info("\t")
        self.logging.info("")
        self.logging.info("------------------------------------------")
        self.logging.info("Single CV Measurement")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of CV for a single cell.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.lcr_meter_address = 17     # gpib address of the lcr meter
        
        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 500              # compliance in [V]
        self.volt_list = np.loadtxt('config/voltagesCV.txt', dtype=int)
        # self.volt_list = [0, -1, -3, -5, -7,-9,-11,-13,-15,-17,-19,-21,-23,-25,-27,-30]

        self.lcr_vol = 0.5              # ac voltage amplitude in [mV]
        self.lcr_freq = 50000           # ac voltage frequency in [kHz]
    
        self.delay_vol = 20             # delay between setting voltage and executing measurement in [s]
        
        

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

        ## Set up lcr meter
        lcr_meter = hp4980(self.lcr_meter_address)
        lcr_meter.reset()
        lcr_meter.set_voltage(self.lcr_vol)
        lcr_meter.set_frequency(self.lcr_freq)
        lcr_meter.set_mode('RX')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        lcr_vol = float(lcr_meter.check_voltage())
        lcr_freq = float(lcr_meter.check_frequency())

        ## Print info
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power Supply current limit:      %8.2E A" % float(lim_cur))
        self.logging.info("LCR measurement voltage:         %8.2E V" % lcr_vol)
        self.logging.info("LCR measurement frequency:       %8.2E Hz" % lcr_freq)
        self.logging.info("Voltage Delay:                   %8.2f s" % self.delay_vol)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tChannel [-]\tR [kOhm]\tX [kOhm]\tCs [pF]\tCp [pF]\tRs [Ohm]\tRp [Ohm]\tTotal Current [A]")
        self.logging.info("\t--------------------------------------------------------------------------")


        ## Prepare
        out = []
        hd = ' Single CV\n' \
           + ' Measurement Settings:\n' \
           + ' Power supply voltage limit:      %8.2E V\n' % lim_vol \
           + ' Power supply current limit:      %8.2E A\n' % lim_cur \
           + ' LCR measurement voltage:         %8.2E V\n' % lcr_vol \
           + ' LCR measurement frequency:       %8.0E Hz\n' % lcr_freq \
           + ' Voltage Delay:                   %8.2f s\n\n' % self.delay_vol \
           + ' Nominal Voltage [V]\t Measured Voltage [V]\tChannel [-]\tR [kOhm]\tR_Err [kOhm]\tX [kOhm]\tX_Err [kOhm]\tCs [pF]\tCp [pF]\tRs [Ohm]\tRp [Ohm]\tTotal Current [A]\n'

        ## Loop over voltages
        try:
            j = 0
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)
                time.sleep(0.001)
    
                cur_tot = pow_supply.read_current()
                vol = pow_supply.read_voltage()
    
                tmp1 = []
                tmp2 = []
                for i in range(5):
                    r, x = lcr_meter.execute_measurement()
                    tmp1.append(r)
                    tmp2.append(x)
                r = np.mean(np.array(tmp1))
                x = np.mean(np.array(tmp2))
                r_err = np.std(np.array(tmp1))
                x_err = np.std(np.array(tmp2))
                
                time.sleep(0.001)            
            
                z = np.sqrt(r**2 + x**2)
                phi = np.arctan(x/r)
                r_s, c_s, l_s, D = lcr_series_equ(self.lcr_freq, z, phi)
                r_p, c_p, l_p, D = lcr_parallel_equ(self.lcr_freq, z, phi)
            
                out.append([v, vol, j, r, r_err, x, x_err, c_s, c_p, r_s, r_p, cur_tot])
                self.logging.info("\t%.2f \t%4d\t%.3f \t%.3f \t%.3E \t%.3E \t%.3E \t%.3E \t%.2E" % (vol, j, r/1000., x/1000., c_s*10**(12), c_p*10**(12), r_s, r_p, cur_tot))

        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")


        ## Close connections
        pow_supply.ramp_voltage(0)
        time.sleep(15)
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("")
        self.save_list(out, "cv.dat", fmt="%.5E", header=hd)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 7], np.array(out)[:, 7] * 0.01, \
                         'Bias Voltage [V]', 'Parallel Capacitance [F]',  'CV ' + self.id, fn="cv_%s.png" % self.id)
        self.print_graph(np.array(out)[2:, 1], np.array(out)[2:, 7]**(-2), 0, \
                         'Bias Voltage [V]', '1/C^2 [1/F^2]',  '1/C2 ' + self.id, fn="1c2v_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 9], np.array(out)[:, 9]*0.01, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_%s.png" % self.id)
        self.logging.info("")
    
    
    def finalise(self):
        self._finalise()