# ============================================================================
# File: test04_single_iv.py
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
#   works well
#
# ============================================================================

import time
import logging
import numpy as np
from measurements.measurement import measurement
#from devices import ke2410 # power supply
#from devices import ke7001 # switch
from devices.ke2410 import * # power supply
from devices.ke7001 import * # switch

from utils.liveplotting import *

class testMD_dummyIVWithSwitch(measurement):
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


        self.close_channnel = 1

        self.lim_cur = 0.0002         # compliance in [A]
        self.lim_vol = 10             # compliance in [V]

        self.volt_list = [-10., -3, -0.5, 0.5, 2.5, 4.] + [4+10.*i for i in range(10)]
        self.currents  = [0 for i in self.volt_list]

        self.delay_vol = 1            # delay between setting voltage and executing measurement in [s]



    def execute(self):

        ## Set up the switch
        switch = ke7001(self.switch_address)
        switch.reset(1)
        switch.get_idn()
        switch.open_all()

        switch.close_channel(1)


        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.reset()
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_voltage(0)
        pow_supply.set_terminal('rear')
        # MARC pow_supply.set_interlock_on()
        pow_supply.set_output_on()

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()

        ## Header
        hd = [
            'Single IV\n',
            'Measurement Settings:',
            'Power supply voltage limit:      %8.2E V' % lim_vol,
            'Power supply current limit:      %8.2E A' % lim_cur,
            'Voltage Delay:                   %8.2f s' % self.delay_vol,
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
        out = []
        
        x_vec = self.volt_list
        y_vec = self.currents

        ax0, ax1, ax2 = init_liveplot()

        line0, line1, line2 = [], [], []

        ## Loop over voltages
        try:
            tmp_x, tmp_y = [], []
            for _iv,v in enumerate(self.volt_list):
                print('ramping to v: ', v)
                pow_supply.ramp_voltage(v,1)
                time.sleep(self.delay_vol)

                if "{: <5.2E}".format(abs(pow_supply.read_current())) == "{: <5.2E}".format(abs(self.lim_cur)):
                    print("Compliance " + "{: <5.2E}".format(self.lim_cur) + "A reached")
                    break

                cur_tot = pow_supply.read_current()
                vol = pow_supply.read_voltage()

                measurements = np.array([pow_supply.read_current() for _ in range(5)])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)

                self.currents[_iv] = means

                I = means
                dI = errs

                line = [v, vol, I, dI, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

                tmp_x.append(v)
                tmp_y.append(means)
                #line1 = live_plotter(tmp_x, tmp_y, line1, identifier='measurement 1')

                line0 = live_plotter(tmp_x, tmp_y, ax0, line0, identifier='measurement 1')
                line1 = live_plotter(tmp_x, tmp_y, ax1, line1, identifier='measurement 2', color='cyan')

        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")


        ## Close connections
        pow_supply.ramp_voltage(0)
        #time.sleep(15)
        time.sleep(5)
        pow_supply.set_interlock_off()
        pow_supply.set_output_off()
        pow_supply.reset()
        switch.open_all()
        switch.reset()


        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header="\n".join(hd))
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 2], np.array(out)[:, 3], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_%s.png" % self.id)
        self.print_graph(np.array([val for val in out if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 1], \
                         np.array([val for val in out if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 2], \
                         np.array([val for val in out if (abs(val[0]) < 251 and abs(val[0])>-0.1)])[:, 3], \
                         'Bias Voltage [V]', 'Leakage Current [A]', 'IV ' + self.id, fn="iv_zoom_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 4], np.array(out)[:, 4]*0.01, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_%s.png" % self.id)
        self.logging.info("\n")


    def finalise(self):
        self._finalise()
