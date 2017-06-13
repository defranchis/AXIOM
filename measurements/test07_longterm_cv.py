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
from devices import switchcard # switch
from utils import lcr_series_equ, lcr_parallel_equ


class test07_longterm_cv(measurement):
    """Multiple measurements of IV over a longer period."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("CV Longterm")
        self.logging.info("------------------------------------------")
        self.logging.info("Multiple measurements of CV over a longer period.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.lcr_meter_address = 17     # gpib address of the lcr meter   
        self.switch_address = 'COM3'    # serial port of switch card  
                    
        self.lim_cur = 0.0005           # compliance in [A]      
        self.lim_vol = 500              # compliance in [V]
        self.volt_list = [-150]          # list of bias voltage in [V]  
        
        self.delay_msr = 1              # delay between two consecutive measurements in [s]
        self.duration_msr = 100         # total measurement time in [s]
        
        self.lcr_vol = 0.5              # ac voltage amplitude in [mV]
        self.lcr_freq = 50000           # ac voltage frequency in [kHz]
        


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

        # Set up switch
        # switch = switchcard(self.switch_address)
        # switch.reboot()
        # switch.set_measurement_type('CV')
        # switch.set_display_mode('ON')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        lcr_vol = float(lcr_meter.check_voltage())
        lcr_freq = float(lcr_meter.check_frequency())
        # temp_pc = switch.get_probecard_temperature()
        # temp_sc = switch.get_matrix_temperature()
        # # humd_pc = switch.get_probecard_humidity()
        # # humd_sc = switch.get_matrix_humidity()
        # type_msr = switch.get_measurement_type()
        # type_disp = switch.get_display_mode()

        ## Print info
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power supply current limit:      %8.2E A" % lim_cur)
        self.logging.info("LCR measurement voltage:         %8.2E V" % lcr_vol)
        self.logging.info("LCR measurement frequency:       %8.2E Hz" % lcr_freq)
        # self.logging.info("Probecard temperature:           %8.1f C" % temp_pc)
        # self.logging.info("Switchcard temperature:          %8.1f C" % temp_sc)
        # self.logging.info("Probecard humidity:              %8.1f %" % humd_pc)
        # self.logging.info("Switchcard humidity:             %8.1f %" % humd_sc)
        # self.logging.info("Switchcard measurement setting:  %s" % type_msr)
        # self.logging.info("Switchcard display setting:      %s" % type_disp)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tTime [s]\tR [Ohm]\tX [Ohm]\tCapacitance [F]")
        self.logging.info("\t--------------------------------------------------")

        ## Prepare
        out = []
        hd = ' Scan CV\n' \
           + ' Measurement Settings:\n' \
           + ' Power supply voltage limit:      %8.2E V\n' % lim_vol \
           + ' Power supply current limit:      %8.2E A\n' % lim_cur \
           + ' LCR measurement voltage:         %8.2E V\n' % lcr_vol \
           + ' LCR measurement frequency:       %8.0E Hz\n' % lcr_freq \
           + ' Voltage [V]\tTime [s]\tR [Ohm]\tX [Ohm]\tCapacitance [F]\tTotal Current [A]\n'

        t = 0
        err = 10**(-14)

        ## Loop over voltages
        # switch.open_channel(0)
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
                r, x = lcr_meter.execute_measurement()

                cap = (-10**(12))/(2*np.pi*self.lcr_freq*x)
                
                out.append([vol, t, r, x, cap, cur_tot])
                time.sleep(self.delay_msr)

                self.logging.info("\t%.2E \t%.2E \t%.3E \t%.3E \t%.3E" % (vol, t, r, x, cap))


        ## Close connections
        pow_supply.ramp_voltage(0)
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("")
        self.save_list(out, "cv_long.dat", fmt="%.5E", header=' volt [V]\t time [s]\tz [Ohm]\tphi [rad]\tcs [F]\tcp [F]\ttotal current[A]')
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 4], err, 'Time [s]', 
                         'Capacitance [F]', 'Longerm CV ' + self.id, fn="cv_long_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 5], err, 'Time [s]', 
                         'Total Current [A]', 'Longerm CV ' + self.id, fn="cv_long_total_current_%s.png" % self.id)        
        self.logging.info("")


    
    def finalise(self):
        self._finalise()