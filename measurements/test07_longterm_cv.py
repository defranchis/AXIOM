# ============================================================================
# File: test07_longterm_cv.py
# ------------------------------
#
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       while measurement time is not reached:
#           measure voltage, time, z, phi
#           calculate cp, cs
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
from devices import hp4980 # lcr meter
from utils import lcr_series_equ, lcr_parallel_equ


class test07_longterm_cv(measurement):
    """Multiple measurements of IV over a longer period."""

    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("CV Longterm")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.lcr_meter_address = 17     # gpib address of the lcr meter
        self.switch_address = 'COM3'    # serial port of switch card

        self.lim_cur = 0.0005           # compliance in [A]
        self.lim_vol = 500              # compliance in [V]
        self.volt_list = [300]         # list of bias voltage in [V]

        self.delay_msr = 0.1            # delay between two consecutive measurements in [s]
        self.duration_msr = 120         # total measurement time in [s]

        self.lcr_vol = 0.5              # ac voltage amplitude in [mV]
        self.lcr_freq = 50000           # ac voltage frequency in [kHz]



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

        ## Set up lcr meter
        lcr_meter = hp4980(self.lcr_meter_address)
        lcr_meter.reset()
        lcr_meter.set_voltage(self.lcr_vol)
        lcr_meter.set_frequency(self.lcr_freq)
        lcr_meter.set_mode('RX')

        ## Check settings
        lim_vol = pow_supply.check_voltage_limit()
        lim_cur = pow_supply.check_current_limit()
        lcr_vol = float(lcr_meter.check_voltage())
        lcr_freq = float(lcr_meter.check_frequency())

        ## Header
        hd = [
            'Longterm CV\n',
            'Measurement Settings:',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % float(lim_cur),
            'LCR measurement voltage:         %8.2E V' % lcr_vol,
            'LCR measurement frequency:       %8.2E Hz' % lcr_freq,
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tTime [s]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]'
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
                time.sleep(self.delay_msr)

                vol = pow_supply.read_voltage()
                cur_tot = pow_supply.read_current()

                t = 0
                t0 = time.time()
                while t < self.duration_msr:
                    t = time.time() - t0
                    time.sleep(0.1)

                    vol = pow_supply.read_voltage()
                    #cur_tot = pow_supply.read_current()

                    measurements = np.array([lcr_meter.execute_measurement() for _ in range(5)])
                    means = np.mean(measurements, axis=0)
                    errs = np.std(measurements, axis=0)

                    r, x = means
                    dr, dx = errs

                    z = np.sqrt(r**2 + x**2)
                    phi = np.arctan(x/r)
                    r_s, c_s, l_s, D = lcr_series_equ(self.lcr_freq, z, phi)
                    r_p, c_p, l_p, D = lcr_parallel_equ(self.lcr_freq, z, phi)

                    line = [v, vol, t, r, dr, x, dx, c_s, c_p, cur_tot]
                    out.append(line)
                    self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

        ## Close connections
        pow_supply.ramp_voltage(0)
        time.sleep(15)
        pow_supply.set_interlock_off()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("")
        self.save_list(out, "cv_long.dat", fmt="%.5E", header="\n".join(hd))
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 8], np.array(out)[:, 8]*0.01, 'Time [s]',
                         'Capacitance [F]', 'Longerm CV ' + self.id, fn="cv_long_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 2], np.array(out)[:, 9], np.array(out)[:, 9]*0.01, 'Time [s]',
                         'Total Current [A]', 'Longerm CV ' + self.id, fn="cv_long_total_current_%s.png" % self.id)
        self.logging.info("")


    def finalise(self):
        self._finalise()
