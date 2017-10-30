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
from measurement import measurement
from devices import ke2410 # power supply
from devices import ke6487 # volt meter


class test04_single_iv(measurement):
    """Measurement of I-V curve for a single cell."""

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("IV Scan")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.volt_meter_address = 23    # gpib address of the multi meter

        self.lim_cur = 0.002            # compliance in [A]
        self.lim_vol = 1000             # compliance in [V]
        # self.volt_list = np.loadtxt('config/voltagesIV.txt', dtype=int)
        # self.volt_list = [0, -1, -3, -5, -7,-9,-11,-13,-15,-17,-19,-21,-23,-25,-27,-30]
        # self.volt_list = range(1, 25, 1) + range(25, 100, 5) + range(100, 1001, 25)
        self.volt_list = range(-1, -25, -1) + range(-25, -100, -5) + range(-100, -1001, -25)

        self.delay_vol = 0.5              # delay between setting voltage and executing measurement in [s]



    def execute(self):

        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.reset()
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_voltage(0)
        pow_supply.set_terminal('rear')
        pow_supply.set_interlock_on()
        pow_supply.set_output_on()

        ## Set up volt meter
        volt_meter = ke6487(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.setup_ammeter()
        volt_meter.set_nplc(1)

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

        ## Loop over voltages
        try:
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(self.delay_vol)

                cur_tot = pow_supply.read_current()
                vol = pow_supply.read_voltage()

                measurements = np.array([volt_meter.read_current() for _ in range(5)])
                means = np.mean(measurements, axis=0)
                errs = np.std(measurements, axis=0)

                I = means
                dI = errs

                line = [v, vol, I, dI, cur_tot]
                out.append(line)
                self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

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
