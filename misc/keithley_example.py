#!/usr/bin/python

import visa

def ReadID(dev):
    cmd = '*IDN?'
    print dev.query(cmd)
    

def SetCurrentLimit(dev, limit):
	dev.write(':SENS:CURR:PROT %f' % limit)
    
def SetVoltageLimit(dev, limit):
    dev.write(":SENS:VOLT:PROT %f" % limit)
        
def InitVoltage(dev):
    dev.write(":SENS:FUNC 'VOLT' ")        # Select to measure voltage
    #dev.write(":SENS:VOLT:NPLC 1")         # Set measurement speed to 1 PLC.

def InitCurrent(dev):
    dev.write(":SENS:FUNC 'CURR' ")        # Select to measure voltage
    #dev.write(":SENS:CURR:NPLC 1")         # Set measurement speed to 1 PLC.
    
def AutoOutput(dev, cntr=0):
    if cntr == 1: 
        dev.write(":SOUR:CLE:AUTO ON")
    else:
        dev.write(":SOUR:CLE:AUTO OFF")
    
def SetVoltage(dev, val):
    dev.write(':SOUR:FUNC VOLT')
    dev.write(':SOUR:VOLT %f' % val)

def SetCurrent(dev, val):
    dev.write(':SOUR:FUNC CURR')
    dev.write(':SOUR:CURR %f' % val)
    
def ReadCurrent(dev):
    cmd = ':MEAS:CURR?'
    print cmd
    print dev.query(cmd)
    
def ReadVoltage(dev):
    cmd = ':MEAS:VOLT?'
    print cmd
    print dev.query(cmd)

def CheckCompliance(dev):
    cmd = ':SENS:CURR:PROT:TRIP?'
    print cmd
    print dev.query(cmd)
    
# SetSource
# SetSense



def main():
    rm = visa.ResourceManager()
    rm.list_resources()
    
    keithley = rm.open_resource('GPIB0::24::INSTR')
    
    ReadID(keithley)
    AutoOutput(keithley, 1)
    SetCurrentLimit(keithley, 0.0005)
    SetVoltage(keithley, 10)
    InitCurrent(keithley)
    ReadCurrent(keithley)


    
    
    

if __name__ == "__main__":
    main()
    print "Success!"