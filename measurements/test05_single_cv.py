# ============================================================================
# File: test05_singe_cv.py
# ------------------------------
# 
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       measure voltage, z, phi
#       calculate cp, cs
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
from utils import lcr_series_equ, lcr_parallel_equ, lcr_error_cp


class test05_single_cv(measurement):
    """Measurement of C-V curve for a single cell on the wafer."""
    
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
        self.volt_list = [0, 1, 5, 10, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350]

        self.lcr_vol = 0.5              # ac voltage amplitude in [mV]
        self.lcr_freq = 50000           # ac voltage frequency in [kHz]
    
        self.delay_vol = 10             # delay between setting voltage and executing measurement in [s]
        
        

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
        lcr_meter.set_mode('ZTR')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        lcr_vol = lcr_meter.check_voltage()
        lcr_freq = lcr_meter.check_frequency()

        ## Print info
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power Supply current limit:      %8.2E A" % float(lim_cur))
        self.logging.info("LCR measurement voltage:         %8.2E V" % lcr_vol)
        self.logging.info("LCR measurement frequency:       %8.2E Hz" % lcr_freq)
        self.logging.info("Voltage Delay:                   %8.2f s" % self.delay_vol)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tCser [F]\tCpar [F]\tCpar_err [F]\tTotal current [A]")
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
           + ' Volt [V]\tZ [Ohm]\tPhi [rad]\tCs [F]\tCp [F]\tCp_err [F]\tTotal Current[A]'

        ## Loop over voltages
        try:
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)
                time.sleep(0.001)
    
                cur_tot = pow_supply.read_current()
                vol = pow_supply.read_voltage()
    
                tmp1 = []
                tmp2 = []
                for i in range(5):
                    z, phi = lcr_meter.execute_measurement()
                    tmp1.append(z)
                    tmp2.append(phi)
                z = np.mean(np.array(tmp1))
                phi = np.mean(np.array(tmp2))
                z_err = np.std(np.array(tmp1))
                phi_err = np.std(np.array(tmp2))
                
                time.sleep(0.001)            
    
                rs, cs, ls, D = lcr_series_equ(self.lcr_freq, z, phi)
                rp, cp, lp, D = lcr_parallel_equ(self.lcr_freq, z, phi)
                cp_err = lcr_error_cp(self.lcr_freq, z, z_err, phi, phi_err)
        
                out.append([vol, z, phi, cs, cp, cp_err, cur_tot])
                self.logging.info("\t%.2E \t%.3E \t%.3E \t%.3E \t%.2E" % (vol, cs, cp, cp_err, cur_tot))
  
        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")


        ## Close connections
        pow_supply.ramp_voltage(0)
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("")
        self.save_list(out, "cv.dat", fmt="%.5E", header=hd)
        self.print_graph(np.array(out)[:, 0], np.array(out)[:, 4], np.array(out)[:, 5], \
                         'Bias Voltage [V]', 'Parallel Capacitance [F]',  'CV ' + self.id, fn="cv_%s.png" % self.id)
        self.print_graph(np.array(out)[2:, 0], np.array(out)[2:, 4]**(-2), 2 * np.array(out)[2:, 5] * np.array(out)[2:, 4]**(-3), \
                         'Bias Voltage [V]', '1/C^2 [1/F^2]',  '1/C2 ' + self.id, fn="1c2v_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 0], np.array(out)[:, 6], np.array(out)[:, 6]*0.0001, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_%s.png" % self.id)
        self.logging.info("")
    

    def finalise(self):
        self._finalise()


