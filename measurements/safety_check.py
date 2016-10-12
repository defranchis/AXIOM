import time
import logging
import numpy as np
from measurement import measurement
from devices import ke2410 # power supply
from devices import ke3706 # switch
from devices import ke2000 # volt meter


class safety_check(measurement):
    """Performs a scan at 10V to check for high currents after alignment."""
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("Safety Check")
        self.logging.info("------------------------------------------")
        self.logging.info("Performs a scan at 10V to check for high currents after alignment.")
        self.logging.info("\n")
        
        self._initialise()
        self.pow_supply_address = 24
        self.volt_meter_address = 16
        self.switch_address = 18
        
        self.lim_cur = 0.0001
        self.lim_vol = 100
        self.delay_vol = 10
        self.delay_ch = 0.4
        self.cell_list = [0, 1, 2]
        self.volt_list = [10]
        
        self.logging.info("\n")
        self.logging.info("Settings:")
        self.logging.info("Power Supply voltage limit:      %.2fV" % self.lim_vol)
        self.logging.info("Power Supply current limit:      %.6fA" % self.lim_cur)
        self.logging.info("Volt Meter voltage limit:        %.2fV" % self.lim_vol)
        self.logging.info("Volt Meter current limit:        %.6fA" % self.lim_cur)
        self.logging.info("\n")
        
        

    def execute(self):
        
        ## Set up power supply
        pow_supply = ke2410(self.pow_supply_address)
        pow_supply.set_source('voltage')
        pow_supply.set_sense('current')
        pow_supply.set_voltage_limit(self.lim_vol)
        pow_supply.set_current_limit(self.lim_cur)
        pow_supply.set_output_on()

        ## Set up volt meter
        # Set up volt meter

        ## Set up switch
        # Set up switch

        for v in self.volt_list:
            pow_supply.set_voltage(v)
            time.sleep(delay_vol)

            cur_tot = pow_supply.read_current() 
            
            total_current_notice = 1.0 * 10**(-7)
            total_current_warning = 5.0 * 10**(-7)

            if cur_tot < total_current_notice:
                self.logging.info("Total current: %e" % cur_tot)
                elif cur > single_channel_notice and cur < single_channel_warning:
                    self.logging.warning(("Total current: %e" % cur_tot)
                else
                    self.logging.critical("Total current: %e" % cur_tot)


            for c in self.cell_list:
                # Check all channels close
                # Open channel c

                time.sleep(delay_ch)
                
                ## Current is measured by voltage over 22M resistor
                cur = volt_meter.read_voltage()
                cur = cur / resistor(c)

                single_channel_notice = 1.0 * 10**(-9)
                single_channel_warning = 5.0 * 10**(-9)
                if cur < single_channel_notice:
                    self.logging.info("cell nr.:%d, vol %d, cur %e" % (c, v, cur))
                elif cur > single_channel_notice and cur < single_channel_warning:
                    self.logging.warning("cell nr.:%d, vol %d, cur %e" % (c, v, cur))
                else
                    self.logging.critical("cell nr.:%d, vol %d, cur %e" % (c, v, cur))

                # Close all channels
                time.sleep(0.01)
                

        ## Close connections
        pow_supply.set_output_off()
        pow_supply.reset()
    
    
    def finalise(self):
        self._finalise()