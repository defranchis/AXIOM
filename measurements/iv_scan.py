import logging
from measurement import measurement
from devices import ke2410


class iv_scan(measurement):
    """ IV scan """
    
    def initialise(self):
        self.logging.info("------------------------------------------")
        self.logging.info("Some header for this test")
        self.logging.info("------------------------------------------")
        
        self._initialise()
        self.address = 24
        
        self.lim_cur = 0.0001
        self.lim_vol = 100
        self.cell_list = [0, 1]
        self.volt_list = [10, 20]
        
        self.logging.info("------------------------------------------")
        self.logging.info("Voltage limit set to %.2fV" % self.lim_vol)
        self.logging.info("Current limit set to %.6fA" % self.lim_cur)
        self.logging.info("------------------------------------------")
        
        
    def execute(self):
        
        ## Set up source meter
        src_meter = ke2410(self.address)
        src_meter.print_idn()
        src_meter.set_source('voltage')
        src_meter.set_sense('current')
        src_meter.set_current_limit(self.lim_cur)
        src_meter.set_output_on()

        ## Set up switch
        switch = something()

        for c in self.cell_list:
            switch.set_channel(c)
            
            for v in self.volt_list:
                src_meter.set_voltage(v)
                vol = src_meter.read_voltage()
                cur = src_meter.read_current()
                self.logging.info("%d   %d" % (vol, cur))

        ## Close connections
        src_meter.set_output_off()
        src_meter.reset()
    
    
    def finalise(self):
        self._finalise()