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
from devices import ke6487 # ampere meter
from devices import ke6517 # alternative ampere meter
from devices import switchcard # switch


class test02_scan_iv(measurement):
    """Measurement of I-V curves for individual cells across the wafer matrix."""

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("IV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 18    # gpib address of the power supply
        self.volt_meter_address = 15    # gpib address of the multi meter
        self.switch_address = 'COM4'    # serial port of switch card

        self.lim_cur = 0.01             # compliance in [A]
        self.lim_vol = 1000             # compliance in [V]

        self.cell_list = np.loadtxt('config/Probe_card_IFX_8in.txt', dtype=int)[:,1]
        self.volt_list = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10, -11, -12, -13, -14, -15, -16, -17, -18, -19, -20, -21, -22, -23, -24, -25, -26, -27, -28, -29, -30, -40, -50]

        self.delay_vol = 5              # delay between setting voltage and executing measurement in [s]
        self.delay_ch = 0.3             # delay between setting channel and executing measurement in [s]



    def execute(self):

        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.reset()
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_voltage(0)
        pow_supply.set_terminal('rear')
        #pow_supply.set_interlock_on()
        pow_supply.set_output_on()

        ## Set up volt meter
        #volt_meter = ke6487(self.volt_meter_address)
        volt_meter = ke6517(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.setup_ammeter()
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
        # humd_pc = switch.get_probecard_humidity()
        # humd_sc = switch.get_matrix_humidity()
        type_msr = switch.get_measurement_type()
        type_disp = switch.get_display_mode()

        ## Header
        hd = [
            'Scan IV\n',
            'Measurement Settings:',
            'Power supply voltage limit:      %8.2E V' % lim_vol,
            'Power supply current limit:      %8.2E A' % lim_cur,
            'Voltage delay:                   %8.2f s' % self.delay_vol,
            'Channel delay:                   %8.2f s' % self.delay_ch,
            'Probecard temperature:           %8.1f C' % temp_pc,
            'Switchcard temperature:          %8.1f C' % temp_sc,
            # 'Probecard humidity:              %s %' % humd_pc,
            # 'Switchcard humidity:             %s %' % humd_sc,
            'Switchcard measurement setting:  %s' % type_msr,
            'Switchcard display setting:      %s' % type_disp,
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tChannel [-]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        ## Print Info
        for line in hd[1:-2]:
            self.logging.info(line)
        self.logging.info("\t")
        self.logging.info("\t")
        self.logging.info(hd[-1])
        self.logging.info("-" * int(1.2 * len(hd[-1])))

        ## Prepare
        out = []
        flag_list = np.zeros(len(self.cell_list))

       ## Loop over voltages
        try:
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)
                time.sleep(0.001)

                j = 0
                for c in self.cell_list:

                    ## Only measure unflagged cells
                    if flag_list[j] == 0:

                        ## Through away first measurements after voltage change
                        if j == 0:
                            switch.open_channel(c)
                            for k in range(3):
                                volt_meter.read_current()
                                pow_supply.read_current()
                                time.sleep(0.001)

                        ## Go on with normal measurement
                        switch.open_channel(c)
                        time.sleep(self.delay_ch)

                        cur_tot = pow_supply.read_current()
                        vol = pow_supply.read_voltage()

                        measurements = np.array([volt_meter.read_current() for _ in range(5)])
                        means = np.mean(measurements, axis=0)
                        errs = np.std(measurements, axis=0)

                        i = means
                        di = errs

                        ## Flag cell if current too large
                        if abs(i) > 1E-5:
                            flag_list[j] = 1

                    ## Handle flagged cells
                    else:
                        cur_tot = pow_supply.read_current()
                        vol = pow_supply.read_voltage()

                        i = np.nan
                        di = np.nan

                    j += 1
                    line = [v, vol, j, i, di, cur_tot]
                    out.append(line)
                    time.sleep(0.001)
                    self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5d}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

        ## Close connections
        pow_supply.ramp_voltage(0)
        time.sleep(15)
        pow_supply.set_interlock_off()
        pow_supply.set_output_off()
        pow_supply.reset()
        volt_meter.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header="\n".join(hd))
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
