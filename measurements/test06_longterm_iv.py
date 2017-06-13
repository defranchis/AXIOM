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
        self.volt_meter_address = 23    # gpib address of the multimeter
        self.switch_address = 'COM3'    # serial port of switch card
        
        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 500              # compliance in [V]
        self.volt_list = [-15]         # list of bias voltage in [V]
        
        self.delay_msr = 0.2              # delay between two consecutive measurements in [s]
        self.duration_msr = 20         # total measurement time in [s]
        
        

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
        volt_meter.set_nplc(1)

        # Set up switch
        # switch = switchcard(self.switch_address)
        # switch.reboot()
        # switch.set_measurement_type('IV')
        # switch.set_display_mode('ON')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        # temp_pc = switch.get_probecard_temperature()
        # temp_sc = switch.get_matrix_temperature()
        # humd_pc = switch.get_probecard_humidity()
        # humd_sc = switch.get_matrix_humidity()
        # type_msr = switch.get_measurement_type()
        # type_disp = switch.get_display_mode()


        ## Print info
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power supply current limit:      %8.2E A" % lim_cur)
        # self.logging.info("Probecard temperature:           %8.1f C" % temp_pc)
        # self.logging.info("Switchcard temperature:          %8.1f C" % temp_sc)
        # self.logging.info("Probecard humidity:              %s %" % humd_pc)
        # self.logging.info("Switchcard humidity:             %s %" % humd_sc)
        # self.logging.info("Switchcard measurement setting:  %s" % type_msr)
        # self.logging.info("Switchcard display setting:      %s" % type_disp)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tTime [s]\tCurrent [A]\tTotal current [A]")
        self.logging.info("\t----------------------------------------------------------------")
        
        ## Prepare
        out = []
        hd = ' Longterm CV\n' \
           + ' Measurement Settings:\n' \
           + ' Power supply voltage limit:      %8.2E V\n' % lim_vol \
           + ' Power supply current limit:      %8.2E A\n' % lim_cur \
           + ' Voltage [V]\tTime [s]\tCurrent [A]\tTotal current [A]\n'

        t = 0
        err = 3*10**(-10)

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

                tmp = []
                for i in range(5):
                    tmp.append(volt_meter.read_current())
                cur = np.mean(np.array(tmp))
                

                out.append([vol, t, cur, cur_tot])
                time.sleep(self.delay_msr)

                self.logging.info("\t%.2E \t%5.2f \t%.4E \t%.4E" % (vol, t, cur, cur_tot))
            
        ## Close connections
        pow_supply.ramp_voltage(0)
        volt_meter.reset()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\t")
        self.save_list(out, "iv_long.dat", fmt="%.5E", header=hd)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 2], err, 'Time [s]', 'Leakage Current [A]', 
                         'Longterm IV ' + self.id, fn="iv_long_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 3], err, 'Time [s]', 'Total Current [A]', 
                         'Longterm IV ' + self.id, fn="iv_long_totaL_current%s.png" % self.id)
        self.logging.info("\t")

    
    def finalise(self):
        self._finalise()



