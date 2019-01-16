# ============================================================================
# File: test10_voltage_across_gr_and_pad.py
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
from devices import ke2450 # volt_meter


class test10_floating_cells(measurement):
    """Measurement voltage evolution of floating cells."""

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Floating Cells")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 24
        self.volt_meter_address = 18

        self.lim_cur = 0.0005
        self.lim_vol = 100

        self.bias_voltage = -100
        self.bias_duration = 100
        self.monitor_duration = 200



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
        volt_meter = ke2450(self.volt_meter_address)
        volt_meter.reset()
        volt_meter.set_voltage(0)
        volt_meter.set_terminal('front')
        volt_meter.setup_current_source()
        volt_meter.set_output_on()

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()

        ## Header
        hd = [
            'Single IV\n',
            'Measurement Settings:',
            'Power supply voltage limit:      %8.2E V' % lim_vol,
            'Power supply current limit:      %8.2E A' % lim_cur,
            '\n\n',
            'Nominal Bias Voltage [V]\tMeasured Bias Voltage [V]\tTime [s]\tFloating voltage [V]\tFloating Voltage Erro [V]\tTotal Current[A]\t'
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
        t = 0

        ## Ramp to voltage and monitor
        pow_supply.ramp_voltage(self.bias_voltage)
        time.sleep(0.1)

        t0 = time.time()
        while t < self.bias_duration:
            t = time.time() - t0

            vol = pow_supply.read_voltage()
            cur_tot = pow_supply.read_current()

            measurements = np.array([volt_meter.read_voltage() for _ in range(5)])
            means = np.mean(measurements, axis=0)
            errs = np.std(measurements, axis=0)

            v = means
            dv = errs

            line = [self.bias_voltage, vol, t, v, dv, cur_tot]
            out.append(line)
            self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        ## Ramp down to zero and monitor
        pow_supply.ramp_voltage(0)
        time.sleep(0.1)

        while t < self.monitor_duration:
            t = time.time() - t0

            vol = pow_supply.read_voltage()
            cur_tot = pow_supply.read_current()

            measurements = np.array([volt_meter.read_voltage() for _ in range(5)])
            means = np.mean(measurements, axis=0)
            errs = np.std(measurements, axis=0)

            v = means
            dv = errs

            line = [v, vol, t, v, dv, cur_tot]
            out.append(line)
            self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))


        ## Close connections
        switch.reset()
        pow_supply.ramp_voltage(0)
        time.sleep(15)
        volt_meter.set_output_off()
        volt_meter.reset()
        pow_supply.set_interlock_off()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header=' volt [V]\tcurrent[A]\ttotal current[A]\t')
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 3], 'Time [s]', 'Floating Cell Voltage [V]', fn="iv.png")
        self.logging.info("\n")



    def finalise(self):
        self._finalise()
