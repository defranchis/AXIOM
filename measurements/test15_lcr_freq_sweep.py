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
#
# ============================================================================

import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # forward bias power supply
from devices import ke2450 # interpad bias power supply
from devices import ke6487 # volt meter
from devices import hp4980 # lcr meter
from devices import switchcard # switch

#monkey patch the classes to support running without any equipment
#from devices import simulatedPsu, simulatedMultimeter
#if False:
#    ke2410 = simulatedPsu
#    ke2450 = simulatedPsu
#    ke6487 = simulatedMultimeter
#    def dummy(*args, **kwargs): pass
#    time.sleep = dummy


class test15_lcr_freq_sweep(measurement):
    """Measure interpad resistance"""

    def initialise(self):
        self._initialise()
        self.delay_f = 0.5              # delay between frequencies
        self.lcr_meter_address = 17     # gpib address of the lcr meter
        self.lcr_vol = 0.5              # ac voltage amplitude in [V]
        self.lcr_frequencies = np.logspace(1,6,20)          # ac voltage frequency in [kHz]



    def execute(self):

        ## Set up lcr meter
        lcr_meter = hp4980(self.lcr_meter_address)
        lcr_meter.reset()
        lcr_meter.set_voltage(self.lcr_vol)
        lcr_meter.set_frequency(self.lcr_frequencies[0])
        lcr_meter.set_mode('RX')

        hd = [
            'Single Impedance',
            'Measurement Settings:',
            'Frequency [Hz]\tR [ohm]\tdR \t X [ohm]\tdX \t'
            ]

        ## Print Info
        for line in hd:
            self.logging.info(line)
        self.logging.info("-"*int(1.2*len(hd[-1])))

        ## Prepare
        out = []


        ## Loop over frequencies
        try:

            for f in self.lcr_frequencies:
                lcr_meter.set_frequency(f)
                time.sleep(self.delay_f)
                time.sleep(0.001)

                measurements = np.array([lcr_meter.execute_measurement() for _ in range(5)])
                means = np.mean(measurements, axis = 0)
                errs = np.std(measurements, axis = 0)

                R, X = means
                dR, dX = errs
                #R, X = lcr_meter.execute_measurement()
                #dR, dX = (0,0)

                line = [f, R, dR, X, dX]
                out.append(line)
                self.logging.info("\t{: <30.4E} \t{: <30.4E} \t{: <30.4E} \t{: <30.4E} \t{: <30.4E}".format(*line))

        except KeyboardInterrupt:
            self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

        ## Close connections


        ## Save and print
        self.logging.info("\n")
        self.save_list(out, "ZV.dat", fmt="%.5E", header="\n".join(hd))


    def finalise(self):
        self._finalise()
