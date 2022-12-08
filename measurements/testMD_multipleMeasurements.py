# ============================================================================
# File: testMD_multipleMeasurements.py
# ------------------------------
#
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       measure voltage, current, total current
#   finish
#
# Status:
#   under debvelopment
#
# ============================================================================

import time
import logging
import numpy as np
from measurements.measurement import measurement

from devices.ke2410 import * # power supply
from devices.ke7001 import * # switch

import mpld3

## load plotting functions
from utils.liveplotting import *

class testMD_multipleMeasurements(measurement):
    """Measurement of a dummy I-V curve. """

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("IV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 25  # gpib address of the power supply
        self.switch_address = 7       # gpib address of the switch


        self.channel_measurement1 = 1
        self.channel_measurement2 = 3

        self.lim_cur = 0.0002         # compliance in [A]
        self.lim_vol = 10             # compliance in [V]

        self.volt_list_measurement1 = [-10., -3, -0.5, 4.] + [5+10.*i for i in range(4)]
        self.currents_measurement1  = [0 for i in self.volt_list_measurement1]

        self.volt_list_measurement2 = [-20.,  -0.5, 7.5] + [9+15.*i for i in range(5)]
        self.currents_measurement2  = [0 for i in self.volt_list_measurement2]


        self.delay_vol = 1            # delay between setting voltage and executing measurement in [s]

        ## initialize the devices
        self.pow_supply = ke2410(self.pow_supply_address)
        self.switch = ke7001(self.switch_address)

    def reset_power_supply(self):

        ## Set up power supply
        self.pow_supply.reset()
        self.pow_supply.set_source('voltage')
        self.pow_supply.set_sense('current')
        self.pow_supply.set_current_limit(self.lim_cur)
        self.pow_supply.set_voltage(0)
        self.pow_supply.set_terminal('rear')
        # MARC pow_supply.set_interlock_on()
        self.pow_supply.set_output_on()

    def reset_switch(self):

        ## Set up the switch
        self.switch.reset(1)
        self.switch.get_idn()
        self.switch.open_all()

    def execute(self):

        ## perform the first measurement
        ## =========================================
        self.reset_power_supply()
        self.reset_switch()

        self.switch.close_channel(self.channel_measurement1)

        ## Check settings
        lim_vol = self.pow_supply.check_voltage_limit()
        lim_cur = self.pow_supply.check_current_limit()

        ## Header
        hd = ['EXECUTING MEASUREMENT 1 !!!',
            'Single IV\n',
            'Measurement Settings:',
            'Power supply voltage limit:      %8.2E V' % lim_vol,
            'Power supply current limit:      %8.2E A' % lim_cur,
            'Voltage Delay:                   %8.2f s' % self.delay_vol,
            'Switch channel to close:         %d     ' % self.channel_measurement1,
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
        ]

        ## Print Info
        for line in hd[1:-2]:
            self.logging.info(line)
        self.logging.info("\t")
        self.logging.info("\t")
        self.logging.info(hd[-1])
        self.logging.info("-" * int(1.2 * len(hd[-1])))

        ## Prepare
        out0, out1 = [], []
        ## initialize stuff for the plotting here
        fig, ax0, ax1, ax2 = init_liveplot()
        line0, line1, line2 = [], [], []

        
        ## Loop over voltages
        try:
            ##for ax in [ax0, ax1, ax2]:
            ##    ax.set_title(identifier)
            ##    #update plot label/title
            ##    ax.set_ylabel('current')
            ##    ax.set_xlabel('voltage')
            ##plt.show()

            tmp_x, tmp_y = [], []
            for _iv,v in enumerate(self.volt_list_measurement1):
                print('ramping to v: ', v)
                self.pow_supply.ramp_voltage(v,1)
                time.sleep(self.delay_vol)

                if "{: <5.2E}".format(abs(self.pow_supply.read_current())) == "{: <5.2E}".format(abs(self.lim_cur)):
                    print("Compliance " + "{: <5.2E}".format(self.lim_cur) + "A reached")
                    break

                cur_tot = self.pow_supply.read_current()
                vol = self.pow_supply.read_voltage()

                measurements = np.array([self.pow_supply.read_current() for _ in range(5)])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)

                self.currents_measurement1[_iv] = means

                I = means
                dI = errs

                line = [v, vol, I, dI, cur_tot]
                out0.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(means)

                ## update the live plotting
                line0 = live_plotter(tmp_x, tmp_y, ax0, line0, identifier='measurement 1')#, isfirst=1)


            ## Close connections
            self.pow_supply.ramp_voltage(0)
            time.sleep(5)
            #self.pow_supply.set_interlock_off()
            #self.pow_supply.set_output_off()

            print('\n\n\ndone with the first measurement!\n\n\n')

            ## ==================================================
            ## perform the second measurement !!
            ## ==================================================
            self.reset_power_supply()
            self.reset_switch()

            self.switch.close_channel(self.channel_measurement2)

            ## Check settings
            lim_vol = self.pow_supply.check_voltage_limit()
            lim_cur = self.pow_supply.check_current_limit()

            tmp_x1, tmp_y1 = [], []
            
            for _iv,v in enumerate(self.volt_list_measurement2):
                print('ramping to v: ', v)
                self.pow_supply.ramp_voltage(v,1)
                time.sleep(self.delay_vol)

                if "{: <5.2E}".format(abs(self.pow_supply.read_current())) == "{: <5.2E}".format(abs(self.lim_cur)):
                    print("Compliance " + "{: <5.2E}".format(self.lim_cur) + "A reached")
                    break

                cur_tot = self.pow_supply.read_current()
                vol = self.pow_supply.read_voltage()

                measurements = np.array([self.pow_supply.read_current() for _ in range(5)])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)

                self.currents_measurement2[_iv] = means

                I = means
                dI = errs

                line = [v, vol, I, dI, cur_tot]
                out1.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x1.append(v)
                tmp_y1.append(means*means - 3e-5*means)

                line1 = live_plotter(tmp_x1, tmp_y1, ax1, line1, identifier='measurement 2', color='c')

        except KeyboardInterrupt:
            self.pow_supply.ramp_voltage(0)
            self.reset_power_supply()
            self.reset_switch()
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")


        ## Close connections
        self.pow_supply.ramp_voltage(0)
        time.sleep(5)

        self.reset_power_supply()
        self.reset_switch()


        ## Save and print
        self.logging.info("\n")
        self.save_list(out0, "iv_measurement1.dat", fmt="%.5E", header="\n".join(hd))
        self.print_graph(np.array(out0)[:, 1], np.array(out0)[:, 2], np.array(out0)[:, 3], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_%s.png" % self.id)
        self.print_graph(np.array([val for val in out0 if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 1], \
                         np.array([val for val in out0 if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 2], \
                         np.array([val for val in out0 if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 3], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_measurement2_zoom_%s.png" % self.id)
        self.print_graph(np.array(out0)[:, 1], np.array(out0)[:, 4], np.array(out0)[:, 4]*0.01, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_measurement2_%s.png" % self.id)
        self.logging.info("\n")


        ## Save and print
        self.logging.info("\n")
        self.save_list(out1, "iv_measurement2.dat", fmt="%.5E", header="\n".join(hd))
        self.print_graph(np.array(out1)[:, 1], np.array(out1)[:, 2], np.array(out1)[:, 3], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_%s.png" % self.id)
        self.print_graph(np.array([val for val in out1 if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 1], \
                         np.array([val for val in out1 if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 2], \
                         np.array([val for val in out1 if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 3], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_measurement2_zoom_%s.png" % self.id)
        self.print_graph(np.array(out1)[:, 1], np.array(out1)[:, 4], np.array(out1)[:, 4]*0.01, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_measurement2_%s.png" % self.id)
        self.logging.info("\n")

        mpld3.show()

    def finalise(self):
        self._finalise()
