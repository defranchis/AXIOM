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
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.volt_meter_address = 23    # gpib address of the multimeter
        self.switch_address = 'COM3'    # serial port of switch card

        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 500              # compliance in [V]
        # self.volt_list = [+10, +50, +100, +200, +300] 
        self.volt_list = [-10, -50, -100, -200, -300]          # list of bias voltage in [V]

        self.delay_msr = 0.05          # delay between two consecutive measurements in [s]
        self.duration_msr = 15         # total measurement time in [s]



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
            'Longterm IV\n',
            'Measurement Settings:',
            'Power supply voltage limit:      %8.2E V' % lim_vol,
            'Power supply current limit:      %8.2E A' % lim_cur,
            '\n\n',
            'Nominal Voltage [V]\tMeasured Voltage [V]\tTime [s]\tCurrent [A]\tCurrent Error [A]\tTotal Current[A]\t'
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

                vol = pow_supply.read_voltage()
                cur_tot = pow_supply.read_current()

                t = 0
                t0 = time.time()
                while t < self.duration_msr:
                    time.sleep(self.delay_msr)
                    t = time.time() - t0

                    cur_tot = pow_supply.read_current()

                    measurements = np.array([volt_meter.read_current() for _ in range(3)])
                    means = np.mean(measurements, axis=0)
                    errs = np.std(measurements, axis=0)

                    i = means
                    di = errs

                    line = [v, vol, t, i, di, cur_tot]
                    out.append(line)
                    self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

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
        self.logging.info("\t")
        self.save_list(out, "iv_long.dat", fmt="%.5E", header="\n".join(hd))
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 3], np.array(out)[:, 4], 'Time [s]', 'Leakage Current [A]', 'Longterm IV ' + self.id, fn="iv_long_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 5], np.array(out)[:, 5]*0.01, 'Time [s]', 'Total Current [A]', 'Longterm IV ' + self.id, fn="iv_long_total_current%s.png" % self.id)
        self.logging.info("\t")


    def finalise(self):
        self._finalise()
