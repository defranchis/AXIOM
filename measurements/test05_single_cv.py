# ============================================================================
# File: test05_singe_cv.py
# ------------------------------
#
# Notes:
#
# Layout:
#   configure and prepare
#   for each voltage:
#       set voltage
#       measure voltage, r, x
#       calculate cp, cs
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
from utils import lcr_series_equ, lcr_parallel_equ, lcr_error_cp


class test05_single_cv(measurement):
    """Measurement of C-V curve for a single cell on the wafer."""

    def initialise(self):
        self.logging.info("\t")
        self.logging.info("")
        self.logging.info("------------------------------------------")
        self.logging.info("Single CV Measurement")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()
        self.pow_supply_address = 24    # gpib address of the power supply
        self.lcr_meter_address = 17     # gpib address of the lcr meter

        self.lim_cur = 0.0001         # compliance in [A]
        self.lim_vol = 1000              # compliance in [V]
        #self.volt_list = np.loadtxt('config/voltagesCV6Inch128Pos.txt', dtype=int)
        #self.volt_list = [0, -25, -50, -75, -100, -125, -150, -170, -180, -190, -200, -210, -220, -230, -250, -275, -300, -325, -350, -400]
        self.volt_list = range(-20, -501, -20) #range(10, 501, 10) # range(1, 25, 1) + range(25, 100, 5) + range(100, 501, 25)

        self.lcr_vol = 0.5              # ac voltage amplitude in [mV]
        self.lcr_freq = 10000           # ac voltage frequency in [kHz]

        self.delay_vol = 5              # delay between setting voltage and executing measurement in [s]



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
        #pow_supply.set_current_range(1E-3, 1)

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
            'Single IV\n',
            'Power Supply voltage limit:      %8.2E V' % lim_vol,
            'Power Supply current limit:      %8.2E A' % float(lim_cur),
            'LCR measurement voltage:         %8.2E V' % lcr_vol,
            'LCR measurement frequency:       %8.2E Hz' % lcr_freq,
            'Voltage Delay:                   %8.2f s' % self.delay_vol,
            '\n\n',
            'Nominal Voltage [V]\t Measured Voltage [V]\tFreq [Hz]\tR [Ohm]\tR_Err [Ohm]\tX [Ohm]\tX_Err [Ohm]\tCs [F]\tCp [F]\tTotal Current [A]'
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

                while "{: <5.2E}".format(pow_supply.read_voltage()) != "{: <5.2E}".format(v):
                    pow_supply.check_current_limit()
                    pow_supply.read_current()
                    #print "{: <5.2E}".format(pow_supply.read_voltage())
                    #print "{: <5.2E}".format(v)
                    if "{: <5.2E}".format(pow_supply.read_current()) == "{: <5.2E}".format(self.lim_cur):
                        break
                    time.sleep(0.5)

                time.sleep(self.delay_vol)
                if "{: <5.2E}".format(pow_supply.read_current()) == "{: <5.2E}".format(self.lim_cur):
                    print "Compliance " + "{: <5.2E}".format(self.lim_cur) + "A reached"
                    break

                #print pow_supply.check_current_limit()
                #print pow_supply.read_current()
                vol = pow_supply.read_voltage()
                cur_tot = pow_supply.read_current()

                # for freq_nom in [self.lcr_freq]:
                for freq_nom in [1E4]: #[5E2, 1E3, 5E3, 7.5E3, 9E3, 1E4, 1.1E4, 1.5E4, 2E4, 5E4, 1E5, 2E5, 1E6]
                    lcr_meter.set_frequency(freq_nom)
                    time.sleep(1)
                    freq = float(lcr_meter.check_frequency())

                    measurements = np.array([lcr_meter.execute_measurement() for _ in range(10)])
                    means = np.mean(measurements, axis=0)
                    errs = np.std(measurements, axis=0)

                    r, x = means
                    dr, dx = errs

                    z = np.sqrt(abs(r)**2 + x**2)
                    phi = np.arctan(x/abs(r))
                    r_s, c_s, l_s, D = lcr_series_equ(freq, z, phi)
                    r_p, c_p, l_p, D = lcr_parallel_equ(freq, z, phi)

                    line = [v, vol, freq, r, dr, x, dx, c_s, c_p, cur_tot]
                    out.append(line)
                    self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        except KeyboardInterrupt:
            pow_supply.ramp_voltage(0)
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")


        ## Close connections
        pow_supply.ramp_voltage(0)
        time.sleep(10)
        pow_supply.set_interlock_off()
        pow_supply.set_output_off()
        pow_supply.reset()

        ## Save and print
        self.logging.info("")
        self.save_list(out, "cv.dat", fmt="%.5E", header="\n".join(hd))
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 7], np.array(out)[:, 7] * 0.01, \
                         'Bias Voltage [V]', 'Parallel Capacitance [F]',  'CV ' + self.id, fn="cv_%s.png" % self.id)
        self.print_graph(np.array(out)[2:, 1], np.array(out)[2:, 7]**(-2), 0, \
                         'Bias Voltage [V]', '1/C^2 [1/F^2]',  '1/C2 ' + self.id, fn="1c2v_%s.png" % self.id)
        self.print_graph(np.array(out)[:, 1], np.array(out)[:, 9], np.array(out)[:, 9]*0.01, \
                         'Bias Voltage [V]', 'Total Current [A]', 'IV ' + self.id, fn="iv_total_current_%s.png" % self.id)
        self.logging.info("")


    def finalise(self):
        self._finalise()
