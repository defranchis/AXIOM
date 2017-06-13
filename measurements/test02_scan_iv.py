# ============================================================================
# File: test02_scan_iv.py
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
from devices import ke6487 # volt meter
from devices import switchcard # switch



class test02_scan_iv(measurement):
    """Measurement of I-V curves for individual cells across the wafer matrix."""
    
    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("IV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of I-V curves for individual cells across the wafer matrix.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.volt_meter_address = 23    # gpib address of the multi meter
        self.switch_address = 'COM3'    # serial port of switch card
        
        self.lim_cur = 0.0001           # compliance in [A]
        self.lim_vol = 100              # compliance in [V]

        self.cell_list = np.loadtxt('config/channels128_from_schematics_sorted.txt', dtype=int)
        self.volt_list = [-10]
        
        self.delay_vol = 5              # delay between setting voltage and executing measurement in [s]
        self.delay_ch = 0.1             # delay between setting channel and executing measurement in [s]



    def execute(self):
        
        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.reset()
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_voltage(0)
        pow_supply.set_nplc(2)
        pow_supply.set_terminal('rear')
        pow_supply.set_output_on()

        ## Set up volt meter
        volt_meter = ke6487(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.setup_ammeter()
        # volt_meter.set_auto_range(0)
        # volt_meter.set_range(2E-8)
        volt_meter.set_nplc(2)

        # Set up switch
        switch = switchcard(self.switch_address)
        switch.reboot()
        switch.set_measurement_type('IV')
        switch.set_display_mode('OFF')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        temp_pc = switch.get_probecard_temperature()
        temp_sc = switch.get_matrix_temperature()
        humd_pc = switch.get_probecard_humidity()
        humd_sc = switch.get_matrix_humidity()
        type_msr = switch.get_measurement_type()
        type_disp = switch.get_display_mode()

        ## Print Info
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power supply current limit:      %8.2E A" % lim_cur)
        self.logging.info("Voltage delay:                   %8.2f s" % self.delay_vol)
        self.logging.info("Channel delay:                   %8.2f s" % self.delay_ch)
        self.logging.info("Probecard temperature:           %8.1f C" % temp_pc)
        self.logging.info("Switchcard temperature:          %8.1f C" % temp_sc)
        # self.logging.info("Probecard humidity:              %s %" % humd_pc)
        # self.logging.info("Switchcard humidity:             %s %" % humd_sc)
        self.logging.info("Switchcard measurement setting:  %s" % type_msr)
        self.logging.info("Switchcard display setting:      %s" % type_disp)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tChannel [-]\tCurrent Mean [A]\tCurrent Err [A]\tTot. Current [A]\tTot. Current Err [A]")
        self.logging.info("\t--------------------------------------------------------------------------------------")

        ## Prepare
        out = []
        hd = ' Single IV\n' \
           + ' Measurement Settings:\n' \
           + ' Power supply voltage limit:      %8.2E V\n' % lim_vol \
           + ' Power supply current limit:      %8.2E A\n' % lim_cur \
           + ' Voltage Delay:                   %8.2f s\n' % self.delay_vol \
           + ' Channel Delay:                   %8.2f s\n' % self.delay_ch \
           + ' Probecard temperature:           %8.1f C\n' % temp_pc \
           + ' Switchcard temperature:          %8.1f C\n' % temp_sc \
           + ' Switchcard measurement setting:  %s\n' % type_msr \
           + ' Switchcard display setting:      %s\n\n\n' % type_disp \
           + ' Nominal Voltage [V]\t Measured Voltage [V]\tChannel [-]\tCurrent Mean [A]\tCurrent Error [A]\tTotal Current [A]\tTotal Current Error A]\n'

       ## Loop over voltages
        try:
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)
                time.sleep(0.001)

                j = 0
                for c in self.cell_list:

                    ## Through away first measurements after voltage change
                    if j == 0:
                        switch.open_channel(c)
                        for k in range(3):
                            volt_meter.read_current()
                            pow_supply.read_current()
                            time.sleep(0.001)

                    switch.open_channel(c)
                    time.sleep(self.delay_ch)
                    vol = pow_supply.read_voltage()
                
                    j += 1
                    tmp = []
                    tmp2 = []
                    for i in range(3):
                        tmp.append(volt_meter.read_current())
                        tmp2.append(pow_supply.read_current())
                    cur = np.mean(np.array(tmp))
                    err = np.std(np.array(tmp))
                    cur_tot = np.mean(np.array(tmp2))
                    cur_tot_err = np.std(np.array(tmp2))

                    time.sleep(0.001)
        
                    out.append([v, vol, j, cur, err, cur_tot, cur_tot_err])
                    self.logging.info("\t%.2E \t%4d \t%.3E \t%.3E \t%.2E \t%.2E" % (vol, j, cur, err, cur_tot, cur_tot_err))
  
        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

        ## Close connections
        pow_supply.ramp_voltage(0)
        volt_meter.reset()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header=hd)
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 5], np.array(out)[:, 5]*0.001, \
            'Channel Nr. [-]', 'Total Current [A]', 'All Channels ' + self.id, fn="iv_all_channels_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 3], np.array(out)[:, 4], \
            'Channel Nr. [-]', 'Leakage Current [A]',  'IV All Channels ' + self.id, fn="iv_all_channels_%s.png" % self.id)
        if 1:
            ch = 1
            self.print_graph(np.array([val for val in out if (val[2] == ch)])[:, 1], \
                np.array([val for val in out if (val[2] == ch)])[:, 3], \
                np.array([val for val in out if (val[2] == ch)])[:, 4], \
                'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_channel_%d_%s.png" % (ch, self.id))
        if (10 in np.array(out)[:, 0]):
            self.print_graph(np.array([val for val in out if (val[0] == 10)])[:, 2], \
                np.array([val for val in out if (val[0] == 10)])[:, 3], \
                np.array([val for val in out if (val[0] == 10)])[:, 4], \
                'Channel Nr. [-]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_all_channels_10V_%s.png" % self.id)
            self.print_graph(np.array([val for val in out if (val[0] == 10)])[:, 2], \
                np.array([val for val in out if (val[0] == 10)])[:, 5], \
                np.array([val for val in out if (val[0] == 10)])[:, 6], \
                'Channel Nr. [-]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_all_channels_10V_%s.png" % self.id)
        if (100 in np.array(out)[:, 0]):
            self.print_graph(np.array([val for val in out if (val[0] == 100)])[:, 2], \
                np.array([val for val in out if (val[0] == 100)])[:, 3], \
                np.array([val for val in out if (val[0] == 100)])[:, 4], \
                'Channel Nr. [-]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_all_channels_100V_%s.png" % self.id)
            self.print_graph(np.array([val for val in out if (val[0] == 100)])[:, 2], \
                np.array([val for val in out if (val[0] == 100)])[:, 5], \
                np.array([val for val in out if (val[0] == 100)])[:, 6], \
                'Channel Nr. [-]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_all_channels_100V_%s.png" % self.id)
        if (1000 in np.array(out)[:, 0]):
            self.print_graph(np.array([val for val in out if (val[0] == 1000)])[:, 2], \
                np.array([val for val in out if (val[0] == 1000)])[:, 3], \
                np.array([val for val in out if (val[0] == 1000)])[:, 4], \
                'Channel Nr. [-]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_all_channels_1000V_%s.png" % self.id)
            self.print_graph(np.array([val for val in out if (val[0] == 100)])[:, 2], \
                np.array([val for val in out if (val[0] == 1000)])[:, 5], \
                np.array([val for val in out if (val[0] == 1000)])[:, 6], \
                'Channel Nr. [-]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_total_current_all_channels_1000V_%s.png" % self.id)
        self.logging.info("\n")

    
    
    def finalise(self):
        self._finalise()