# ============================================================================
# File: test03_scan_cv.py
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
from devices import hp4980 # lcr meter
from devices import switchcard # switch
from utils import lcr_series_equ, lcr_parallel_equ, lcr_error_cp



class test03_scan_cv(measurement):
    """Measurement of C-V curves for individual cells across the wafer matrix."""

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("")
        self.logging.info("------------------------------------------")
        self.logging.info("CV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of C-V curves for individual cells across the wafer matrix.")
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.lcr_meter_address = 17     # gpib address of the lcr meter
        self.switch_address = 'COM3'    # serial port of switch card

        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 100              # compliance in [V]
        self.cell_list = np.loadtxt('config/channels256_from_schematics_sorted_few.txt', dtype=int)
        self.volt_list = np.loadtxt('config/voltagesCV6Inch256Pos.txt', dtype=int)

        self.delay_vol = 30              # delay between setting voltage and executing measurement in [s]
        self.delay_ch = 0.3              # delay between setting channel and executing measurement in [s]

        self.lcr_vol = 0.501             # ac voltage amplitude in [mV]
        self.lcr_freq = 50000            # ac voltage frequency in [Hz]

        #self.cor_open = np.loadtxt('config/valuesOpen.txt') # open correction for lcr meter
        #self.cor_short = np.loadtxt('config/valuesShort.txt') # short correction for lcr meter
        #self.cor_load = np.loadtxt('config/valuesLoad.txt') # load correction for lcr meter


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

        ## Set up lcr meter
        lcr_meter = hp4980(self.lcr_meter_address)
        lcr_meter.reset()
        lcr_meter.set_voltage(self.lcr_vol)
        lcr_meter.set_frequency(self.lcr_freq)
        lcr_meter.set_mode('RX')

        # Set up switch
        switch = switchcard(self.switch_address)
        switch.reboot()
        switch.set_measurement_type('CV')
        switch.set_display_mode('OFF')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        lcr_vol = float(lcr_meter.check_voltage())
        lcr_freq = float(lcr_meter.check_frequency())
        temp_pc = switch.get_probecard_temperature()
        temp_sc = switch.get_matrix_temperature()
        # humd_pc = switch.get_probecard_humidity()
        # humd_sc = switch.get_matrix_humidity()
        type_msr = switch.get_measurement_type()
        type_disp = switch.get_display_mode()

        ## Print info
        self.logging.info("Settings:")
        self.logging.info("Power supply voltage limit:      %8.2E V" % lim_vol)
        self.logging.info("Power supply current limit:      %8.2E A" % lim_cur)
        self.logging.info("LCR measurement voltage:         %8.2E V" % lcr_vol)
        self.logging.info("LCR measurement frequency:       %8.2E Hz" % lcr_freq)
        self.logging.info("Voltage delay:                   %8.2f s" % self.delay_vol)
        self.logging.info("Channel delay:                   %8.2f s" % self.delay_ch)
        self.logging.info("Probecard temperature:           %8.1f C" % temp_pc)
        self.logging.info("Switchcard temperature:          %8.1f C" % temp_sc)
        # self.logging.info("Probecard humidity:              %8.1f %" % humd_pc)
        # self.logging.info("Switchcard humidity:             %8.1f %" % humd_sc)
        self.logging.info("Switchcard measurement setting:  %s" % type_msr)
        self.logging.info("Switchcard display setting:      %s" % type_disp)
        self.logging.info("\t")

        self.logging.info("\tVoltage [V]\tChannel [-]\tFrequency [Hz]\tR [kOhm]\tX [kOhm]\tCs [pF]\tCp [pF]\tTotal Current [A]")
        self.logging.info("\t--------------------------------------------------------------------------")


        ## Prepare
        out = []
        hd = ' Scan CV\n' \
           + ' Measurement Settings:\n' \
           + ' Power supply voltage limit:      %8.2E V\n' % lim_vol \
           + ' Power supply current limit:      %8.2E A\n' % lim_cur \
           + ' LCR measurement voltage:         %8.2E V\n' % lcr_vol \
           + ' LCR measurement frequency:       %8.0E Hz\n' % lcr_freq \
           + ' Voltage Delay:                   %8.2f s\n' % self.delay_vol \
           + ' Channel Delay:                   %8.2f s\n' % self.delay_ch \
           + ' Probecard temperature:           %8.1f C\n' % temp_pc \
           + ' Switchcard temperature:          %8.1f C\n' % temp_sc \
           + ' Switchcard measurement setting:  %s\n' % type_msr \
           + ' Switchcard display setting:      %s\n\n\n' % type_disp \
           + ' Nominal Voltage [V]\t Measured Voltage [V]\tFrequency[Hz]\tChannel [-]\tR [kOhm]\tR_Err [kOhm]\tX [kOhm]\tX_Err [kOhm]\tC [pF]\tTotal Current [A]\n'

        ## Loop over voltages
        try:
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)

                cur_tot = pow_supply.read_current()
                vol = pow_supply.read_voltage()

                j = 1
                for c in self.cell_list:
                    switch.open_channel(c)
                    time.sleep(self.delay_ch)

                    for freq_nom in [5E2, 1E3, 2E3, 3E3, 5E3, 1E4, 2E4, 5E4, 1E5, 1E6]:
                        lcr_meter.set_frequency(freq_nom)
                        time.sleep(1)
                        freq = float(lcr_meter.check_frequency())

                        ## Through away first measurements after voltage change
                        if j == 0:
                            switch.open_channel(c)
                            for k in range(5):
                                lcr_meter.execute_measurement()
                                pow_supply.read_current()
                                time.sleep(0.001)

                        measurements = np.array([lcr_meter.execute_measurement() for _ in range(5)])
                        means = np.mean(measurements, axis = 0)
                        errs = np.std(measurements, axis = 0)

                        R, X = means
                        dR, dX = errs

                        time.sleep(0.001)

                        z = np.sqrt(R**2 + X**2)
                        phi = np.arctan(X/R)
                        r_s, c_s, l_s, D = lcr_series_equ(freq, z, phi)
                        r_p, c_p, l_p, D = lcr_parallel_equ(freq, z, phi)

                        out.append([v, vol, freq, c, r, r_err, x, x_err, c_s, c_p, cur_tot])
                        self.logging.info("\t%.2f \t%4d \t%7d \t%.3f \t%.3f \t%.3E \t%.3E \t%.2E" % (vol, j, freq, r/1000., x/1000., c_s*10**(12), c_p*10**(12), cur_tot))

                    j += 1


        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")


        ## Close connections
        pow_supply.ramp_voltage(0)
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "cv.dat", fmt="%.5E", header=hd)
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 8], np.array(out)[:, 8]*0.01, \
            'Channel Nr. [-]', 'Total Current [A]', 'All Channels ' + self.id, fn="cv_total_current_all_channels_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 6], np.array(out)[:, 6]*0.01, \
            'Channel Nr. [-]', 'Capacitance [F]',  'CV All Channels ' + self.id, fn="cv_all_channels_%s.png" % self.id)
        if 0:
            ch = 1
            self.print_graph(np.array([val for val in out if (val[2] == ch)])[:, 1], \
                np.array([val for val in out if (val[2] == ch)])[:, 5], \
                np.array([val for val in out if (val[2] == ch)])[:, 6], \
                'Bias Voltage [V]', 'Parallel Capacitance [F]', 'CV ' + self.id, fn="cv_channel_%d_%s.png" % (ch, self.id))
            self.print_graph(np.array([val for val in out if (val[2] == ch)])[2:, 1], \
                np.array([val for val in out if (val[2] == ch)])[2:, 7]**(-2), \
                np.array([val for val in out if (val[2] == ch)])[2:, 7] * 0.01 * 2 * (np.array([val for val in out if (val[2] == ch)])[2:, 7]*0.01)**(-3), \
                'Bias Voltage [V]', '1/C^2 [1/F^2]', '1/C2 ' + self.id, fn="1c2v_channel%d_%s.png" % (ch, self.id))
        if (10 in np.array(out)[:, 0]):
            self.print_graph(np.array([val for val in out if (val[0] == 10)])[:, 2], \
                np.array([val for val in out if (val[0] == 10)])[:, 5], \
                np.array([val for val in out if (val[0] == 10)])[:, 6], \
                'Channel Nr. [-]', 'Parallel Capacitance [F]', 'CV ' + self.id, fn="cv_all_channels_10V_%s.png" % self.id)
            self.print_graph(np.array([val for val in out if (val[0] == 10)])[:, 2], \
                np.array([val for val in out if (val[0] == 10)])[:, 8], \
                np.array([val for val in out if (val[0] == 10)])[:, 8]*0.01, \
                'Channel Nr. [-]', 'Total Current [A]', 'CV ' + self.id, fn="cv_total_current_all_channels_10V_%s.png" % self.id)
        if (100 in np.array(out)[:, 0]):
            self.print_graph(np.array([val for val in out if (val[0] == 100)])[:, 2], \
                np.array([val for val in out if (val[0] == 100)])[:, 5], \
                np.array([val for val in out if (val[0] == 100)])[:, 6], \
                'Channel Nr. [-]', 'Parallel Capacitance [F]', 'CV ' + self.id, fn="cv_all_channels_100V_%s.png" % self.id)
            self.print_graph(np.array([val for val in out if (val[0] == 100)])[:, 2], \
                np.array([val for val in out if (val[0] == 100)])[:, 8], \
                np.array([val for val in out if (val[0] == 100)])[:, 8]*0.01, \
                'Channel Nr. [-]', 'Total Current [A]', 'CV ' + self.id, fn="cv_total_current_all_channels_100V_%s.png" % self.id)
        self.logging.info("\n")

        if 0:
            self.save_list(range(0,512,1), "channel_list.txt", fmt='%d', header='')

    def finalise(self):
        self._finalise()
