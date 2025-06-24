# Documentation for this Instrument:  https://download.tek.com/manual/6487-901-01(B-Mar2011)(Ref).pdf
import sys
import os
import time
from devices.pyvisa_device import device


## These imports originated from the EPool project, but are not available in this context.
# from EPool_Instruments.Visa.visadevice import visadevice
# from Epool_Tools.NPTconfig import logit




class agilent_4263b(device):

    ## Old __init__ method, commented out for reference.
    # def __init__(self, ressource, *args, **kwargs):
    #     super().__init__(ressource, *args, **kwargs)

    def __init__(self, address):
        """ Constructor for the Agilent 4263B LCR meter.
        """
        device.__init__(self, address=address)
        self.ctrl.write("*RST") 
        


    def selfCalibration(self, **instructions):
        """ open/short correction
        """
        VALID_CORRECTION = {'OPEN': '1', 'SHORT': '2'}
        self.logging.info(1, "You are in agilent_4263b.selfCalibration")
        self.logging.info(3, "instructions = " + str(instructions))
        lcr_correction_type = VALID_CORRECTION[instructions['lcr_correction_type']]
        self.ctrl.write("SENS:CORR:COLL STAN" + str(lcr_correction_type))


    def getMeasurement(self, **instructions):
        """ Get the measurement set
        """
        self.logging.info(1, "Yor are in agilent_4263b.getMeasurement")
        self.logging.info(3, "instructions = " + str(instructions))
        self.ctrl.write(":INIT:CONT OFF")
        self.ctrl.write("INIT")
        time.sleep(2)
        data = str(self.ctrl.query("FETCH?").split(',')[1][0:])
        return float(data)


    def setAmplitude(self, **instructions):
        """ setAmplitude en mV """
        self.logging.info(1, "Yor are in agilent_4263b.setAmplitude")
        self.logging.info(3, "instructions = " + str(instructions))
        lcr_source_level = instructions['lcr_source_level']
        self.ctrl.write(f'SOUR:VOLT:AMPL {lcr_source_level}')


    def setBias(self, **instructions):
        """ setAmplitude en mV """
        self.logging.info(1, "Yor are in agilent_4263b.setBias")
        self.logging.info(3, "instructions = " + str(instructions))
        lcr_source_bias = instructions['lcr_source_bias']
        self.ctrl.write(f'SOUR:VOLT:OFFS {lcr_source_bias}')


    def setFrequency(self, **instructions):
        """ Frequency Hz 100, 120, 1k, 10k, 100k"""
        self.logging.info(1, "You are in Lcr_agilent_4263b.setFrequency")
        self.logging.info(3, "instructions = " + str(instructions))
        lcr_source_frequency = instructions['lcr_source_frequency']
        self.ctrl.write(f':SOUR:FREQ {lcr_source_frequency}')


    def setMeasurementTime(self, **instructions):
        """ set measurement time mode
        Short, Medium, Long
        """
        VALID_MODES = {'Short': '0.025',
                       'Medium': '0.065',
                       'Long': '0.5'}
        self.logging.info(1, "You are in agilent_4263b.setMeasurementTime")
        self.logging.info(3, "instructions = " + str(instructions))
        lcr_measurement_time = VALID_MODES[instructions['lcr_measurement_time']]
        self.ctrl.write("SENS:FIMP:APER " + lcr_measurement_time)


    def setMeasurement(self, **instructions):
        """ setMeasurement"""
        self.logging.info(1, "Yor are in agilent_4263b.setMeasurement")
        self.logging.info(3, "instructions = " + str(instructions))
        lcr_measurement = instructions['lcr_measurement']

        VALID_prefix = {'Cp-D': 'FADM',
                        'R-X': 'FIMP',
                        'Cp-Q': 'FADM',
                        'Ls-Q': 'FIMP'}
        VALID_form = {'D': 'D',
                      'Cp': 'CP',
                      'Cs': 'CS',
                      'Ls': 'LS',
                      'Rs': 'REAL',
                      'G': 'REAL',
                      'R': 'REAL',
                      'X': 'IMAG',
                      'Q': 'Q'}
        pivot = lcr_measurement.find("-")
        calc1 = lcr_measurement[:pivot]
        calc2 = lcr_measurement[pivot+1:]

        self.ctrl.write(f":SENS:FUNC '" + VALID_prefix[lcr_measurement] + "'")
        self.ctrl.write(f':CALC1:FORM {VALID_form[calc1]}')
        self.ctrl.write(f':CALC2:FORM {VALID_form[calc2]}')


    def setOnOff(self, status, **instructions):
        """ Enable DC BIAS
        """
        self.logging.info(1, "Yor are in agilent_4263b")
        self.logging.info(3, "instructions = " + str(instructions) + ", status = " + str(status))
        if status == 'ON':
            self.ctrl.write("SOUR:VOLT:OFFS:STAT " + status)
        else:
            self.ctrl.write("SOUR:VOLT:OFFS:STAT OFF")