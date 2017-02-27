# ============================================================================
# File: ke3706.py
# -----------------------
# Communication for Keithley 3706 switching unit.
# 
# Date: 06.06.2016
# Author: Florian Pitters
#
# ============================================================================

from pyvisa_device import device, device_error


class ke3706(device):
    """
    Keithley 3706 switching unit.
    
    Example:
    -------------
    dev = ke3706(address=24)
    dev.print_idn()
    dev.reset()
    """

    def __init__(self, address):
        device.__init__(self, address=address)
        self.ctrl.write("reset()")
    
    def print_idn(self):
        self.logging("Query ID.")
        #self.logging(self.ctrl.query("*IDN?"))
        return 0
    
    def get_idn(self):
        #return self.ctrl.query("*IDN?")
    
    def reset(self):
        self.logging("Reseting device.")
        self.ctrl.write("reset()")
        return 0



    # Switch functions
    # ---------------------------------

    def close_channel(self, nch):
        self.logging("Closing channel %d." % nch)
        self.ctrl.write("dmm.close('%d')", nch)
        return 0
    
        # channel.open()
        # channel.getstate()
        # channel.clearforbidden() (on page 13- 36)
        # channel.close() (on page 13-37)
        # channel.getbackplane() (on page 13-45) channel.getclose() (on page 13-46) channel.getcount() (on page 13-48) channel.getdelay() (on page 13-49) channel.getforbidden() (on page 13-50) channel.getimage() (on page 13-51) channel.getlabel() (on page 13-52) channel.getpole() (on page 13-55) channel.getstate() (on page 13-56) channel.open() (on page 13-59) channel.pattern.catalog() (on page 13- 61)
        # channel.pattern.delete() (on page 13- 62)
        # channel.pattern.getimage() (on page 13- 62)
        # channel.pattern.setimage() (on page 13- 63)
        # channel.pattern.snapshot() (on page 13- 66)
        # channel.reset() (on page 13-68) channel.setbackplane() (on page 13-70) channel.setdelay() (on page 13-72) channel.setforbidden() (on page 13-73) channel.setlabel() (on page 13-74) channel.setpole() (on page 13-79)


    # DMM functions
    # ---------------------------------

    def set_sense(self, prop):
        if prop == 'dcvolts':
            self.logging("Setting sense to voltage.")
            self.ctrl.write("dmm.func = 'dcvolts' ")
        elif prop == 'current':
            self.logging("Setting sense to current.")
            #self.ctrl.write(":SENS:FUNC 'CURR' ")
        elif prop == 'resistance':
            self.logging("Setting sense to resistance.")
            #self.ctrl.write(":SENS:FUNC 'RES' ")
        elif prop == 'temperature'
            self.ctrl.write("dmm.func = 'temperature'")
        else:
            self.logging("Choosen property cannot be measured by this device.")
            # rise some error
            return -1

    def set_speed(self, val):
        self.ctrl.write("dmm.nplc = %f" % val)
        return 0

    def read_sense(self):
        self.logging("Reading sense.")
        val = self.ctrl.write("dmm.measure() ")
        return float(val)

    # Set the NPLC for DC volts
    # 
    # Set the range for DC volts
    # dmm.range = 10
    # Take the DC volts measurement

    # dmm.adjustment.count (on page 13-109) dmm.adjustment.date (on page 13-109) dmm.aperture (on page 13-110) dmm.appendbuffer() (on page 13-111) dmm.autodelay (on page 13-112) dmm.autorange (on page 13-113) dmm.autozero (on page 13-114) dmm.buffer.catalog() (on page 13-115) dmm.buffer.info() (on page 13-116) dmm.buffer.maxcapacity (on page 13-117) dmm.buffer.usedcapacity (on page 13- 118)
    # dmm.calibration.ac() (on page 13-118) dmm.calibration.dc() (on page 13-120) dmm.calibration.lock() (on page 13-121) dmm.calibration.password (on page 13- 122)
    # dmm.calibration.save() (on page 13-122) dmm.calibration.unlock() (on page 13- 122)
    # dmm.calibration.verifydate (on page 13- 123)
    # dmm.close() (on page 13-123) dmm.configure.catalog() (on page 13- 125)
    # dmm.configure.delete() (on page 13-125) dmm.configure.query() (on page 13-126) dmm.configure.recall() (on page 13-128) dmm.configure.set() (on page 13-129) dmm.connect (on page 13-130) dmm.dbreference (on page 13-131) dmm.detectorbandwidth (on page 13-132) dmm.displaydigits (on page 13-132) dmm.drycircuit (on page 13-133) dmm.filter.count (on page 13-134) dmm.filter.enable (on page 13-134) dmm.filter.type (on page 13-135) dmm.filter.window (on page 13-136) dmm.fourrtd (on page 13-137)
    # dmm.func (on page 13-137) dmm.getconfig() (on page 13-139) dmm.inputdivider (on page 13-140) dmm.limit[Y].autoclear (on page 13-141) dmm.limit[Y].clear() (on page 13-141) dmm.limit[Y].enable (on page 13-142) dmm.limit[Y].high.fail (on page 13-142) dmm.limit[Y].high.value (on page 13- 143)
    # dmm.limit[Y].low.fail (on page 13-143) dmm.limit[Y].low.value (on page 13-144) dmm.linesync (on page 13-144) dmm.makebuffer() (on page 7-8) dmm.math.enable (on page 13-147) dmm.math.format (on page 13-147) dmm.math.mxb.bfactor (on page 13-148) dmm.math.mxb.mfactor (on page 13-149) dmm.math.mxb.units (on page 13-149) dmm.math.percent (on page 13-150) dmm.measure() (on page 13-150) dmm.measurecount (on page 13-151) dmm.measurewithtime() (on page 13-151) dmm.nplc (on page 13-152) dmm.offsetcompensation (on page 13-153) dmm.open() (on page 13-154) dmm.opendetector (on page 13-155) dmm.range (on page 13-156) dmm.refjunction (on page 13-157) dmm.rel.acquire() (on page 13-158) dmm.rel.enable (on page 13-159) dmm.rel.level (on page 13-160) dmm.reset() (on page 13-161) dmm.rtdalpha (on page 13-162) dmm.rtdbeta (on page 13-163) dmm.rtddelta (on page 13-164) dmm.rtdzero (on page 13-165) dmm.savebuffer() (on page 7-10) dmm.setconfig() (on page 13-168) dmm.simreftemperature (on page 13-169) dmm.thermistor (on page 13-170) dmm.thermocouple (on page 13-171) dmm.threertd (on page 13-172) dmm.threshold (on page 13-173) dmm.transducer (on page 13-173) dmm.units (on page 13-174)

    # exit() (on page 13-180)
    # setup.cards() (on page 13-252)

    # slot[X].commonsideohms (on page 13-255) slot[X].digio (on page 13-255) slot[X].endchannel.amps (on page 13- 255)
    # slot[X].endchannel.isolated (on page 13-256)
    # slot[X].endchannel.voltage (on page 13- 257)
    # slot[X].idn (on page 13-257) slot[X].interlock.override (on page 13- 257)
    # slot[X].interlock.state (on page 13- 258)
    # slot[X].isolated (on page 13-259) slot[X].matrix (on page 13-259) slot[X].maxvoltage (on page 13-259) slot[X].multiplexer (on page 13-259) slot[X].poles.four (on page 13-260) slot[X].poles.one (on page 13-260) slot[X].poles.two (on page 13-260) slot[X].pseudocard (on page 13-260) slot[X].startchannel.amps (on page 13- 261)
    # slot[X].startchannel.isolated (on page 13-262)
    # slot[X].startchannel.voltage (on page 13-263)
    # slot[X].tempsensor (on page 13-263) slot[X].thermal.state (on page 13-263)



