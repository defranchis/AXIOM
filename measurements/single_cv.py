import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import hp4284A # lcr meter


class single_cv(measurement):
    """Measurement of C-V curve for a single cell on the wafer."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("Single CV Measurement")
        self.logging.info("------------------------------------------")
        self.logging.info("Measurement of CV for a single cell.")
        self.logging.info("\n")
        
        self._initialise()
        self.pow_supply_address = 24
        self.lcr_meter_address = 16
        
        self.lim_cur = 0.0001
        self.lim_vol = 300
        self.volt_list = [20, 50, 100, 200]

        self.lcr_vol = 500 # ac voltage amplitude in mV
        self.lcr_freq = 10 # ac voltage frequency in kHz
        self.cor_open = np.loadtxt('valuesOpen.txt') # open correction for lcr meter
        self.cor_short = np.loadtxt('valuesShort.txt') # short correction for lcr meter
        self.cor_load = np.loadtxt('valuesLoad.txt')
        
        self.logging.info("\n")
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %.2fV" % self.lim_vol)
        self.logging.info("Power Supply current limit:      %.6fA" % self.lim_cur)
        self.logging.info("LCR measurement voltage:         %.2fV" % self.lcr_vol)
        self.logging.info("LCR measurement frequency:       %.6fA" % self.lcr_freq)
        self.logging.info("\n")
        
        

    def execute(self):
        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_voltage_limit(self.lim_vol)
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_output_on()

        ## Set up lcr meter
        lcr_meter = hp4284A(self.pow_supply_address)
        lcr_meter.set_mode('CPRP')
        lcr_meter.set_voltage(self.lcr_vol)
        lcr_meter.set_frequency(self.lcr_freq)
        #lcr_meter.set_output_on()


        for v in self.volt_list:
            pow_supply.set_voltage(v)
            vol = pow_supply.read_voltage()
            cap = lcr_meter.read_capacitance()

            time.sleep(0.5)
            self.logging.info("vol %d, cap %d" % (vol, cap))


        ## Close connections
        pow_supply.set_output_off()
        pow_supply.reset()
    
    
    def finalise(self):
        self._finalise()