import time, math, os
import logging
import numpy as np
from measurements.measurement import measurement


from devices.hp4980 import * # switch

import mpld3

## load plotting functions
#from utils.liveplotting import *

from utils.correct_cv import lcr_series_equ, lcr_parallel_equ, lcr_error_cp


def getCorrection(lcr_meter,freq):
    lcr_meter.set_frequency(freq)
    measurements = np.array([lcr_meter.execute_measurement() for _ in range(100)])
    means = np.mean(measurements, axis=0)
    print(freq,means)
    


lcr_meter = hp4980(17)
lcr_meter.reset()
lcr_meter.set_voltage(0.5)
lcr_meter.set_mode('RX')
lcr_freq = [1e4, 1e5, 1e6]


for freq in lcr_freq:
    getCorrection(lcr_meter,freq)

'''
class testMD_fullStrip(measurement):
    """Measurement of a dummy I-V curve. """

    def initialise(self):

        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Running all 3 measurements of the silicon! :)")
        self.logging.info("------------------------------------------")
        self.logging.info(self.__doc__)
        self.logging.info("\t")

        self._initialise()

        ## KEITHLEY settings
        self.keithley2410_address =  8      # in the SSD lab gpib address of the power supply that does the IV scan
        self.keithley2410_ramp_address =  25  # in the SSD lab gpib address of the power supply that does the IV scan

        self.keithley2410_gcddiode_address = 8
        self.switch_address       = 7       # gpib address of the switch

        ## LCR meter settings
        self.lcr_meter_address = 17         # in the SSD lab this is 9
        self.cv_res = 1e6                   # cv parallel resistor in [Ohm]
        
        self.lcr_vol = 0.5 #0.501             # ac voltage amplitude in [mV]
        self.lcr_freq = [1e4, 1e5, 1e6]     # ac voltage frequency in [Hz]


        self.lim_cur_ke2410 = 1E-4          # compliance in [A]
        self.lim_cur_ke6487 = 5E-7          # compliance in [A] for the GCD, this should be ?
        self.lim_vol = 10                   # compliance in [V]

        
        self.Vmin_iv = -1
        self.Vmax_iv = 1
        self.Vstep_iv = .2
        self.volt_list_iv = np.arange(self.Vmin_iv, self.Vmax_iv + self.Vstep_iv, self.Vstep_iv)
        #self.volt_list_iv = np.append(self.volt_list_iv,np.arange(self.Vmax_iv -self.Vstep_iv, self.Vmin_iv - self.Vstep_iv, -self.Vstep_iv))

        
        self.Vmin_bias_CV = -100
        self.Vmax_bias_CV = -900
        self.Vstep_bias_CV = -50
        self.volt_list_bias_CV = np.arange(self.Vmin_bias_CV, self.Vmax_bias_CV + self.Vstep_bias_CV, self.Vstep_bias_CV)

        
        self.Vmin_bias_IV = -200
        self.Vmax_bias_IV = -900
        self.Vstep_bias_IV = -100
        self.volt_list_bias_IV = np.arange(self.Vmin_bias_IV, self.Vmax_bias_IV + self.Vstep_bias_IV, self.Vstep_bias_IV) if not '_0kGy'in self.id else np.array([-350])
        
        #self.volt_list_bias_IV = [-350]


        self.nSampling_CV =  10
        self.nSampling_IV = 30 # TODO change to original 30s

        self.delay_vol_cv = 10     # delay between setting voltage and executing measurement in [s]
        self.delay_vol_iv = 30      # delay between setting voltage and executing measurement in [s]

        self.delay_initial_iv = 30  # TODO change to original 30s
        #self.delay_step_iv = 60
        #self.discharge_voltage = 10

        ## initialize the devices

        self.keithley2410 = ke2410(self.keithley2410_address)
        self.keithley2410_ramp = ke2410(self.keithley2410_ramp_address)


        self.switch = ke7001(self.switch_address)
        self.reset_switch()

        ## Set up lcr meter
        self.lcr_meter = hp4980(self.lcr_meter_address)
        self.lcr_meter.reset()
        self.lcr_meter.set_voltage(self.lcr_vol)
        self.lcr_meter.set_mode('RX')

        ## Set up volt meter
        self.keithley6487_address = 15
        self.keithley6487 = ke6487(self.keithley6487_address)


    def CRVpoint(self, biasV, freq, channel):  ## don't really know how best to do this ... to be teasted on the setup

        self.switch.close_channel(channel)
        self.keithley2410.set_output_on()
        self.keithley2410.ramp_up(biasV)
        self.keithley2410_ramp.set_output_on()
        self.keithley2410_ramp.ramp_up(0)
        time.sleep(self.delay_vol_cv)

        cur_tot = self.keithley2410.read_current()
        vol = self.keithley2410.read_voltage()

        print("New frequency:", freq)
        self.lcr_meter.set_frequency(freq)
        time.sleep(1)

        measurements = np.array([self.lcr_meter.execute_measurement() for _ in range(self.nSampling_CV)])
        means = np.mean(measurements, axis=0)
        errs = np.std(measurements, axis=0)/math.sqrt(self.nSampling_CV)

        r, x = means
        dr, dx = errs

        z = np.sqrt(r**2 + x**2)
        phi = np.arctan(x/r)
        r_s, c_s, l_s, D = lcr_series_equ(freq, z, phi)
        r_p, c_p, l_p, D = lcr_parallel_equ(freq, z, phi)

        line = [biasV, vol, freq, r_p, dr, x, dx, c_s, c_p, cur_tot]
        
        self.logging.info("{:<5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <5.2E}\t{: <8.3E}\t{: <8.3E}\t{: <5.2E}".format(*line))

        return (line)
        '''