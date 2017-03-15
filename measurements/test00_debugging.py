# ============================================================================
# File: test00_debugging.py
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


import sys
import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import ke2450 # volt meter
from devices import hp4980 # lcr meter
from devices import switchcard # switch


class test00_debugging(measurement):
    """A test on communication and functionality."""

    def initialise(self):
        #self.logging.info("\t")
        self.logging.info("\t")
        self.logging.info("------------------------------------------")
        self.logging.info("Debugging")
        self.logging.info("------------------------------------------")
        self.logging.info("A test on communication and functionality.")
        self.logging.info("\t")
        
        self._initialise()
        self.pow_supply_address = 24
        self.volt_meter_address = 16
        self.lcr_meter_address = 17
        self.switch_address = 'COM3'
        
        self.lim_cur = 0.0001
        self.lim_vol = 100
        self.cell_list = range(1, 10, 1)
        self.volt_list = [1, 5, 10]

        self.delay_vol = 10
        self.delay_ch = 0.4

        self.test_vol = 0.5
        self.test_freq = 1E4

        self.mode = 3

        if self.mode == 0:
            self.logging.info("Note: A general test on software functionality.")
            self.logging.info("\t")

        elif self.mode == 1:
            self.logging.info("Note: A test of communication.")
            self.logging.info("\t")        
            self.logging.info("Settings:")
            self.logging.info("Power supply voltage limit:      %.2fV" % self.lim_vol)
            self.logging.info("Power supply current limit:      %.6fA" % self.lim_cur)
            self.logging.info("Volt meter voltage limit:        %.2fV" % self.lim_vol)
            self.logging.info("Volt meter current limit:        %.6fA" % self.lim_cur)
            self.logging.info("LCR meter test voltage:          %.2fV" % self.test_vol)
            self.logging.info("LCR meter test frequency:        %.0fHz" % self.test_freq)
            self.logging.info("Voltage Delay:                   %.2fs" % self.delay_vol)
            self.logging.info("Channel Delay:                   %.2fs" % self.delay_ch)
            self.logging.info("\t")

        elif self.mode == 2:
            self.logging.info("Note: A test to ramp voltage.")
            self.logging.info("\t")
            self.logging.info("Settings:")
            self.logging.info("Power supply voltage limit:      %.2fV" % self.lim_vol)
            self.logging.info("Power supply current limit:      %.6fA" % self.lim_cur)
            self.logging.info("Volt meter voltage limit:        %.2fV" % self.lim_vol)
            self.logging.info("Volt meter current limit:        %.6fA" % self.lim_cur)
            self.logging.info("LCR meter test voltage:          %.2fV" % self.test_vol)
            self.logging.info("LCR meter test frequency:        %.0fHz" % self.test_freq)
            self.logging.info("Voltage Delay:                   %.2fs" % self.delay_vol)
            self.logging.info("Channel Delay:                   %.2fs" % self.delay_ch)
            self.logging.info("\t")

        elif self.mode == 3:
            self.logging.info("Note: A test for the switch card.")
            self.logging.info("\t")

        else:
            self.logging.info("Nothing happening in this mode.") 
        
        

    def execute(self):

        ## Test functionality
        if self.mode == 0:
            out = []

            self.logging.info("\t")           
            self.logging.info("X[-]\tY[-]")
            self.logging.info("-----------------")
            self.logging.info("\t")

            ## Create fake data
            try:
                for i in range(1, 10):
                    out.append([i, i**2])
                    time.sleep(0.3)
                    self.logging.info("\t%d \t%d" % (i, i**2))
  
            except KeyboardInterrupt:
                self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

            ## Save and print
            self.logging.info("\t")
            self.logging.info("\t")
            self.save_list(out, "out.dat", fmt="%4d", header=' x [-]\ty [-]')
            #self.print_graph(np.array(out)[:, 0], np.array(out)[:, 1], 0.5, 'x', 'y', fn="out.png")
        

        ## Test communication
        elif self.mode == 1: 

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
            volt_meter.set_source('voltage')
            volt_meter.set_sense('current')
            volt_meter.set_current_range(1E-4)
            volt_meter.set_voltage(0)
            volt_meter.set_output_on()
    
            ## Set up lcr meter
            lcr_meter = hp4980(self.lcr_meter_address)
            lcr_meter.reset()
            lcr_meter.set_voltage(self.test_vol)
            lcr_meter.set_frequency(self.test_freq)
            lcr_meter.set_mode('CPRP')
    
            for v in self.volt_list:
                pow_supply.ramp_voltage(v)
                time.sleep(1)
    
                vol = pow_supply.read_voltage()
                cur = pow_supply.read_current()
                cap, res = lcr_meter.execute_measurement()
                cur_tot = pow_supply.read_current() 
    
                self.logging.info("vol %E, cur %E, cap %E, cur_tot %E" % (vol, cur, cap, cur_tot))
    
    
            ## Close connections
            pow_supply.set_output_off()
            pow_supply.reset()
            volt_meter.set_output_off()
            volt_meter.reset()


        ## Test ramping of voltage
        elif self.mode == 2: 

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
            volt_meter = ke2001(self.volt_meter_address)
            volt_meter.reset()
            volt_meter.setup_ammeter(nplc=10, dig=9)

            try:
                for v in [-5, -1, 0, 1, 5, 10, 25, 50]:
                    pow_supply.ramp_voltage(v, debug=1)
                    time.sleep(1)
        
                    vol = pow_supply.read_voltage()
                    cur = volt_meter.read_current()
                    cur_tot = pow_supply.read_current()
        
                    self.logging.info("vol %E, cur_tot %E" % (vol, cur_tot))
  
            except KeyboardInterrupt:
                pow_supply.ramp_voltage(0)
                self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")
    
            ## Close connections
            pow_supply.ramp_voltage(0, debug=1)
            pow_supply.set_output_off()
            pow_supply.reset()


        ## Test switchcard
        if self.mode == 3:

            ## Set up switch
            switch = switchcard(self.switch_address)
            switch.reboot()
            switch.set_display_mode('ON')

            self.logging.info("\t")           
            self.logging.info("Channel Set [-]\tChannel Read [-]")
            self.logging.info("-----------------")
            self.logging.info("\t")

            try:
                init = time.time()
                for i in self.cell_list:
                    switch.open_channel(i)
                    ch = switch.get_channel()
                    t = time.time() - init
                    if ch == i:
                        self.logging.info("\t%.3f \t%d \t%d" % (t, i, ch))
                    else:
                        self.logging.warning("\t%.3f \t%d \t%d" % (t, i, ch))
  
            except KeyboardInterrupt:
                self.logging.error("Keyboard interrupt. Ramping down voltage and shutting down.")

            ## Save and print
            self.logging.info("\t")
            self.logging.info("\t")
        

        else: 
            pass
    
    
    def finalise(self):
        self._finalise()

