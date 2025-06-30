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
        
## ----------- TO BE IMPLEMENTED: -----------    

    # # Configuration functions
    # # ---------------------------------

    # RST can remain the same since it uses the IEEE 488.2 standard, like the keithley devices
    def reset(self, debug=0):  #USED
        if debug == 1:
            self.logging("Reseting device.")
        self.ctrl.write("*RST")
        return 0        
    
    def set_voltage(self, val, debug=0):
        """ Sets the test signal level : page 184 of the 4263B manual
        """
        if debug == 1:
            self.logging("Setting voltage to %f V." % val)
        self.ctrl.write(f'SOUR:VOLT {val}')
        return 0

    def set_frequency(self, val, debug=0):
        """ Set the frequency for AC source
        """
        if debug == 1:
            self.logging("Setting frequency to %s Hz." % val)
        self.ctrl.write(f':SOUR:FREQ {val}')
        return 0

    def set_mode(self, mode='CSRS', debug=0, **instructions):
        """
        Set the measurement mode for the Agilent 4263B.
        Compatible with legacy set_mode usage: lcr_meter.set_mode('RX')
        """
        if debug == 1:
            self.logging("Setting measurement mode to %s. Options are ['RX', 'CSRS', 'CPRP', 'ZTD']." % mode)

        # this maps the (previously used) commands from the keysight E4980 to the agilent 4263b formatting
        # refer to E4980 manual page 353: https://www.keysight.com/us/en/assets/9018-05655/user-manuals/9018-05655.pdf
        # and the 4263b  manual page 167: https://www.keysight.com/us/en/assets/9018-01378/user-manuals/9018-01378.pdf
        MODE_MAP = {
            'RX': 'R-X',
            'CSRS': 'Cs-Rs',
            'CPRP': 'Cp-Rp',
            'ZTD': 'Z-thd'
        }
        if mode in MODE_MAP:
            lcr_measurement = MODE_MAP[mode]
        else:
            lcr_measurement = mode

        # Set the correct measurement mode and formatting for the Agilent 4263B
        VALID_prefix = {'Cp-D': 'FADM',
                        'R-X': 'FIMP',
                        'Cs-Rs': 'FIMP',
                        'Cp-Rp': 'FADM',
                        'Z-thd': 'FIMP',
                        'Cp-Q': 'FADM',
                        'Ls-Q': 'FIMP'}
        VALID_form = {'D': 'D',
                        'Cp': 'CP',
                        'Cs': 'CS',
                        'Ls': 'LS',
                        'Rs': 'REAL',
                        'Rp': 'RP',
                        'G': 'REAL',
                        'R': 'REAL',
                        'X': 'IMAG',
                        'Q': 'Q',
                        'Z': 'MLIN',
                        'thd' : 'PHAS'
                        }
        
        # Split the measurement info two parts for the relevant commands
        pivot = lcr_measurement.find("-")
        calc1 = lcr_measurement[:pivot]
        calc2 = lcr_measurement[pivot+1:]

        # example command formatting on page 133 of the 4263B manual
        self.ctrl.write(f":SENS:FUNC '" + VALID_prefix[lcr_measurement] + "'")
        self.ctrl.write(f':CALC1:FORM {VALID_form[calc1]}')
        self.ctrl.write(f':CALC2:FORM {VALID_form[calc2]}')

        return 0
    
    def check_voltage(self, debug=0):
        """ Queries the test signal level : page 184 of the 4263B manual
        """
        if debug == 1:
            self.logging("Checking voltage setting.")
        voltage = float(self.ctrl.query("SOUR:VOLT?"))
        if debug == 1:
            self.logging("Current voltage setting is %f V." % voltage)
        return voltage
    
    def check_frequency(self, debug=0):
        """ Queries the frequency for normal measurement.
        """
        if debug == 1:
            self.logging("Checking frequency setting.")
        frequency = float(self.ctrl.query("SOUR:FREQ?"))
        if debug == 1:
            self.logging("Current frequency setting is %f Hz." % frequency)
        return frequency

    #TODO: ensure the logging error is not printed for status 0
    def execute_measurement(self, debug=0):
        """ Fetches the measurement data from the device.
            Format of query response is, <status>,<data1> ,<data2>,<val1>,<val2>
        """
        if debug == 1:
            self.logging("Fetching measurement data.")
        self.ctrl.write(":INIT:CONT OFF")
        self.ctrl.write("INIT")
        time.sleep(0.5)
        vals = self.ctrl.query("FETC?").split(',')
        print("Measurement data fetched: " + str(vals))
        return float(vals[1]), float(vals[2])



# ---------------------------- OLD FUNCTIONS FROM PREVIOUS IMPLEMENTATION ----------------------------
# ----------------------------------------------------------------------------------------------------



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
        data = self.ctrl.query("FETCH?").split(',')
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


    #TODO: this function was used by other setup, unkown if the hp4980 did this automatically, or if not used in test setup.
    def setOnOff(self, status, **instructions):
        """ Enable DC BIAS
        """
        self.logging.info(1, "Yor are in agilent_4263b")
        self.logging.info(3, "instructions = " + str(instructions) + ", status = " + str(status))
        if status == 'ON':
            self.ctrl.write("SOUR:VOLT:OFFS:STAT " + status)
        else:
            self.ctrl.write("SOUR:VOLT:OFFS:STAT OFF")