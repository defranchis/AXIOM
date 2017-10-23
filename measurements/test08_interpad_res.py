# ============================================================================
# File: test08_interpad_res.py
# ------------------------------
#
# Notes: Measure the interpad resistance
#
# Layout:
#   configure and prepare,
#   set the forward bias voltage to a constant
#   a second source biases between the cells
#   for each interpad bias voltage:
#       set voltage
#       while measurement time is not reached:
#           measure voltage, time, current, total current
#   finish
#
# Status:
#
# ============================================================================

import time
import logging
import numpy as np
import scipy.optimize as opt
from measurement import measurement
from devices import ke2410 # forward bias power supply
from devices import ke2450 # interpad bias power supply
from devices import ke6487 # volt meter
from devices import switchcard # switch


from devices import simulatedSMU, simulatedDMM
if 0:
    ke2410 = simulatedSMU
    ke2450 = simulatedSMU
    ke6487 = simulatedDMM
    def dummy(*args, **kwargs):
        pass
    time.sleep = dummy



def linef(x, a, b):
    return a * x + b


class test08_interpad_res(measurement):
    """Measure interpad resistance"""

    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("Interpad Reistance")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.forward_pow_supply_address = 24    # gpib address of the forward bias power supply
        self.interpad_pow_supply_address = 0    # gpib address of the interpad bias power supply
        self.volt_meter_address = 23            # gpib address of the multimeter
        self.switch_address = 'COM3'            # serial port of switch card

        self.forward_bias_lim_cur = 0.0005           # compliance in [A]
        self.interpad_bias_lim_cur = 0.0005
        self.lim_vol = 500                           # compliance in [V]

        self.bias_volt_list = [50, 100, 200, 300]
        self.interpad_volt_list = [0, 1, 2, 3, 4, 5]

        self.delay_vol = 1              # delay between setting voltage and executing measurement in [s]



    def execute(self):

        ## Set up the forward bias power supply
        forward_pow_supply = ke2410(self.forward_pow_supply_address)
        forward_pow_supply.reset()
        forward_pow_supply.set_source('voltage')
        forward_pow_supply.set_sense('current')
        forward_pow_supply.set_current_limit(self.forward_bias_lim_cur)
        forward_pow_supply.set_voltage(0)
        forward_pow_supply.set_terminal('rear')
        forward_pow_supply.set_output_on()

        ## Set up the interpad bias power supply
        interpad_pow_supply = ke2450(self.interpad_pow_supply_address)
        interpad_pow_supply.reset()
        interpad_pow_supply.set_source('voltage')
        interpad_pow_supply.set_sense('current')
        interpad_pow_supply.set_current_limit(self.interpad_bias_lim_cur)
        interpad_pow_supply.set_voltage(0)
        interpad_pow_supply.set_terminal('rear')
        interpad_pow_supply.set_output_on()

        ## Check settings
        lim_vol = forward_pow_supply.check_voltage_limit()
        lim_cur = forward_pow_supply.check_current_limit()

        ## Header
        hd = [
            'Interpad R\n',
            'Measurement Settings:',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % lim_cur,
            'Voltage Delay:                   %8.2f s' % self.delay_vol,
            '\n\n',
            'Interpad Voltage [V]\tInterpad Current Mean [A]\tInterpad Current Error [A]\tForward Bias Voltage\tForward Bias Current[A]\t'
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
            for vbias in self.bias_volt_list:
                forward_pow_supply.ramp_voltage(vbias)
                time.sleep(self.delay_vol)

                i = []
                di = []
                for v in self.interpad_volt_list:
                    interpad_pow_supply.ramp_voltage(v)
                    time.sleep(0.1)

                    cur_tot = forward_pow_supply.read_current()

                    measurements = np.array([interpad_pow_supply.read_current() for _ in range(5)])
                    i.append(np.mean(measurements))
                    di.append(np.std(measurements))

                ## Calculate resistance
                popt, pcov = opt.curve_fit(linef, self.interpad_volt_list, i, sigma=di)
                r = popt[0]
                dr = np.sqrt(pcov[0, 0])

                ## Write output
                k = 0
                for v in self.interpad_volt_list:
                    line = [vbias, v, i[k], di[k], r, dr, cur_tot]
                    k += 1
                    out.append(line)

                    self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}".format(*line))

        except KeyboardInterrupt:
            interpad_pow_supply.ramp_voltage(0)
            forward_pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

        ## Close connections
        interpad_pow_supply.ramp_voltage(0)
        forward_pow_supply.ramp_voltage(0)
        time.sleep(15)

        forward_pow_supply.set_output_off()
        forward_pow_supply.reset()

        interpad_pow_supply.set_output_off()
        interpad_pow_supply.reset()

        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "iv.dat", fmt="%.5E", header="\n".join(hd))


    def finalise(self):
        self._finalise()
